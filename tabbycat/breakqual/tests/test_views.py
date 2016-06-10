from utils.tests import ConditionalTableViewTest, TestCase
from django.core.urlresolvers import reverse

from breakqual.models import BreakingTeam


class BreakingTeamsViewTest(ConditionalTableViewTest):
    view_name = 'public_breaking_teams'
    view_toggle = 'public_features__public_breaking_teams'

    def get_response(self):
        return self.client.get(reverse(self.view_name, kwargs={
            'tournament_slug': self.t.slug, 'category': self.break_slug}))

    def table_data(self):
        # Check number of rows in table matches number of breaking teams
        return BreakingTeam.objects.filter(
            break_category__slug=self.break_slug).count()


class PublicOpenBreakingTeamsViewTest(BreakingTeamsViewTest, TestCase):
    break_slug = 'open'


class PublicESLBreakingTeamsViewTest(BreakingTeamsViewTest, TestCase):
    break_slug = 'esl'


class PublicEFLBreakingTeamsViewTest(BreakingTeamsViewTest, TestCase):
    break_slug = 'efl'


class PublicBreakingAdjuidcatorsViewTest(ConditionalTableViewTest, TestCase):
    view_name = 'public_breaking_adjs'
    view_toggle = 'public_features__public_breaking_adjs'
