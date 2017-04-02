import inspect

from django.contrib import messages
from django.http import Http404
from django.utils.text import slugify
from django.views.generic import TemplateView
from dynamic_preferences.views import PreferenceFormView

from actionlog.mixins import LogActionMixin
from actionlog.models import ActionLogEntry
from tournaments.mixins import TournamentMixin
from utils.mixins import SuperuserRequiredMixin
from utils.misc import reverse_tournament

from . import presets
from .forms import tournament_preference_form_builder
from .dynamic_preferences_registry import tournament_preferences_registry


class TournamentConfigIndexView(SuperuserRequiredMixin, TournamentMixin, TemplateView):
    template_name = "preferences_index.html"

    def get_context_data(self, **kwargs):
        preset_options = []

        # Get a list of classes from presets
        for name, obj in inspect.getmembers(presets):
            if inspect.isclass(obj):
                test = obj()
                # Check if each object should be shown
                if test.show_in_list:
                    obj.slugified_name = slugify(name)
                    obj.description = inspect.getdoc(test)
                    preset_options.append(obj)

        kwargs["presets"] = preset_options
        return super().get_context_data(**kwargs)


class TournamentPreferenceFormView(SuperuserRequiredMixin, LogActionMixin, TournamentMixin, PreferenceFormView):
    registry = tournament_preferences_registry
    section = None
    template_name = "preferences_section_set.html"

    action_log_type = ActionLogEntry.ACTION_TYPE_OPTIONS_EDIT

    def form_valid(self, *args, **kwargs):
        messages.success(self.request, "Tournament option saved.")
        return super().form_valid(*args, **kwargs)

    def get_success_url(self):
        return reverse_tournament('options-tournament-index', self.get_tournament())

    def get_form_class(self, *args, **kwargs):
        tournament = self.get_tournament()
        form_class = tournament_preference_form_builder(instance=tournament, section=self.section)
        return form_class


class TournamentPreferencesView(SuperuserRequiredMixin, TournamentMixin, TemplateView):

    def pname(self):
        return self.kwargs["preset_name"]

    def get_selected_preset(self):
        preset_name = self.kwargs["preset_name"]
        # Get a list of classes from presets
        preset_classes = inspect.getmembers(presets)
        # Retrieve the class that matches the name
        selected_preset = [item for item in preset_classes if slugify(item[0]) == preset_name]
        return selected_preset

    def get_preferences_data(self, selected_preset):
        # Grab the registry of the preferences
        registry = tournament_preferences_registry
        preset_preferences = []
        # Create an instance of the class and iterate over its properties for the UI
        for key, value in selected_preset[0][1]().__dict__.items():
            if key is not 'name' and key is not 'show_in_list':
                # Lookup the base object
                preset_object = registry[key.split('__')[0]][key.split('__')[1]]
                preset_preferences.append({
                    'name': preset_object.verbose_name,
                    'current_value': self.request.tournament.preferences[key],
                    'new_value': value,
                    'help_text': preset_object.help_text
                })
                self.get_tournament().preferences[key] = value
        return preset_preferences


class ConfirmTournamentPreferencesView(TournamentPreferencesView):
    template_name = "preferences_presets_confirm.html"

    def get_context_data(self, **kwargs):
        selected_preset = self.get_selected_preset()
        if len(selected_preset) == 0:
            raise Http404("Preset {!r} not found.".format(self.pname()))

        preset_preferences = self.get_preferences_data(selected_preset)

        kwargs["preset_title"] = selected_preset[0][1]().name
        kwargs["preset_name"] = self.pname()
        kwargs["preset_preferences"] = preset_preferences
        return super().get_context_data(**kwargs)


class ApplyTournamentPreferencesView(TournamentPreferencesView):

    template_name = "preferences_presets_apply.html"

    def get_context_data(self, **kwargs):
        selected_preset = self.get_selected_preset()
        if len(selected_preset) == 0:
            raise Http404("Preset {!r} not found.".format(self.pname()))

        preset_preferences = self.get_preferences_data(selected_preset)

        t = self.get_tournament()
        ActionLogEntry.objects.log(type=ActionLogEntry.ACTION_TYPE_OPTIONS_EDIT,
                user=self.request.user, tournament=t, content_object=t)
        messages.success(self.request, "Tournament option saved.")

        kwargs["preset_title"] = selected_preset[0][1]().name
        kwargs["preferences"] = preset_preferences
        return super().get_context_data(**kwargs)
