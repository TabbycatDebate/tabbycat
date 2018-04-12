from django.test import TestCase

from utils.tests import ConditionalTableViewTestsMixin
from participants.models import Adjudicator, Team


class PublicAddFeedbackViewTestCase(ConditionalTableViewTestsMixin, TestCase):

    view_toggle = 'data_entry__participant_feedback'
    view_name = 'adjfeedback-public-add-index'
    view_toggle_on = 'public'
    view_toggle_off = 'off'

    def table_data_a(self):
        # Check number of speakers matches
        return Team.objects.filter(team__tournament=self.t).count()

    def table_data_b(self):
        # Check number of adjs matches
        return Adjudicator.objects.filter(tournament=self.t).count()
