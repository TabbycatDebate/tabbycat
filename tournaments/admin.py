from django.contrib import admin

from .models import Tournament, Division, Round


# ==============================================================================
# Tournament
# ==============================================================================

class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'seq', 'emoji', 'short_name', 'current_round')
    ordering = ('seq', )


admin.site.register(Tournament, TournamentAdmin)


# ==============================================================================
# Division
# ==============================================================================

class DivisionAdmin(admin.ModelAdmin):
    list_display = ('name', 'tournament', 'venue_group', 'time_slot')
    list_filter = ('tournament', 'venue_group')
    search_fields = ('name', )
    ordering = ('tournament', 'name', )


admin.site.register(Division, DivisionAdmin)


# ==============================================================================
# Round
# ==============================================================================

class RoundAdmin(admin.ModelAdmin):
    list_display = ('name', 'tournament', 'seq', 'abbreviation', 'stage',
                    'draw_type', 'draw_status', 'feedback_weight', 'silent',
                    'motions_released', 'starts_at')
    list_filter = ('tournament', )
    search_fields = ('name', 'seq', 'abbreviation', 'stage', 'draw_type',
                     'draw_status')


admin.site.register(Round, RoundAdmin)
