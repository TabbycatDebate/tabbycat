from utils.tests import ConditionalTableViewTest, TestCase

from breakqual.models import BreakingTeam


class BreakingTeamsViewTest(ConditionalTableViewTest):
    view_name = 'breakqual-public-teams'
    view_toggle = 'public_features__public_breaking_teams'

    def get_url_kwargs(self):
        kwargs = super().get_url_kwargs()
        kwargs['category'] = self.break_slug
        return kwargs

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
    view_name = 'breakqual-public-adjs'
    view_toggle = 'public_features__public_breaking_adjs'
