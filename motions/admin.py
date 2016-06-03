from django.contrib import admin

from .models import Motion, DebateTeamMotionPreference

from utils.admin import BaseModelAdmin


# ==============================================================================
# Motions
# ==============================================================================

class MotionAdmin(admin.ModelAdmin, BaseModelAdmin):
    list_display = ('reference', 'round', 'seq', 'get_tournament')
    list_filter = ('round', 'divisions')

admin.site.register(Motion, MotionAdmin)


class DebateTeamMotionPreferenceAdmin(admin.ModelAdmin, BaseModelAdmin):
    list_display = ('ballot_submission', 'get_confirmed', 'get_team',
                    'get_team_position', 'preference', 'get_motion_ref')

admin.site.register(DebateTeamMotionPreference, DebateTeamMotionPreferenceAdmin)
