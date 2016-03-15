from django.db import models
from tournaments.models import Tournament
from dynamic_preferences.models import PerInstancePreferenceModel
from dynamic_preferences.registries import PerInstancePreferenceRegistry, preference_models

tournament_preferences_registry = PerInstancePreferenceRegistry()


class TournamentPreferenceModel(PerInstancePreferenceModel):

    instance = models.ForeignKey(Tournament, related_name="preferences")
    registry = tournament_preferences_registry

    class Meta(PerInstancePreferenceModel.Meta):
        app_label = "options"
        verbose_name = "tournament preference"


preference_models.register(TournamentPreferenceModel,
                           tournament_preferences_registry)
