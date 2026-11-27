from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models import Count
from django.test import TestCase

from adjfeedback.models import AdjudicatorFeedback
from tournaments.models import Tournament
from utils.tests import CompletedTournamentTestMixin, ConditionalTableViewTestsMixin


class PublicAddFeedbackViewTestCase(ConditionalTableViewTestsMixin, TestCase):

    view_name = 'adjfeedback-public-add-index'
    view_toggle_preference = 'data_entry__participant_feedback'
    view_toggle_on_value = 'public'
    view_toggle_off_value = 'off'

    def expected_row_counts(self):
        return [
            self.tournament.team_set.count(),
            self.tournament.adjudicator_set.count(),
        ]


class TesterFeedbackViewTestCase(CompletedTournamentTestMixin, TestCase):

    def test_shows_feedback_from_testers_in_this_tournament(self):
        debate = self.tournament.round_set.first().debate_set.annotate(
            panel_size=Count('debateadjudicator'),
        ).filter(panel_size=3).first()
        marked, core, ordinary = debate.debateadjudicator_set.select_related('adjudicator')
        marked.adjudicator.adj_core = False
        marked.adjudicator.is_tester = True
        marked.adjudicator.tournament = None
        marked.adjudicator.save()
        core.adjudicator.adj_core = True
        core.adjudicator.is_tester = False
        core.adjudicator.save()
        ordinary.adjudicator.adj_core = ordinary.adjudicator.is_tester = False
        ordinary.adjudicator.tournament = None
        ordinary.adjudicator.save()

        marked_feedback = AdjudicatorFeedback.objects.create(
            adjudicator=ordinary.adjudicator, source_adjudicator=marked, score=4, ignored=True,
        )
        core_feedback = AdjudicatorFeedback.objects.create(
            adjudicator=ordinary.adjudicator, source_adjudicator=core, score=5, confirmed=True,
        )
        AdjudicatorFeedback.objects.create(
            adjudicator=marked.adjudicator, source_adjudicator=ordinary, score=3,
        )
        AdjudicatorFeedback.objects.create(
            adjudicator=marked.adjudicator, source_team=debate.debateteam_set.first(), score=3,
        )

        other = Tournament.objects.create(name="Other tournament", slug='other')
        other_round = other.round_set.create(seq=1)
        other_debate = other_round.debate_set.create()
        other_source = other_debate.debateadjudicator_set.create(
            adjudicator=marked.adjudicator, type=marked.type,
        )
        AdjudicatorFeedback.objects.create(
            adjudicator=ordinary.adjudicator, source_adjudicator=other_source, score=3,
        )

        cache.clear()
        admin = get_user_model().objects.get(username='admin')
        self.client.force_login(admin)
        response = self.client.get(self.reverse_url('adjfeedback-view-testers'))

        self.assertContains(response, "Feedback from Testers")
        self.assertEqual(list(response.context['feedbacks']), [core_feedback, marked_feedback])
