import unittest
from decimal import Decimal
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase
from dynamic_preferences.forms import GlobalPreferenceForm

from options.forms import tournament_preference_form_builder
from tournaments.models import Tournament


class FormBuilderTest(unittest.TestCase):

    @patch('options.forms.preference_form_builder')
    def test_create_global_form(self, mock_builder):
        tournament_preference_form_builder(None, section='global')
        mock_builder.assert_called_with(GlobalPreferenceForm, [], section='global')


class TournamentPreferenceFormTests(TestCase):

    def setUp(self):
        self.tournament = Tournament.objects.create()

    def tearDown(self):
        self.tournament.delete()

    def test_falsy_preference_change(self):
        # Test that get_pref() doesn't get the current value if falsy in the posted data
        form = tournament_preference_form_builder(self.tournament, section='data_entry')()
        self.tournament.preferences['data_entry__public_use_password'] = False
        form.cleaned_data = {'data_entry__public_use_password': True, 'data_entry__public_password': ''}
        with self.assertRaises(ValidationError) as cm:
            form.clean()
        self.assertIsNotNone(cm.exception.args[0].get('data_entry__public_password'))

    def test_validation_between_prefs(self):
        tests = [
            ('scoring', (('score_min', Decimal('100')), ('score_max', Decimal('0')))),
            ('scoring', (('reply_score_min', Decimal('100')), ('reply_score_max', Decimal('0')))),
            ('feedback', (('adj_min_score', 100), ('adj_max_score', 0))),
            ('draw_rules', (('draw_side_allocations', 'balance'), ('draw_odd_bracket', 'intermediate1'))),
            ('debate_rules', (('ballots_per_debate_prelim', 'per-adj'), ('teams_in_debate', 4))),
            ('data_entry', (('public_use_password', True), ('public_password', ''))),
            ('ui_options', (('team_code_names', 'everywhere'), ('show_team_institutions', True))),
        ]
        for section, prefs in tests:
            with self.subTest(section=section, prefs=[p[0] for p in prefs]):
                form = tournament_preference_form_builder(self.tournament, section=section)()
                form.cleaned_data = {section + "__" + pref: val for pref, val in prefs}
                with self.assertRaises(ValidationError) as cm:
                    form.clean()
                self.assertIsNotNone(cm.exception.args[0].get(section + "__" + prefs[-1][0]))
