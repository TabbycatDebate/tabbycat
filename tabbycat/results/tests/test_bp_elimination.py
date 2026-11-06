from importlib import import_module

from django.db import connection
from django.test import TestCase

from breakqual.models import BreakCategory
from draw.generator.bpelimination import AfterPartialBPEliminationDrawGenerator, SubsequentBPEliminationDrawGenerator
from draw.generator.pairing import BPEliminationResultPairing
from draw.models import Debate, DebateTeam
from draw.types import DebateSide
from participants.models import Institution, Speaker, Team
from results.models import BallotSubmission, TeamScore
from tournaments.models import Round, Tournament


class TestBPScoredElimination(TestCase):

    sides = [DebateSide.OG, DebateSide.OO, DebateSide.CG, DebateSide.CO]

    def setUp(self):
        self.tournament = Tournament.objects.create(slug='bp-elimination', name='BP Elimination')
        self.tournament.preferences['debate_rules__teams_in_debate'] = 4
        self.tournament.preferences['debate_rules__substantive_speakers'] = 2
        self.tournament.preferences['debate_rules__reply_scores_enabled'] = False
        self.tournament.preferences['debate_rules__speakers_in_ballots'] = 'always'
        self.tournament.preferences['debate_rules__ballots_per_debate_elim'] = 'per-debate'
        self.semifinal = Round.objects.create(
            tournament=self.tournament, seq=1, schedule_group=1,
            stage=Round.Stage.ELIMINATION, draw_type=Round.DrawType.ELIMINATION,
        )
        self.final = Round.objects.create(
            tournament=self.tournament, seq=2, schedule_group=2,
            stage=Round.Stage.ELIMINATION, draw_type=Round.DrawType.ELIMINATION,
        )
        institution = Institution.objects.create(name='Institution', code='Inst')
        self.teams = []
        for i in range(12):
            team = Team.objects.create(tournament=self.tournament, institution=institution, reference=str(i))
            for position in [1, 2]:
                Speaker.objects.create(team=team, name=f'Speaker {i}-{position}')
            self.teams.append(team)

    def make_ballot(self, teams, room_rank=1, round=None):
        debate = Debate.objects.create(round=round or self.semifinal, room_rank=room_rank)
        for side, team in zip(self.sides, teams):
            DebateTeam.objects.create(debate=debate, team=team, side=side)
        ballot = BallotSubmission.objects.create(
            debate=debate, confirmed=True, submitter_type=BallotSubmission.Submitter.TABROOM,
        )
        result = ballot.result
        # Closing teams advance, so advancement cannot be inferred from side order.
        for side, team, score in zip(self.sides, teams, [73, 72, 76, 75]):
            for position, speaker in enumerate(team.speaker_set.all(), start=1):
                result.set_speaker(side, position, speaker)
                result.set_score(side, position, score)
        result.save()
        return ballot

    def test_advancement_from_saved_speaker_scores(self):
        ballot = self.make_ballot(self.teams[:4])
        # Simulate a ballot saved before scored elimination wins were recorded.
        ballot.teamscore_set.update(win=False)
        result = BallotSubmission.objects.get(pk=ballot.pk).result
        self.assertEqual(result.advancing_teams(), self.teams[2:4])
        self.assertEqual([dt.team for dt in result.eliminated_dt()], self.teams[:2])

    def test_saved_wins_match_advancing_teams(self):
        ballot = self.make_ballot(self.teams[:4])
        self.assertEqual(dict(ballot.teamscore_set.values_list('debate_team__side', 'win')), {
            DebateSide.OG: False, DebateSide.OO: False,
            DebateSide.CG: True, DebateSide.CO: True,
        })

    def test_resaving_repairs_existing_win_values(self):
        ballot = self.make_ballot(self.teams[:4])
        ballot.teamscore_set.update(win=False)
        BallotSubmission.objects.get(pk=ballot.pk).result.save()
        self.assertCountEqual(
            ballot.teamscore_set.filter(win=True).values_list('debate_team__team_id', flat=True),
            [team.pk for team in self.teams[2:4]],
        )

    def run_win_repair(self):
        migration = import_module('results.migrations.0021_repair_scored_bp_elimination_wins')
        with connection.schema_editor() as editor:
            migration.Migration.operations[0].database_forwards('results', editor, None, None)

    def test_migration_repairs_saved_ballots(self):
        semifinal = self.make_ballot(self.teams[:4])
        final = self.make_ballot(self.teams[:4], round=self.final)
        final.confirmed = False
        final.save()
        for ballot in (semifinal, final):
            ballot.teamscore_set.update(win=False)
        self.run_win_repair()
        self.run_win_repair()  # Running the repair again preserves corrected wins.
        for ballot, winners in ((semifinal, [DebateSide.CG, DebateSide.CO]), (final, [DebateSide.CG])):
            with self.subTest(ballot=ballot.pk):
                self.assertCountEqual(
                    ballot.teamscore_set.filter(win=True).values_list('debate_team__side', flat=True), winners,
                )

    def test_migration_final_ignores_later_rounds_in_other_categories(self):
        categories = [BreakCategory.objects.create(
            tournament=self.tournament, name=name, slug=name, seq=seq,
            break_size=4, is_general=True, priority=seq,
        ) for seq, name in enumerate(['open', 'esl'])]
        self.final.break_category = categories[0]
        self.final.save()
        Round.objects.create(
            tournament=self.tournament, seq=3, schedule_group=3, break_category=categories[1],
            stage=Round.Stage.ELIMINATION, draw_type=Round.DrawType.ELIMINATION,
        )
        ballot = self.make_ballot(self.teams[:4], round=self.final)
        ballot.teamscore_set.update(win=False)
        self.run_win_repair()
        self.assertEqual(
            list(ballot.teamscore_set.filter(win=True).values_list('debate_team__side', flat=True)),
            [DebateSide.CG],
        )

    def test_migration_preserves_ineligible_ballots(self):
        preliminary = Round.objects.create(
            tournament=self.tournament, seq=0, schedule_group=0,
            stage=Round.Stage.PRELIMINARY, draw_type=Round.DrawType.RANDOM,
        )
        self.tournament.preferences['debate_rules__ballots_per_debate_prelim'] = 'per-debate'
        prelim_ballot = self.make_ballot(self.teams[:4], round=preliminary)
        forfeit = self.make_ballot(self.teams[:4])
        forfeit.forfeit = True
        forfeit.save()
        unranked = self.make_ballot(self.teams[:4])
        unranked.teamscore_set.update(points=None, score=None)
        incomplete = self.make_ballot(self.teams[:4])
        incomplete.teamscore_set.filter(debate_team__side=DebateSide.CO).delete()
        tied = self.make_ballot(self.teams[:4])
        tied.teamscore_set.update(points=2)
        two_team = self.make_ballot(self.teams[:4])
        two_team.debate.debateteam_set.filter(side__in=[DebateSide.CG, DebateSide.CO]).delete()
        ballots = [prelim_ballot, forfeit, unranked, incomplete, tied, two_team]
        for ballot in ballots:
            ballot.teamscore_set.update(win=False)
        scores = list(TeamScore.objects.order_by('pk').values())
        self.run_win_repair()
        self.assertEqual(list(TeamScore.objects.order_by('pk').values()), scores)

    def test_subsequent_draw(self):
        self.make_ballot(self.teams[:4], room_rank=1)
        self.make_ballot(self.teams[4:8], room_rank=2)
        debates = self.semifinal.debate_set_with_prefetches(results=True)
        results = [BPEliminationResultPairing.from_debate(debate) for debate in debates]
        pairings = SubsequentBPEliminationDrawGenerator(self.teams[:8], results=results).make_pairings()
        self.assertEqual(len(pairings), 1)
        self.assertEqual(pairings[0].teams, self.teams[2:4] + self.teams[6:8])

    def test_draw_after_partial_elimination(self):
        self.make_ballot(self.teams[4:8], room_rank=5)
        self.make_ballot(self.teams[8:12], room_rank=6)
        debates = self.semifinal.debate_set_with_prefetches(results=True)
        results = [BPEliminationResultPairing.from_debate(debate) for debate in debates]
        pairings = AfterPartialBPEliminationDrawGenerator(self.teams, results=results).make_pairings()
        self.assertEqual([pairing.teams for pairing in pairings], [
            [self.teams[0], self.teams[3], *self.teams[6:8]],
            [self.teams[1], self.teams[2], *self.teams[10:12]],
        ])

    def test_final_has_one_winner(self):
        ballot = self.make_ballot(self.teams[:4], round=self.final)
        self.assertEqual(
            list(ballot.teamscore_set.filter(win=True).values_list('debate_team__side', flat=True)),
            [DebateSide.CG],
        )
        result = BallotSubmission.objects.get(pk=ballot.pk).result
        self.assertEqual(result.advancing_teams(), [self.teams[2]])
        self.assertEqual([dt.team for dt in result.eliminated_dt()], [
            self.teams[0], self.teams[1], self.teams[3],
        ])

    def test_invalid_scores_do_not_advance_teams(self):
        result = self.make_ballot(self.teams[:4]).result
        result.set_score(DebateSide.CG, 1, None)
        self.assertEqual(result.advancing_teams(), [])
        result.set_score(DebateSide.CG, 1, 74)  # Tie CG and CO on 150 points.
        self.assertEqual(result.advancing_teams(), [])

    def test_ranked_ballot_advancement_does_not_require_break_round(self):
        self.tournament.preferences['debate_rules__ballots_per_debate_prelim'] = 'per-debate'
        preliminary = Round.objects.create(
            tournament=self.tournament, seq=0, schedule_group=0,
            stage=Round.Stage.PRELIMINARY, draw_type=Round.DrawType.RANDOM,
        )
        ballot = self.make_ballot(self.teams[:4], round=preliminary)
        self.assertFalse(ballot.teamscore_set.filter(win=True).exists())
        result = ballot.result
        self.assertEqual([dt.team for dt in result.get_ranked_dt()], [
            self.teams[2], self.teams[3], self.teams[0], self.teams[1],
        ])
        self.assertEqual(result.advancing_teams(), self.teams[2:4])

    def test_scoreless_ballot_still_uses_declared_winners(self):
        self.tournament.preferences['debate_rules__speakers_in_ballots'] = 'prelim'
        self.tournament._prefs.clear()
        debate = Debate.objects.create(round=self.semifinal)
        for side, team in zip(self.sides, self.teams[:4]):
            DebateTeam.objects.create(debate=debate, team=team, side=side)
        ballot = BallotSubmission.objects.create(
            debate=debate, confirmed=True, submitter_type=BallotSubmission.Submitter.TABROOM,
        )
        ballot.result.set_winners({DebateSide.OG, DebateSide.CO})
        ballot.result.save()
        self.assertCountEqual(
            ballot.teamscore_set.filter(win=True).values_list('debate_team__side', flat=True),
            [DebateSide.OG, DebateSide.CO],
        )
        result = BallotSubmission.objects.get(pk=ballot.pk).result
        self.assertEqual(result.advancing_teams(), [self.teams[0], self.teams[3]])
        self.assertEqual([dt.team for dt in result.eliminated_dt()], self.teams[1:3])
