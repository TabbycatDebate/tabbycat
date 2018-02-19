from django.contrib import admin

from dynamic_preferences.admin import PerInstancePreferenceAdmin
from dynamic_preferences.models import GlobalPreferenceModel

from .models import TournamentPreferenceModel


# ==============================================================================
# Preferences
# ==============================================================================

@admin.register(TournamentPreferenceModel)
class TournamentPreferenceAdmin(PerInstancePreferenceAdmin):
    pass


admin.site.unregister(GlobalPreferenceModel)
