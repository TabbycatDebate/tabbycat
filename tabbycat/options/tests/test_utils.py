from itertools import product

from django.forms import ValidationError
from django.test import TestCase

from options.preferences import TeamCodeNames
from options.utils import use_team_code_names, use_team_code_names_data_entry, validate_metric_duplicates
from standings.teams import TeamStandingsGenerator
from tournaments.models import Tournament


class UseTeamCodeNamesTests(TestCase):

    def setUp(self):
        Tournament.objects.create(slug="unittest", name="Unit Testing")

    def tearDown(self):
        Tournament.objects.filter(slug='unittest').delete()

    def test_use_codes_if_setting(self):
        tournament = Tournament.objects.get(slug='unittest')
        for setting, admin in product([c[0] for c in TeamCodeNames.choices], (False, True)):
            with self.subTest(setting=setting, admin=admin):
                tournament._prefs['team_code_names'] = setting

                if setting in ['admin-tooltips-real', 'everywhere'] or (setting == 'admin-tooltips-code' and not admin):
                    self.assertTrue(use_team_code_names(tournament, admin))
                else:
                    self.assertFalse(use_team_code_names(tournament, admin))

    def test_use_codes_data_entry(self):
        tournament = Tournament.objects.get(slug='unittest')
        for setting, tabroom in product([c[0] for c in TeamCodeNames.choices], (False, True)):
            with self.subTest(setting=setting, tabroom=tabroom):
                tournament._prefs['team_code_names'] = setting

                if setting in ['off', 'all-tooltips']:
                    self.assertEqual(use_team_code_names_data_entry(tournament, tabroom), 'off')
                elif setting in ['admin-tooltips-code', 'admin-tooltips-real'] and tabroom:
                    self.assertEqual(use_team_code_names_data_entry(tournament, tabroom), 'both')
                elif setting == 'everywhere' or (setting in ['admin-tooltips-code', 'admin-tooltips-real'] and not tabroom):
                    self.assertEqual(use_team_code_names_data_entry(tournament, tabroom), 'code')


class DuplicatePreferencesTest(TestCase):

    def test_unique_metrics(self):
        self.assertIsNone(validate_metric_duplicates(TeamStandingsGenerator, ['wins', 'speaks_sum']))

    def test_repeatable_metrics(self):
        self.assertIsNone(validate_metric_duplicates(TeamStandingsGenerator, ['wins', 'wbw', 'speaks_sum', 'wbw']))

    def test_non_repeatable_metrics(self):
        with self.assertRaises(ValidationError):
            validate_metric_duplicates(TeamStandingsGenerator, ['wins', 'speaks_sum', 'wins'])
