from decimal import Decimal
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from options.management.commands.applypreset import Command
from options.presets import PreferencesPreset
from tournaments.models import Tournament


class TestPreset(PreferencesPreset):
    name         = "Test Rules"
    description  = "Used for unit tests"
    show_in_list = False

    # Scoring
    scoring__score_min = Decimal('70')
    scoring__score_max = Decimal('80')


class ApplyPresetTests(TestCase):
    @patch('options.management.commands.applypreset.all_presets', return_value=[TestPreset])
    def test_preset_options(self, mock_all_presets):
        with self.assertRaises(CommandError) as cm:
            Command().create_parser('', '').parse_args(['notvalidpreset'])
        self.assertEqual(str(cm.exception), "Error: argument preset: invalid choice: 'notvalidpreset' (choose from 'testpreset')")

    @patch('options.management.commands.applypreset.all_presets', return_value=[TestPreset])
    def test_set_invalid_preset(self, mock_all_presets):
        tournament = Tournament.objects.create(slug="command", name="Command Testing")
        with self.assertRaises(CommandError) as cm:
            call_command('applypreset', ['-t', 'command', 'notvalidpreset'])
        self.assertEqual(str(cm.exception), "Error: argument preset: invalid choice: 'notvalidpreset' (choose from 'testpreset')")
        tournament.delete()

    @patch('options.management.commands.applypreset.all_presets', return_value=[TestPreset])
    def test_set_valid_preset(self, mock_all_presets):
        tournament = Tournament.objects.create(slug="command", name="Command Testing")
        tournament.preferences['scoring__score_min'] = Decimal('0')
        tournament.preferences['scoring__score_max'] = Decimal('100')

        call_command('applypreset', ['-t', 'command', 'testpreset'])
        for pref, val in [('scoring__score_min', Decimal('70')), ('scoring__score_max', Decimal('80'))]:
            self.assertEqual(tournament.preferences[pref], val)
