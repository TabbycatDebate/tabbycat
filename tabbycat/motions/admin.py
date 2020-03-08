from django.contrib import admin

from utils.admin import TabbycatModelAdminFieldsMixin

from .models import DebateTeamMotionPreference, Motion


# ==============================================================================
# Motions
# ==============================================================================

@admin.register(Motion)
class MotionAdmin(TabbycatModelAdminFieldsMixin, admin.ModelAdmin):
    list_display = ('reference', 'round', 'seq', 'get_tournament')
    list_filter = ('round__tournament', 'round')
    ordering = ('round',)


@admin.register(DebateTeamMotionPreference)
class DebateTeamMotionPreferenceAdmin(TabbycatModelAdminFieldsMixin, admin.ModelAdmin):
    list_display = ('ballot_submission', 'get_confirmed', 'get_team',
                    'get_team_side', 'preference', 'get_motion_ref')
    search_fields = ('motion__reference',)
