from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
from dynamic_preferences.registries import preference_models

from .registries import tournament_preferences_registry


class OptionsConfig(AppConfig):
    name = 'options'
    verbose_name = _("Tournament Options")

    def ready(self):
        TournamentPreferenceModel = self.get_model('TournamentPreferenceModel')  # noqa: N806
        preference_models.register(TournamentPreferenceModel, tournament_preferences_registry)
