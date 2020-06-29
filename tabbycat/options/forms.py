from dynamic_preferences.forms import GlobalPreferenceForm, preference_form_builder, PreferenceForm
from dynamic_preferences.registries import global_preferences_registry

from .preferences import tournament_preferences_registry


class TournamentPreferenceForm(PreferenceForm):
    registry = tournament_preferences_registry


def tournament_preference_form_builder(instance, preferences=[], **kwargs):
    if kwargs.get('section') in [str(s) for s in global_preferences_registry.sections()]:
        # Check for global preferences
        return preference_form_builder(GlobalPreferenceForm, preferences, **kwargs)

    return preference_form_builder(
        TournamentPreferenceForm, preferences, model={'instance': instance}, **kwargs)
