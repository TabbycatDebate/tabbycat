from django.test import TestCase

from draw.models import Debate, DebateTeam
from draw.types import DebateSide
from motions.models import DebateTeamMotionPreference, Motion, RoundMotion
from motions.statistics import MotionBPStatsCalculator, MotionTwoTeamStatsCalculator
from participants.models import Team
from results.models import BallotSubmission, TeamScore
from tournaments.models import Round, Tournament


class TestMotionStatisticsTwoTeam(TestCase):
    """Very basic test for motion statistics for two-team formats, involving
    just one debate and two motions."""

    def setUp(self):
        self.tournament = Tournament.objects.create(slug="motions-twoteam", name="Motion statistics two-team")
        self.tournament.preferences['debate_rules__teams_in_debate'] = 2
        self.tournament.preferences['debate_rules__ballots_per_debate_prelim'] = 'per-adj'
        team1 = Team.objects.create(tournament=self.tournament, reference="1", use_institution_prefix=False)
        team2 = Team.objects.create(tournament=self.tournament, reference="2", use_institution_prefix=False)
        rd = Round.objects.create(tournament=self.tournament, seq=1)
        motion = Motion.objects.create(text="Motion", reference="Motion", tournament=self.tournament)
        debate = Debate.objects.create(round=rd)
        dt1 = DebateTeam.objects.create(debate=debate, team=team1, side=DebateSide.AFF)
        dt2 = DebateTeam.objects.create(debate=debate, team=team2, side=DebateSide.NEG)
        ballotsub = BallotSubmission.objects.create(debate=debate, motion=motion, confirmed=True)
        TeamScore.objects.create(debate_team=dt1, ballot_submission=ballotsub,
            margin=+2, points=1, score=101, win=True,  votes_given=1, votes_possible=1)
        TeamScore.objects.create(debate_team=dt2, ballot_submission=ballotsub,
            margin=-2, points=0, score=99, win=False, votes_given=0, votes_possible=1)

        vetoed = Motion.objects.create(text="No one wants", reference="Vetoed", tournament=self.tournament)
        DebateTeamMotionPreference.objects.create(debate_team=dt1, ballot_submission=ballotsub,
            motion=vetoed, preference=3)
        DebateTeamMotionPreference.objects.create(debate_team=dt2, ballot_submission=ballotsub,
            motion=vetoed, preference=3)

        RoundMotion.objects.create(round=rd, motion=motion, seq=1)
        RoundMotion.objects.create(round=rd, motion=vetoed, seq=2)

    def tearDown(self):
        DebateTeam.objects.filter(team__tournament=self.tournament).delete()
        self.tournament.delete()

    def test_statistics(self):
        stats = MotionTwoTeamStatsCalculator(self.tournament)
        for m in stats.motions:
            if m.reference == "Motion":
                self.assertEqual(m.s0_wins, 1)
                self.assertEqual(m.s1_wins, 0)
                self.assertEqual(m.s0_vetoes, 0)
                self.assertEqual(m.s1_vetoes, 0)
                self.assertEqual(m.s0_win_percentage, 100)
                self.assertEqual(m.s1_win_percentage, 0)
                self.assertEqual(m.s0_veto_percentage, 0)
                self.assertEqual(m.s1_veto_percentage, 0)
            if m.reference == "Vetoed":
                self.assertEqual(m.s0_wins, 0)
                self.assertEqual(m.s1_wins, 0)
                self.assertEqual(m.s0_vetoes, 1)
                self.assertEqual(m.s1_vetoes, 1)
                self.assertEqual(m.s0_veto_percentage, 50)
                self.assertEqual(m.s1_veto_percentage, 50)


class TestMotionStatisticsBP(TestCase):
    """Very basic test for motion statistics for two-team formats, involving
    just one debate and two motions."""

    def setUp(self):
        self.tournament = Tournament.objects.create(slug="motions-bp", name="Motion statistics BP")
        self.tournament.preferences['debate_rules__teams_in_debate'] = 4
        self.tournament.preferences['debate_rules__ballots_per_debate_prelim'] = 'per-debate'
        self.teams = {side: Team.objects.create(tournament=self.tournament, reference=side,
                use_institution_prefix=False) for side in self.tournament.sides}

    def tearDown(self):
        DebateTeam.objects.filter(team__tournament=self.tournament).delete()
        self.tournament.delete()

    def test_prelim_statistics(self):
        rd = Round.objects.create(tournament=self.tournament, seq=1, stage=Round.Stage.PRELIMINARY)
        motion = Motion.objects.create(text="Prelim motion", reference="Prelim", tournament=self.tournament)
        rd.roundmotion_set.create(motion=motion, seq=1)
        debate = Debate.objects.create(round=rd)
        ballotsub = BallotSubmission.objects.create(debate=debate, motion=motion, confirmed=True)

        for i, side in enumerate(self.tournament.sides):
            dt = DebateTeam.objects.create(debate=debate, team=self.teams[side], side=side)
            TeamScore.objects.create(debate_team=dt, ballot_submission=ballotsub,
                points=i, score=100+i)

        stats = MotionBPStatsCalculator(self.tournament)
        motion = next(stats.motions)
        assert motion.reference == "Prelim"

        self.assertEqual(motion.s0_average, 0)
        self.assertEqual(motion.s1_average, 1)
        self.assertEqual(motion.s2_average, 2)
        self.assertEqual(motion.s3_average, 3)

        self.assertEqual(motion.s0_0_count, 1)
        self.assertEqual(motion.s0_1_count, 0)
        self.assertEqual(motion.s0_2_count, 0)
        self.assertEqual(motion.s0_3_count, 0)
        self.assertEqual(motion.s1_0_count, 0)
        self.assertEqual(motion.s1_1_count, 1)
        self.assertEqual(motion.s1_2_count, 0)
        self.assertEqual(motion.s1_3_count, 0)
        self.assertEqual(motion.s2_0_count, 0)
        self.assertEqual(motion.s2_1_count, 0)
        self.assertEqual(motion.s2_2_count, 1)
        self.assertEqual(motion.s2_3_count, 0)
        self.assertEqual(motion.s3_0_count, 0)
        self.assertEqual(motion.s3_1_count, 0)
        self.assertEqual(motion.s3_2_count, 0)
        self.assertEqual(motion.s3_3_count, 1)

        self.assertAlmostEqual(motion.counts_by_half['top'], 0.5)
        self.assertAlmostEqual(motion.counts_by_half['bottom'], 2.5)
        self.assertAlmostEqual(motion.counts_by_bench['gov'], 1)
        self.assertAlmostEqual(motion.counts_by_bench['opp'], 2)

    def test_elim_statistics(self):
        rd = Round.objects.create(tournament=self.tournament, seq=1, stage=Round.Stage.ELIMINATION)
        motion = Motion.objects.create(text="Elim motion", reference="Elim", tournament=self.tournament)
        rd.roundmotion_set.create(motion=motion, seq=1)
        debate = Debate.objects.create(round=rd)
        ballotsub = BallotSubmission.objects.create(debate=debate, motion=motion, confirmed=True)

        for side in self.tournament.sides:
            dt = DebateTeam.objects.create(debate=debate, team=self.teams[side], side=side)
            TeamScore.objects.create(debate_team=dt, ballot_submission=ballotsub,
                win=side in [DebateSide.OO, DebateSide.CG])

        stats = MotionBPStatsCalculator(self.tournament)
        motion = next(stats.motions)
        assert motion.reference == "Elim"

        self.assertEqual(motion.s0_advancing, 0)
        self.assertEqual(motion.s1_advancing, 1)
        self.assertEqual(motion.s2_advancing, 1)
        self.assertEqual(motion.s3_advancing, 0)
        self.assertEqual(motion.s0_eliminated, 1)
        self.assertEqual(motion.s1_eliminated, 0)
        self.assertEqual(motion.s2_eliminated, 0)
        self.assertEqual(motion.s3_eliminated, 1)
