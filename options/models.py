from django.db import models
from tournaments.models import Tournament
from dynamic_preferences.models import PerInstancePreferenceModel

class TournamentPreferenceModel(PerInstancePreferenceModel):

    instance = models.ForeignKey(Tournament)

    class Meta(PerInstancePreferenceModel.Meta):
        app_label = 'dynamic_preferences' # Can't change this
        verbose_name = "Tournament Preference"
        verbose_name_plural = "Tournament Preferencess"
