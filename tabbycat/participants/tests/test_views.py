from django.test import TestCase

from utils.tests import ConditionalTableViewTestsMixin
from participants.models import Speaker


class PublicParticipantsViewTestCase(ConditionalTableViewTestsMixin, TestCase):

    view_toggle = 'public_features__public_participants'
    view_name = 'participants-public-list'

    def expected_row_counts(self):
        return [
            self.t.adjudicator_set.count(),
            Speaker.objects.filter(team__tournament=self.t).count(),
        ]
