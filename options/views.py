from django import forms
from django.views.generic import TemplateView
from actionlog.models import ActionLogEntry
from utils.views import *
from dynamic_preferences.views import PreferenceFormView
from django.utils.text import slugify

import options.presets
import inspect

@admin_required
@tournament_view
def tournament_config_index(request, t):
    preset_options = []

    # Get a list of classes from options.presets
    for name, obj in inspect.getmembers(options.presets):
        if inspect.isclass(obj):
            test = obj()
            # Check if each object should be shown
            if test.show_in_list:
                obj.slugified_name = slugify(name)
                preset_options.append(obj)

    return r2r(request, 'preferences_index.html', dict(presets=preset_options))


from options.dynamic_preferences_registry import tournament_preferences_registry
from dynamic_preferences.forms import preference_form_builder, PreferenceForm

class TournamentPreferenceForm(PreferenceForm):
    registry = tournament_preferences_registry


def tournament_preference_form_builder(instance, preferences=[], **kwargs):
    return preference_form_builder(TournamentPreferenceForm, preferences, model={'instance': instance}, **kwargs)


class TournamentPreferenceFormView(PreferenceFormView):
    registry = tournament_preferences_registry
    section = None
    template_name = "preferences_section_set.html"

    def get_form_class(self, *args, **kwargs):
        form_class = tournament_preference_form_builder(instance=self.request.tournament, section=self.section)
        return form_class


@admin_required
@tournament_view
def tournament_preference_confirm(request, t, preset_name):
    # Grab the registry of the preferences
    registry = tournament_preferences_registry
    # Get a list of classes from options.presets
    preset_classes = inspect.getmembers(options.presets)
    # Retrieve the class that matches the name
    selected_preset = [item for item in preset_classes if slugify(item[0]) == preset_name]

    preset_preferences = []

    # Create an instance of the class and iterate over its properties for the UI
    for key, value in selected_preset[0][1]().__dict__.items():
        # Lookup the base object
        if key is not 'name' and key is not 'show_in_list':
            preset_object = registry[key.split('__')[0]][key.split('__')[1]]
            preset_preferences.append({
                'name': preset_object.verbose_name,
                'current_value': request.tournament.preferences[key],
                'new_value': value[0],
                'help_text': preset_object.help_text
            })

    context = {}
    context['preset_title'] = selected_preset[0][1]().name
    context['preset_name'] = preset_name
    context['preferences'] = preset_preferences


    return r2r(request, 'preferences_presets_confirm.html', context)


@admin_required
@tournament_view
def tournament_preference_apply(request, t, preset_name):

    registry = tournament_preferences_registry
    preset_classes = inspect.getmembers(options.presets)
    selected_preset = [item for item in preset_classes if slugify(item[0]) == preset_name]

    preset_preferences = []
    # Create an instance of the class and iterate over its properties for the UI
    for key, value in selected_preset[0][1]().__dict__.items():
        if key is not 'name' and key is not 'show_in_list':
            # Lookup the base object
            print(str(key),str(value[0]))
            preset_object = registry[key.split('__')[0]][key.split('__')[1]]
            preset_preferences.append({
                'name': preset_object.verbose_name,
                'current_value': request.tournament.preferences[key],
                'new_value': value[0],
                'help_text': preset_object.help_text
            })
            t.preferences[key] = value[0]

    context = {}
    context['preset_title'] = selected_preset[0][1]().name
    context['preferences'] = preset_preferences


    return r2r(request, 'preferences_presets_apply.html', context)


class TournamentPreferenceApplyView(TemplateView):

    preset = None
    template_name = "preferences_presets_apply.html"

