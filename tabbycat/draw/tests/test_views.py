from django.test import TestCase

from utils.tests import ConditionalTableViewTestsMixin


class PublicDrawForRoundViewTest(ConditionalTableViewTestsMixin, TestCase):
    """ Check that an arbitrary round can have its draw seen if enabled"""
    view_name = 'draw-public-for-round'
    view_toggle = 'public_features__public_draw'
    round_seq = 2
    view_toggle_on = 'all-released'
    view_toggle_off = 'off'

    def table_data(self):
        # Check number of debates is correct
        round = self.t.round_set.get(seq=self.round_seq)
        return round.debate_set.all().count()


class PublicDrawForCurrentRoundViewTest(ConditionalTableViewTestsMixin, TestCase):
    """ Check that the current round can have its draw seen if enabled"""
    view_name = 'draw-public-current-rounds'
    view_toggle = 'public_features__public_draw'
    view_toggle_on = 'current'
    view_toggle_off = 'off'

    def table_data(self):
        # Check number of debates is correct
        round = self.t.round_set.get(seq=self.round_seq)
        return round.debate_set.all().count()
