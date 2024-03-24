from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase

from options.presets import get_preset_from_slug, PreferencesPreset
from tournaments.models import Tournament


class TestPreset(PreferencesPreset):
    name         = "Test Rules"
    description  = "Used for unit tests"
    show_in_list = False

    # Scoring
    scoring__score_min = Decimal('70')
    scoring__score_max = Decimal('80')


class TestPresets(TestCase):
    def set_up_tournament(self):
        tournament = Tournament.objects.create(slug="preset", name="Preset Testing")
        tournament.preferences['scoring__score_min'] = Decimal('0')
        tournament.preferences['scoring__score_max'] = Decimal('100')
        return tournament

    @patch('options.presets.all_presets', return_value=[TestPreset])
    def test_get_preset_good_slug(self, mock_all_presets):
        self.assertEqual(get_preset_from_slug('testpreset'), TestPreset)

    @patch('options.presets.all_presets', return_value=[])
    def test_get_preset_slug_invalid(self, mock_all_presets):
        with self.assertRaises(ValueError):
            get_preset_from_slug('testpreset')

    @patch('options.presets.all_presets', return_value=[TestPreset, TestPreset])
    def test_get_preset_many_presets(self, mock_all_presets):
        with self.assertLogs('options.presets', level='WARNING') as cm:
            self.assertEqual(get_preset_from_slug('testpreset'), TestPreset)
            self.assertEqual(cm.output, ['WARNING:options.presets:Found more than one preset for testpreset'])

    def test_preferences_does_not_include_meta(self):
        self.assertFalse('name' in list(TestPreset.get_preferences()))

    def test_preferences_includes_all_preferences(self):
        self.assertTrue(set(TestPreset.get_preferences()) == {'scoring__score_min', 'scoring__score_max'})

    def test_can_save_preset(self):
        tournament = self.set_up_tournament()
        TestPreset.save(tournament)

        for pref, new_val in [('scoring__score_min', Decimal('70')), ('scoring__score_max', Decimal('80'))]:
            self.assertEqual(tournament.preferences[pref], new_val)

        tournament.delete()

    def test_can_create_form(self):
        tournament = self.set_up_tournament()

        form = TestPreset.get_form(tournament)

        for pref, new_val in [('scoring__score_min', Decimal('70')), ('scoring__score_max', Decimal('80'))]:
            self.assertTrue(pref in form.fields)
            self.assertEqual(form[pref].initial, new_val)
            self.assertEqual(form[pref].changed, True)

        tournament.delete()

    def test_can_save_preset_form(self):
        tournament = self.set_up_tournament()

        form = TestPreset.get_form(tournament, data={'scoring__score_min': Decimal('70'), 'scoring__score_max': Decimal('80')})
        form.is_valid()
        form.update_preferences()

        for pref, new_val in [('scoring__score_min', Decimal('70')), ('scoring__score_max', Decimal('80'))]:
            self.assertEqual(tournament.preferences[pref], new_val)

        tournament.delete()
