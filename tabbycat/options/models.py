from django.db import models
from django.utils.translation import gettext_lazy as _
from dynamic_preferences.models import PerInstancePreferenceModel
from dynamic_preferences.registries import PerInstancePreferenceRegistry, preference_models

from tournaments.models import Tournament

tournament_preferences_registry = PerInstancePreferenceRegistry()


class TournamentPreferenceModel(PerInstancePreferenceModel):

    instance = models.ForeignKey(Tournament, models.CASCADE, related_name="preferences",
        verbose_name=_("instance"))
    registry = tournament_preferences_registry

    class Meta(PerInstancePreferenceModel.Meta):
        app_label = "options"
        verbose_name = _("tournament preference")
        verbose_name_plural = _("tournament preferences")


preference_models.register(TournamentPreferenceModel,
                           tournament_preferences_registry)
