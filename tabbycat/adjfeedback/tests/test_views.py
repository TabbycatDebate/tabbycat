from django.test import TestCase

from utils.tests import ConditionalTableViewTestsMixin


class PublicAddFeedbackViewTestCase(ConditionalTableViewTestsMixin, TestCase):

    view_toggle = 'data_entry__participant_feedback'
    view_name = 'adjfeedback-public-add-index'
    view_toggle_on = 'public'
    view_toggle_off = 'off'

    def expected_row_counts(self):
        return [
            self.t.team_set.count(),
            self.t.adjudicator_set.count(),
        ]
