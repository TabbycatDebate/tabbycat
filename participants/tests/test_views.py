from utils.views_tests import ConditionalTableViewTest, TestCase
from participants.models import Speaker, Adjudicator


class PublicParticipantsViewTestCase(ConditionalTableViewTest, TestCase):

    view_toggle = 'public_features__public_participants'
    view_name = 'public_participants'

    def table_data_a(self):
        # Check number of adjs matches
        return Adjudicator.objects.filter(tournament=self.t).count()

    def table_data_b(self):
        # Check number of speakers matches
        return Speaker.objects.filter(team__tournament=self.t).count()
