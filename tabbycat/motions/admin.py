from django.contrib import admin

from utils.admin import ModelAdmin, TabbycatModelAdminFieldsMixin

from .models import DebateTeamMotionPreference, Motion, RoundMotion


# ==============================================================================
# Motions
# ==============================================================================

@admin.register(Motion)
class MotionAdmin(TabbycatModelAdminFieldsMixin, ModelAdmin):
    list_display = ('reference', 'text')
    list_filter = ('rounds',)


@admin.register(DebateTeamMotionPreference)
class DebateTeamMotionPreferenceAdmin(TabbycatModelAdminFieldsMixin, ModelAdmin):
    list_display = ('ballot_submission', 'get_confirmed', 'get_team',
                    'get_team_side', 'preference', 'get_motion_ref')
    search_fields = ('motion__reference',)


@admin.register(RoundMotion)
class RoundMotionAdmin(TabbycatModelAdminFieldsMixin, ModelAdmin):
    list_display = ('seq', 'round', 'motion')
    list_filter = ('round', 'motion')
    ordering = ('round__seq', 'seq')
