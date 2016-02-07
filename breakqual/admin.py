from django.contrib import admin

from .models import BreakCategory, BreakingTeam

# ==============================================================================
# Break Catergories
# ==============================================================================

class BreakCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'seq', 'tournament', 'break_size',
                    'priority', 'is_general', 'institution_cap')
    list_filter = ('tournament', )
    ordering = ('tournament', 'seq')


admin.site.register(BreakCategory, BreakCategoryAdmin)

# ==============================================================================
# Breaking Teams
# ==============================================================================

class BreakingTeamAdmin(admin.ModelAdmin):
    list_display = ('break_category', 'team', 'rank', 'break_rank', 'remark')
    list_filter = ('break_category__tournament', 'break_category')
    search_fields = ('team', )
    ordering = ('break_category', )


admin.site.register(BreakingTeam, BreakingTeamAdmin)
