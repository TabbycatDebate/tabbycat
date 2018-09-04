from django.test import TestCase

from utils.tests import ConditionalTableViewTestsMixin


class PublicResultsForRoundViewTestCase(ConditionalTableViewTestsMixin, TestCase):

    view_toggle = 'public_features__public_results'
    view_name = 'results-public-round'
    round_seq = 3

    def expected_row_counts(self):
        return [self.t.round_set.get(seq=self.round_seq).debate_set.count() * 2]
