from django.contrib.auth import get_user_model
from django.test import TestCase

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


class AdjudicatorJsonAttributeSetViewsTestCase(CompletedTournamentTestMixin, TestCase):

    def setUp(self):
        super().setUp()
        user = get_user_model().objects.create(username='test_admin', is_superuser=True)
        self.client.force_login(user)
        self.adj = self.tournament.adjudicator_set.first()

    def post_json(self, view_name, payload):
        return self.client.post(self.reverse_url(view_name), data=payload,
                                content_type='application/json')

    def assert_saves(self, view_name, post_field, adj_field):
        for value in (True, False):
            response = self.post_json(view_name, {'id': self.adj.pk, post_field: value})
            self.assertEqual(response.status_code, 200)
            self.adj.refresh_from_db()
            self.assertEqual(getattr(self.adj, adj_field), value)

    def test_set_breaking(self):
        self.assert_saves('adjfeedback-set-adj-breaking-status', 'breaking', 'breaking')

    def test_set_tester(self):
        self.assert_saves('adjfeedback-set-adj-tester-status', 'tester', 'is_tester')
