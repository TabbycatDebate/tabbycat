from utils.views_tests import ConditionalTableViewTest, TestCase

from participants.models import Team

class PublicResultsForRoundViewTestCase(ConditionalTableViewTest, TestCase):

    view_toggle = 'public_features__public_results'
    view_name = 'public_results'
    round_seq = 3
