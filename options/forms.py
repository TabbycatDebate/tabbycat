from dynamic_preferences.forms import preference_form_builder, PreferenceForm

from .dynamic_preferences_registry import tournament_preferences_registry

class TournamentPreferenceForm(PreferenceForm):
    registry = tournament_preferences_registry


def tournament_preference_form_builder(instance, preferences=[], **kwargs):
    return preference_form_builder(TournamentPreferenceForm, preferences, model={'instance': instance}, **kwargs)


