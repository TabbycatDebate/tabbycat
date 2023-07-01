from unittest.mock import patch

from django.http.response import Http404
from django.test import RequestFactory, TestCase

from options.presets import PreferencesPreset
from options.views import SetPresetPreferencesView
from tournaments.models import Tournament
from utils.misc import reverse_tournament


class TestPreset(PreferencesPreset):
    name         = "Test Rules"
    description  = "Used for unit tests"
    show_in_list = False

    # Scoring
    scoring__score_min = 70
    scoring__score_max = 80


class TestSetPresetPreferencesView(TestCase):
    def set_up_tournament(self):
        tournament = Tournament.objects.create(slug="preset", name="Preset Testing")
        tournament.preferences['scoring__score_min'] = 0
        tournament.preferences['scoring__score_max'] = 100
        return tournament

    @patch('options.presets.all_presets', return_value=[TestPreset])
    def test_title_with_preset(self, mock_all_presets):
        tournament = self.set_up_tournament()
        request = RequestFactory().get(reverse_tournament('options-presets-confirm', tournament, kwargs={'preset_name': 'testpreset'}))
        view = SetPresetPreferencesView()
        view.setup(request, preset_name='testpreset')

        self.assertEqual(view.get_page_title(), 'Apply Preset: Test Rules')
        tournament.delete()

    @patch('options.presets.all_presets', return_value=[TestPreset])
    def test_404_with_invalid_preset(self, mock_all_presets):
        tournament = self.set_up_tournament()
        request = RequestFactory().get(reverse_tournament('options-presets-confirm', tournament, kwargs={'preset_name': 'testpreset'}))
        view = SetPresetPreferencesView()
        view.setup(request, preset_name='invalidpreset')

        with self.assertRaises(Http404):
            view.get_page_title()
        tournament.delete()

    @patch('options.presets.all_presets', return_value=[TestPreset])
    @patch('options.views.messages.success')
    @patch('django.views.generic.edit.HttpResponseRedirect')
    def test_save_form(self, mock_redirect, mock_success, mock_all_presets):
        tournament = self.set_up_tournament()
        request = RequestFactory().get(reverse_tournament('options-presets-confirm', tournament, kwargs={'preset_name': 'testpreset'}))
        view = SetPresetPreferencesView()
        view.setup(request, tournament_slug=tournament.slug, preset_name='testpreset')

        form = TestPreset.get_form(tournament, data={'scoring__score_min': 70, 'scoring__score_max': 80})
        form.is_valid()
        view.form_valid(form)
        mock_redirect.assert_called_with(reverse_tournament('options-tournament-index', tournament))

        tournament.delete()

    @patch('options.presets.all_presets', return_value=[TestPreset])
    def test_gets_correct_form(self, mock_all_presets):
        tournament = self.set_up_tournament()
        request = RequestFactory().get(reverse_tournament('options-presets-confirm', tournament, kwargs={'preset_name': 'testpreset'}))
        view = SetPresetPreferencesView()
        view.setup(request, tournament_slug=tournament.slug, preset_name='testpreset')

        form = view.get_form()
        for pref in ['scoring__score_min', 'scoring__score_max']:
            self.assertIn(pref, form.fields)
        tournament.delete()
