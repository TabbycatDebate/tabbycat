from django.db import models
from django.utils.translation import gettext_lazy as _
from dynamic_preferences.models import PerInstancePreferenceModel

from tournaments.models import Tournament

from .registries import tournament_preferences_registry


class TournamentPreferenceModel(PerInstancePreferenceModel):

    instance = models.ForeignKey(Tournament, models.CASCADE, related_name="preferences",
        verbose_name=_("instance"))
    registry = tournament_preferences_registry

    class Meta(PerInstancePreferenceModel.Meta):
        app_label = "options"
        verbose_name = _("tournament preference")
        verbose_name_plural = _("tournament preferences")
