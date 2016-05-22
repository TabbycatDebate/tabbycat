from utils.tests import ConditionalTableViewTest, TestCase

from tournaments.models import Round

class PublicResultsForRoundViewTestCase(ConditionalTableViewTest, TestCase):

    view_toggle = 'public_features__public_results'
    view_name = 'public_results'
    round_seq = 3

    def table_data(self):
        # Check number of debates is correct
        round = Round.objects.get(tournament=self.t, seq=self.round_seq)
        return len(round.get_draw())