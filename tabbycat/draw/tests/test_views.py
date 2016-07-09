from utils.tests import ConditionalTableViewTest, TestCase

from tournaments.models import Round


class PublicDrawForRoundViewTest(ConditionalTableViewTest, TestCase):
    view_name = 'public_draw_by_round'
    view_toggle = 'public_features__public_draw'
    round_seq = 2

    def table_data(self):
        # Check number of debates is correct
        round = Round.objects.get(tournament=self.t, seq=self.round_seq)
        return round.debate_set.all().count()
