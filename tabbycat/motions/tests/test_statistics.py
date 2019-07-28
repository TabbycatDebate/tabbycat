from django.test import TestCase

from draw.models import Debate, DebateTeam
from motions.models import DebateTeamMotionPreference, Motion
from motions.statistics import MotionBPStatsCalculator, MotionTwoTeamStatsCalculator
from participants.models import Team
from results.models import BallotSubmission, TeamScore
from tournaments.models import Round, Tournament


class TestMotionStatisticsTwoTeam(TestCase):
    """Very basic test for motion statistics for two-team formats, involving
    just one debate and two motions."""

    def setUp(self):
        self.tournament = Tournament.objects.create(slug="motions-twoteam", name="Motion statistics two-team")
        self.tournament.preferences['debate_rules__teams_in_debate'] = 'two'
        self.tournament.preferences['debate_rules__ballots_per_debate_prelim'] = 'per-adj'
        team1 = Team.objects.create(tournament=self.tournament, reference="1", use_institution_prefix=False)
        team2 = Team.objects.create(tournament=self.tournament, reference="2", use_institution_prefix=False)
        rd = Round.objects.create(tournament=self.tournament, seq=1)
        motion = Motion.objects.create(round=rd, text="Motion", reference="Motion")
        debate = Debate.objects.create(round=rd)
        dt1 = DebateTeam.objects.create(debate=debate, team=team1, side=DebateTeam.SIDE_AFF)
        dt2 = DebateTeam.objects.create(debate=debate, team=team2, side=DebateTeam.SIDE_NEG)
        ballotsub = BallotSubmission.objects.create(debate=debate, motion=motion, confirmed=True)
        TeamScore.objects.create(debate_team=dt1, ballot_submission=ballotsub,
            margin=+2, points=1, score=101, win=True,  votes_given=1, votes_possible=1)
        TeamScore.objects.create(debate_team=dt2, ballot_submission=ballotsub,
            margin=-2, points=0, score=99, win=False, votes_given=0, votes_possible=1)

        vetoed = Motion.objects.create(round=rd, text="No one wants", reference="Vetoed")
        DebateTeamMotionPreference.objects.create(debate_team=dt1, ballot_submission=ballotsub,
            motion=vetoed, preference=3)
        DebateTeamMotionPreference.objects.create(debate_team=dt2, ballot_submission=ballotsub,
            motion=vetoed, preference=3)

    def tearDown(self):
        DebateTeam.objects.filter(team__tournament=self.tournament).delete()
        self.tournament.delete()

    def test_statistics(self):
        stats = MotionTwoTeamStatsCalculator(self.tournament)
        for m in stats.motions:
            if m.reference == "Motion":
                motion = m
            if m.reference == "Vetoed":
                vetoed = m

        self.assertEqual(motion.aff_wins, 1)
        self.assertEqual(motion.neg_wins, 0)
        self.assertEqual(motion.aff_vetoes, 0)
        self.assertEqual(motion.neg_vetoes, 0)
        self.assertEqual(motion.aff_win_percentage, 100)
        self.assertEqual(motion.neg_win_percentage, 0)
        self.assertEqual(motion.aff_veto_percentage, 0)
        self.assertEqual(motion.neg_veto_percentage, 0)

        self.assertEqual(vetoed.aff_wins, 0)
        self.assertEqual(vetoed.neg_wins, 0)
        self.assertEqual(vetoed.aff_vetoes, 1)
        self.assertEqual(vetoed.neg_vetoes, 1)
        self.assertEqual(vetoed.aff_veto_percentage, 50)
        self.assertEqual(vetoed.neg_veto_percentage, 50)


class TestMotionStatisticsBP(TestCase):
    """Very basic test for motion statistics for two-team formats, involving
    just one debate and two motions."""

    def setUp(self):
        self.tournament = Tournament.objects.create(slug="motions-bp", name="Motion statistics BP")
        self.tournament.preferences['debate_rules__teams_in_debate'] = 'bp'
        self.tournament.preferences['debate_rules__ballots_per_debate_prelim'] = 'per-debate'
        self.teams = {side: Team.objects.create(tournament=self.tournament, reference=side,
                use_institution_prefix=False) for side in self.tournament.sides}

    def tearDown(self):
        DebateTeam.objects.filter(team__tournament=self.tournament).delete()
        self.tournament.delete()

    def test_prelim_statistics(self):
        rd = Round.objects.create(tournament=self.tournament, seq=1, stage=Round.STAGE_PRELIMINARY)
        motion = Motion.objects.create(round=rd, text="Prelim motion", reference="Prelim")
        debate = Debate.objects.create(round=rd)
        ballotsub = BallotSubmission.objects.create(debate=debate, motion=motion, confirmed=True)

        for i, side in enumerate(self.tournament.sides):
            dt = DebateTeam.objects.create(debate=debate, team=self.teams[side], side=side)
            TeamScore.objects.create(debate_team=dt, ballot_submission=ballotsub,
                points=i, score=100+i)

        stats = MotionBPStatsCalculator(self.tournament)
        motion = next(stats.motions)
        assert motion.reference == "Prelim"

        self.assertEqual(motion.og_average, 0)
        self.assertEqual(motion.oo_average, 1)
        self.assertEqual(motion.cg_average, 2)
        self.assertEqual(motion.co_average, 3)

        self.assertEqual(motion.og_0_count, 1)
        self.assertEqual(motion.og_1_count, 0)
        self.assertEqual(motion.og_2_count, 0)
        self.assertEqual(motion.og_3_count, 0)
        self.assertEqual(motion.oo_0_count, 0)
        self.assertEqual(motion.oo_1_count, 1)
        self.assertEqual(motion.oo_2_count, 0)
        self.assertEqual(motion.oo_3_count, 0)
        self.assertEqual(motion.cg_0_count, 0)
        self.assertEqual(motion.cg_1_count, 0)
        self.assertEqual(motion.cg_2_count, 1)
        self.assertEqual(motion.cg_3_count, 0)
        self.assertEqual(motion.co_0_count, 0)
        self.assertEqual(motion.co_1_count, 0)
        self.assertEqual(motion.co_2_count, 0)
        self.assertEqual(motion.co_3_count, 1)

        self.assertAlmostEqual(motion.counts_by_half['top'], 0.5)
        self.assertAlmostEqual(motion.counts_by_half['bottom'], 2.5)
        self.assertAlmostEqual(motion.counts_by_bench['gov'], 1)
        self.assertAlmostEqual(motion.counts_by_bench['opp'], 2)

    def test_elim_statistics(self):
        rd = Round.objects.create(tournament=self.tournament, seq=1, stage=Round.STAGE_ELIMINATION)
        motion = Motion.objects.create(round=rd, text="Elim motion", reference="Elim")
        debate = Debate.objects.create(round=rd)
        ballotsub = BallotSubmission.objects.create(debate=debate, motion=motion, confirmed=True)

        for side in self.tournament.sides:
            dt = DebateTeam.objects.create(debate=debate, team=self.teams[side], side=side)
            TeamScore.objects.create(debate_team=dt, ballot_submission=ballotsub,
                win=side in ['oo', 'cg'])

        stats = MotionBPStatsCalculator(self.tournament)
        motion = next(stats.motions)
        assert motion.reference == "Elim"

        self.assertEqual(motion.og_advancing, 0)
        self.assertEqual(motion.oo_advancing, 1)
        self.assertEqual(motion.cg_advancing, 1)
        self.assertEqual(motion.co_advancing, 0)
        self.assertEqual(motion.og_eliminated, 1)
        self.assertEqual(motion.oo_eliminated, 0)
        self.assertEqual(motion.cg_eliminated, 0)
        self.assertEqual(motion.co_eliminated, 1)
