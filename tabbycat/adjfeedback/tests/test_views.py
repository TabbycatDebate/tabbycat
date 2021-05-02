from django.test import TestCase

from utils.tests import ConditionalTableViewTestsMixin


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
