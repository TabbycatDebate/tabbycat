

# Config settings

from dynamic_preferences.types import BooleanPreference, StringPreference, Section
from dynamic_preferences import user_preferences_registry, global_preferences_registry


scoring = Section('scoring')

from tournaments.models import Tournament
from django.db import models
from dynamic_preferences.models import PerInstancePreferenceModel
class TournamentPreferenceModel(PerInstancePreferenceModel):

    instance = models.ForeignKey(Tournament)

    class Meta(PerInstancePreferenceModel.Meta):
        app_label = 'dynamic_preferences'
        verbose_name = "user preference"
        verbose_name_plural = "user preferences"



from dynamic_preferences.registries import PreferenceRegistry, PerInstancePreferenceRegistry
tournament_preferences_registry = PerInstancePreferenceRegistry()

from dynamic_preferences.registries import autodiscover, preference_models
preference_models.register(TournamentPreferenceModel, tournament_preferences_registry)



# now we declare a per-tournament preference
@tournament_preferences_registry.register
class CommentNotificationsEnabled(BooleanPreference):
    """Do you want to be notified on comment publication ?"""
    section = scoring
    name = 'comment_notifications_enabled'
    default = True


