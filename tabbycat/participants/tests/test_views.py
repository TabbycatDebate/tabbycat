from django.test import TestCase

from participants.models import Speaker
from utils.tests import ConditionalTableViewTestsMixin


class PublicParticipantsViewTestCase(ConditionalTableViewTestsMixin, TestCase):

    view_toggle_preference = 'public_features__public_participants'
    view_name = 'participants-public-list'

    def expected_row_counts(self):
        return [
            self.tournament.adjudicator_set.count(),
            Speaker.objects.filter(team__tournament=self.tournament).count(),
        ]
