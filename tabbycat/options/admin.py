from django.contrib import admin

from dynamic_preferences.admin import PerInstancePreferenceAdmin
from dynamic_preferences.models import GlobalPreferenceModel, UserPreferenceModel

from .models import TournamentPreferenceModel


# ==============================================================================
# Preferences
# ==============================================================================

class TournamentPreferenceAdmin(PerInstancePreferenceAdmin):
    pass


admin.site.register(TournamentPreferenceModel, TournamentPreferenceAdmin)
admin.site.unregister(GlobalPreferenceModel)
admin.site.unregister(UserPreferenceModel)
