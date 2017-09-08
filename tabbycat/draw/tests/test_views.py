from tournaments.models import Round
from utils.misc import reverse_round, reverse_tournament
from utils.tests import TournamentTestCase, ConditionalTableViewTestCase


class PublicDrawForRoundViewTest(ConditionalTableViewTestCase):
    view_name = 'draw-public-for-round'
    view_toggle = 'public_features__public_draw'
    round_seq = 2

    def table_data(self):
        # Check number of debates is correct
        round = Round.objects.get(tournament=self.t, seq=self.round_seq)
        return round.debate_set.all().count()


class TestCreateDrawViewErrors(TournamentTestCase):

    fixtures = ['after_round_1.json']

    def test_no_checkins(self):
        client = Client()
