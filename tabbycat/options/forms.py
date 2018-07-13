from dynamic_preferences.forms import preference_form_builder, PreferenceForm

from .preferences import tournament_preferences_registry, global_preferences_registry


class TournamentPreferenceForm(PreferenceForm):
    registry = tournament_preferences_registry


class GlobalPreferenceForm(PreferenceForm):
    registry = global_preferences_registry


def tournament_preference_form_builder(instance, preferences=[], **kwargs):
    prefs_are_global = [pref in global_preferences_registry for pref in preferences]

    section_is_global = None
    if 'section' in kwargs:
        section = kwargs['section']
        for section_obj in global_preferences_registry.section_objects:
            section_is_global = section in str(section_obj)
            if section_is_global:
                break

    if (all(prefs_are_global) and prefs_are_global) or section_is_global is True:
        return preference_form_builder(GlobalPreferenceForm, preferences, **kwargs)
    elif (not any(prefs_are_global) and prefs_are_global) or section_is_global is False:
        return preference_form_builder(
            TournamentPreferenceForm, preferences, model={'instance': instance}, **kwargs)
    else:
        return None