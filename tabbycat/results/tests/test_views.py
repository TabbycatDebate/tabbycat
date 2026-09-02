from django.test import TestCase

from utils.tests import ConditionalTableViewTestsMixin


class PublicResultsForRoundViewTestCase(ConditionalTableViewTestsMixin, TestCase):

    view_toggle_preference = 'public_features__public_results'
    view_name = 'results-public-round'
    round_seq = 3

    def expected_row_counts(self):
        return [self.round.debate_set.count() * 2]
