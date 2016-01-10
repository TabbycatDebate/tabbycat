from django.contrib import admin

from dynamic_preferences.admin import PerInstancePreferenceAdmin

from options.dynamic_preferences_registry import TournamentPreferenceModel


# ==============================================================================
# Preferences
# ==============================================================================

class TournamentPreferenceAdmin(PerInstancePreferenceAdmin):
  pass

admin.site.register(TournamentPreferenceModel, TournamentPreferenceAdmin)

from dynamic_preferences.models import GlobalPreferenceModel, UserPreferenceModel
admin.site.unregister(GlobalPreferenceModel)
admin.site.unregister(UserPreferenceModel)