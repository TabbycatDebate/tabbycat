from django.apps import AppConfig
from dynamic_preferences.registries import preference_models

from .registries import tournament_preferences_registry


class OptionsConfig(AppConfig):
    name = 'options'
    verbose_name = "Tournament Options"

    def ready(self):
        TournamentPreferenceModel = self.get_model('TournamentPreferenceModel')  # noqa: N806
        preference_models.register(TournamentPreferenceModel, tournament_preferences_registry)
