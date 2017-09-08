from django.test import TestCase

from utils.tests import ConditionalTableViewTestsMixin


class PublicDrawForRoundViewTest(ConditionalTableViewTestsMixin, TestCase):
    view_name = 'draw-public-for-round'
    view_toggle = 'public_features__public_draw'
    round_seq = 2

    def table_data(self):
        # Check number of debates is correct
        round = self.t.round_set.get(seq=self.round_seq)
        return round.debate_set.all().count()
