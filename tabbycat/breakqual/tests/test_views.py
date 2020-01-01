import logging

from django.test import TestCase

from utils.tests import ConditionalTableViewTestsMixin, suppress_logs


class BreakingTeamsViewTestMixin(ConditionalTableViewTestsMixin):
    view_name = 'breakqual-public-teams'
    view_toggle_preference = 'public_features__public_breaking_teams'

    def get_view_reverse_kwargs(self):
        kwargs = super().get_view_reverse_kwargs()
        kwargs['category'] = self.break_category_slug
        return kwargs

    def expected_row_counts(self):
        category = self.tournament.breakcategory_set.get(slug=self.break_category_slug)
        return [category.breaking_teams.count()]

    def test_view_enabled(self):
        # Suppress standings queryset info logging
        with suppress_logs('standings.metrics', logging.INFO):
            super().test_view_enabled()


class PublicOpenBreakingTeamsViewTest(BreakingTeamsViewTestMixin, TestCase):
    break_category_slug = 'open'


class PublicESLBreakingTeamsViewTest(BreakingTeamsViewTestMixin, TestCase):
    break_category_slug = 'esl'


class PublicNoviceBreakingTeamsViewTest(BreakingTeamsViewTestMixin, TestCase):
    break_category_slug = 'novice'


class PublicBreakingAdjudicatorsViewTest(ConditionalTableViewTestsMixin, TestCase):
    view_name = 'breakqual-public-adjs'
    view_toggle_preference = 'public_features__public_breaking_adjs'

    def expected_row_counts(self):
        return [self.tournament.adjudicator_set.filter(breaking=True).count()]
