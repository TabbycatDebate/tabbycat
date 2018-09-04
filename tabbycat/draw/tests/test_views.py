from django.test import TestCase

from utils.tests import ConditionalTableViewTestsMixin


class PublicDrawForRoundViewTest(ConditionalTableViewTestsMixin, TestCase):
    """ Check that an arbitrary round can have its draw seen if enabled"""
    view_name = 'draw-public-for-round'
    view_toggle = 'public_features__public_draw'
    round_seq = 2
    view_toggle_on = 'all-released'  # Otherwise will assign True as the set state
    view_toggle_off = 'off'  # Otherwise False as the config's unset state

    def expected_row_counts(self):
        return [self.t.round_set.get(seq=self.round_seq).debate_set.count()]


class PublicDrawForCurrentRoundViewTest(ConditionalTableViewTestsMixin, TestCase):
    """ Check that the current round can have its draw seen if enabled"""
    view_name = 'draw-public-current-round'
    view_toggle = 'public_features__public_draw'
    view_toggle_on = 'current'  # Otherwise will assign True as the set state
    view_toggle_off = 'off'  # Otherwise False as the config's unset state

    def expected_row_counts(self):
        return [self.t.round_set.get(seq=2).debate_set.count()]
