import inspect

from django.http import Http404
from django.utils.text import slugify
from django.views.generic import TemplateView
from dynamic_preferences.views import PreferenceFormView

from actionlog.mixins import LogActionMixin
from actionlog.models import ActionLogEntry
from tournaments.mixins import TournamentMixin
from utils.mixins import SuperuserRequiredMixin
from utils.views import *
from utils.misc import reverse_tournament

from . import presets
from .forms import tournament_preference_form_builder
from .dynamic_preferences_registry import tournament_preferences_registry


@admin_required
@tournament_view
def tournament_config_index(request, t):
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

    return render(request, 'preferences_index.html', dict(presets=preset_options))


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


@admin_required
@tournament_view
def tournament_preference_confirm(request, t, preset_name):
    # Grab the registry of the preferences
    registry = tournament_preferences_registry
    # Get a list of classes from presets
    preset_classes = inspect.getmembers(presets)
    # Retrieve the class that matches the name
    selected_preset = [item for item in preset_classes if slugify(item[0]) == preset_name]

    if len(selected_preset) == 0:
        raise Http404("Preset {!r} not found.".format(preset_name))

    preset_preferences = []

    # Create an instance of the class and iterate over its properties for the UI
    for key, value in selected_preset[0][1]().__dict__.items():
        # Lookup the base object
        if key is not 'name' and key is not 'show_in_list':
            preset_object = registry[key.split('__')[0]][key.split('__')[1]]
            preset_preferences.append({
                'name': preset_object.verbose_name,
                'current_value': request.tournament.preferences[key],
                'new_value': value,
                'help_text': preset_object.help_text
            })

    context = {}
    context['preset_title'] = selected_preset[0][1]().name
    context['preset_name'] = preset_name
    context['preferences'] = preset_preferences

    return render(request, 'preferences_presets_confirm.html', context)


@admin_required
@tournament_view
def tournament_preference_apply(request, t, preset_name):

    registry = tournament_preferences_registry
    preset_classes = inspect.getmembers(presets)
    selected_preset = [item for item in preset_classes if slugify(item[0]) == preset_name]

    preset_preferences = []
    # Create an instance of the class and iterate over its properties for the UI
    for key, value in selected_preset[0][1]().__dict__.items():
        if key is not 'name' and key is not 'show_in_list':
            # Lookup the base object
            preset_object = registry[key.split('__')[0]][key.split('__')[1]]
            preset_preferences.append({
                'name': preset_object.verbose_name,
                'current_value': request.tournament.preferences[key],
                'new_value': value,
                'help_text': preset_object.help_text
            })
            t.preferences[key] = value

    ActionLogEntry.objects.log(type=ActionLogEntry.ACTION_TYPE_OPTIONS_EDIT, user=request.user, tournament=t)
    messages.success(request, "Tournament option saved.")

    context = {}
    context['preset_title'] = selected_preset[0][1]().name
    context['preferences'] = preset_preferences

    return render(request, 'preferences_presets_apply.html', context)


class TournamentPreferenceApplyView(TemplateView):

    preset = None
    template_name = "preferences_presets_apply.html"
