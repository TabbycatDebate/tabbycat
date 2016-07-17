from django.contrib import admin

from .models import Round, Tournament


# ==============================================================================
# Tournament
# ==============================================================================

class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'seq', 'emoji', 'short_name', 'current_round')
    ordering = ('seq', )


admin.site.register(Tournament, TournamentAdmin)


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
