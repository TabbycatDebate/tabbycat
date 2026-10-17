from django.core.cache import cache
from django.test import TestCase

from tournaments.utils import get_side_name
from utils.tests import ConditionalTableViewTestsMixin


class PublicResultsForRoundViewTestCase(ConditionalTableViewTestsMixin, TestCase):

    view_toggle_preference = 'public_features__public_results'
    view_name = 'results-public-round'
    round_seq = 3

    def expected_row_counts(self):
        return [self.round.debate_set.count() * 2]

    def test_debate_view_without_pairings(self):
        self.round.debate_set.all().delete()
        self.round.completed = False
        self.round.silent = True
        self.round.save()
        self.tournament.preferences[self.view_toggle_preference] = True
        self.tournament.preferences['debate_rules__ballots_per_debate_prelim'] = 'per-debate'
        self.tournament.preferences['tab_release__all_results_released'] = True

        for teams_in_debate in (2, 4):
            with self.subTest(teams_in_debate=teams_in_debate):
                self.tournament.preferences['debate_rules__teams_in_debate'] = teams_in_debate
                cache.clear()
                response = self.client.get(self.reverse_url(self.view_name), {'view': 'debate'})

                self.assertResponseOK(response)
                self.assertEqual(response.context['view_type'], 'debate')
                self.assertResponseTableRowCountsEqual(response, [0], allow_vacuous=True)
                table = self.get_table_data(response)[0]
                keys = [header['key'] for header in table['head']]
                for side in range(teams_in_debate):
                    self.assertIn(get_side_name(response.context['tournament'], side, 'abbr'), keys)

    def test_debate_view_uses_actual_sides(self):
        self.tournament.preferences[self.view_toggle_preference] = True
        self.tournament.preferences['debate_rules__ballots_per_debate_prelim'] = 'per-debate'
        self.tournament.preferences['debate_rules__teams_in_debate'] = 4
        self.round.debate_set.update(sides_confirmed=True)
        cache.clear()
        response = self.client.get(self.reverse_url(self.view_name), {'view': 'debate'})

        self.assertResponseOK(response)
        self.assertResponseTableRowCountsEqual(response, [self.round.debate_set.count()])
        table = self.get_table_data(response)[0]
        keys = [header['key'] for header in table['head']]
        for side in range(2):
            self.assertIn(get_side_name(response.context['tournament'], side, 'abbr'), keys)
        for side in range(2, 4):
            self.assertNotIn(get_side_name(response.context['tournament'], side, 'abbr'), keys)
