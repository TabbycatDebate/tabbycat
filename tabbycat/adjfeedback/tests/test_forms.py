from django.test import TestCase

from adjallocation.models import DebateAdjudicator
from adjfeedback.forms import make_feedback_form_class
from draw.models import Debate, DebateTeam
from participants.models import Adjudicator, Team
from tournaments.models import Round, Tournament


class FeedbackFormRoundEligibilityTests(TestCase):

    def setUp(self):
        self.tournament = Tournament.objects.create()
        self.tournament.preferences['feedback__feedback_from_teams'] = 'all-adjs'
        self.tournament.preferences['feedback__feedback_paths'] = 'all-adjs'
        self.team = Team.objects.create(tournament=self.tournament, reference='Team')
        self.chair = Adjudicator.objects.create(tournament=self.tournament, name='Chair')
        self.panellist = Adjudicator.objects.create(tournament=self.tournament, name='Panellist')
        self.round = Round.objects.create(
            tournament=self.tournament, seq=1, name='Round 1',
            draw_status=Round.Status.RELEASED, completed=True,
        )
        self.debate = self.create_debate(self.round)

    def create_debate(self, round):
        debate = Debate.objects.create(round=round)
        DebateTeam.objects.create(debate=debate, team=self.team, side=0)
        DebateAdjudicator.objects.create(debate=debate, adjudicator=self.chair, type=DebateAdjudicator.TYPE_CHAIR)
        DebateAdjudicator.objects.create(debate=debate, adjudicator=self.panellist, type=DebateAdjudicator.TYPE_PANEL)
        return debate

    def assert_feedback_targets(self, debate_ids, include_unreleased_draws=False, team_debate_ids=None):
        for source, targets, expected_debates in (
            (self.team, [self.chair, self.panellist], debate_ids if team_debate_ids is None else team_debate_ids),
            (self.chair, [self.panellist], debate_ids),
        ):
            with self.subTest(source=type(source).__name__, include_unreleased_draws=include_unreleased_draws):
                tournament = Tournament.objects.get(pk=self.tournament.pk)
                form = make_feedback_form_class(
                    source, tournament, {}, include_unreleased_draws=include_unreleased_draws,
                )()
                choices = list(form.fields['target'].choices)
                actual = {value for _, group in choices[1:] for value, _ in group}
                expected = {f'{debate_id}-{target.pk}' for debate_id in expected_debates for target in targets}
                self.assertEqual(actual, expected)

    def test_feedback_remains_available_after_all_rounds_completed(self):
        last_round = Round.objects.create(
            tournament=self.tournament, seq=2, draw_status=Round.Status.RELEASED, completed=True,
        )
        last_debate = self.create_debate(last_round)
        for include_unreleased in (False, True):
            self.assert_feedback_targets([self.debate.pk, last_debate.pk], include_unreleased_draws=include_unreleased)

    def test_feedback_available_before_elimination_draw_created(self):
        Round.objects.create(tournament=self.tournament, seq=2, stage=Round.Stage.ELIMINATION)

        self.assert_feedback_targets([self.debate.pk])

    def test_parallel_current_rounds_included_but_future_round_excluded(self):
        second_round = Round.objects.create(
            tournament=self.tournament, seq=2, schedule_group=2, draw_status=Round.Status.RELEASED,
        )
        third_round = Round.objects.create(
            tournament=self.tournament, seq=3, schedule_group=2, draw_status=Round.Status.RELEASED,
        )
        future_round = Round.objects.create(
            tournament=self.tournament, seq=4, schedule_group=3, draw_status=Round.Status.RELEASED,
        )
        second_debate = self.create_debate(second_round)
        third_debate = self.create_debate(third_round)
        self.create_debate(future_round)

        self.assert_feedback_targets([self.debate.pk, second_debate.pk, third_debate.pk])

    def test_unreleased_draw_only_available_to_tabroom(self):
        self.round.draw_status = Round.Status.CONFIRMED
        self.round.save()

        self.assert_feedback_targets([])
        self.assert_feedback_targets([self.debate.pk], include_unreleased_draws=True)

    def test_silent_round_excluded_only_for_teams(self):
        self.round.silent = True
        self.round.save()

        self.assert_feedback_targets([self.debate.pk], team_debate_ids=[])

    def test_elimination_round_excluded(self):
        self.round.stage = Round.Stage.ELIMINATION
        self.round.save()

        self.assert_feedback_targets([])
