import logging

from django.test import TestCase

from breakqual.models import BreakingTeam
from utils.tests import ConditionalTableViewTestsMixin, suppress_logs


class BreakingTeamsViewTestMixin(ConditionalTableViewTestsMixin):
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

    def test_set_preference(self):
        # Suppress standings queryset info logging
        with suppress_logs('standings.metrics', logging.INFO):
            super().test_set_preference()


class PublicOpenBreakingTeamsViewTest(BreakingTeamsViewTestMixin, TestCase):
    break_slug = 'open'


class PublicESLBreakingTeamsViewTest(BreakingTeamsViewTestMixin, TestCase):
    break_slug = 'esl'


class PublicNoviceBreakingTeamsViewTest(BreakingTeamsViewTestMixin, TestCase):
    break_slug = 'novice'


class PublicBreakingAdjudicatorsViewTest(ConditionalTableViewTestsMixin, TestCase):
    view_name = 'breakqual-public-adjs'
    view_toggle = 'public_features__public_breaking_adjs'
