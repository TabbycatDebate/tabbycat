from django.test import TestCase

from utils.tests import ConditionalTableViewTestsMixin


class PublicDrawForRoundViewTest(ConditionalTableViewTestsMixin, TestCase):
    """ Check that an arbitrary round can have its draw seen if enabled"""
    view_name = 'draw-public-for-round'
    view_toggle_preference = 'public_features__public_draw'
    view_toggle_on_value = 'all-released'
    view_toggle_off_value = 'off'
    round_seq = 2

    def expected_row_counts(self):
        return [self.round.debate_set.count()]


class PublicDrawForCurrentRoundViewTest(ConditionalTableViewTestsMixin, TestCase):
    """ Check that the current round can have its draw seen if enabled"""
    view_name = 'draw-public-current-rounds'
    view_toggle_preference = 'public_features__public_draw'
    view_toggle_on_value = 'current'
    view_toggle_off_value = 'off'

    def setUp(self):
        super().setUp()
        self.tournament.current_round = self.tournament.round_set.get(seq=2)

    def expected_row_counts(self):
        r = self.tournament.round_set.get(seq=2)
        return [r.debate_set.count()]
