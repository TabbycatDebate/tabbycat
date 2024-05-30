from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.http.response import Http404
from django.test import RequestFactory, TestCase

from options.preferences import scoring
from options.presets import PreferencesPreset, PublicInformation
from options.views import SetPresetPreferencesView, TournamentConfigIndexView, TournamentPreferenceFormView
from tournaments.models import Tournament
from utils.misc import reverse_tournament


class TestPreset(PreferencesPreset):
    name         = "Test Rules"
    description  = "Used for unit tests"
    show_in_list = False

    # Scoring
    scoring__score_min = Decimal('70')
    scoring__score_max = Decimal('80')


class TournamentConfigIndexViewTests(TestCase):

    def test_order_presets(self):
        tournament = Tournament.objects.create(slug="optionform", name="Option Form Testing")
        view = TournamentConfigIndexView()
        request = RequestFactory()
        request.user = get_user_model()(is_superuser=True)
        view.setup(request, tournament_slug=tournament.slug)

        presets = view.get_context_data()['presets']
        self.assertEqual(presets[0], PublicInformation)


class TournamentPreferenceFormViewTests(TestCase):

    @patch('options.views.tournament_preference_form_builder')
    def test_gets_correct_form(self, mock_builder):
        tournament = Tournament.objects.create(slug="optionform", name="Option Form Testing")
        view = TournamentPreferenceFormView()
        view.setup(RequestFactory().get(
            reverse_tournament('options-tournament-section', tournament, kwargs={'section': 'scoring'})), tournament_slug=tournament.slug, section='scoring',
        )
        view.get_form_class()
        mock_builder.assert_called_with(instance=tournament, section='scoring')
        tournament.delete()

    def test_section_does_not_exist(self):
        tournament = Tournament.objects.create(slug="optionform", name="Option Form Testing")
        tournament.round_set.create(seq=1, name='1', abbreviation='1', draw_type='M')
        request = RequestFactory().get(reverse_tournament('options-tournament-section', tournament, kwargs={'section': 'invalidsection'}))
        request.user = get_user_model()(is_superuser=True)

        view = TournamentPreferenceFormView()
        view.setup(request, tournament_slug=tournament.slug, section='invalidsection')

        with self.assertRaises(Http404):
            view.dispatch(request, section='invalidsection')

        tournament.delete()

    @patch('options.views.messages.success')
    @patch('django.views.generic.edit.HttpResponseRedirect')
    def test_save_form(self, mock_redirect, mock_success):
        tournament = Tournament.objects.create(slug="optionform", name="Option Form Testing")
        request = RequestFactory().get(reverse_tournament('options-tournament-section', tournament, kwargs={'section': 'scoring'}))
        view = TournamentPreferenceFormView()
        view.setup(request, tournament_slug=tournament.slug, section='scoring')
        view.section = scoring

        form = TestPreset.get_form(tournament, data={'scoring__score_min': Decimal('70'), 'scoring__score_max': Decimal('80')})
        form.is_valid()
        view.form_valid(form)
        mock_success.assert_called()
        mock_redirect.assert_called_with(reverse_tournament('options-tournament-index', tournament))

        tournament.delete()


class TestSetPresetPreferencesView(TestCase):
    def set_up_tournament(self):
        tournament = Tournament.objects.create(slug="preset", name="Preset Testing")
        tournament.preferences['scoring__score_min'] = Decimal('0')
        tournament.preferences['scoring__score_max'] = Decimal('100')
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

        form = TestPreset.get_form(tournament, data={'scoring__score_min': Decimal('70'), 'scoring__score_max': Decimal('80')})
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
