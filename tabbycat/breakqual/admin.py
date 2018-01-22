from django.contrib import admin

from .models import BreakCategory, BreakingTeam


# ==============================================================================
# Break Catergories
# ==============================================================================

@admin.register(BreakCategory)
class BreakCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'seq', 'tournament', 'break_size',
                    'priority', 'is_general', 'rule')
    list_filter = ('tournament', )
    ordering = ('tournament', 'seq')


# ==============================================================================
# Breaking Teams
# ==============================================================================

@admin.register(BreakingTeam)
class BreakingTeamAdmin(admin.ModelAdmin):
    list_display = ('break_category', 'team', 'rank', 'break_rank', 'remark')
    list_filter = ('break_category__tournament', 'break_category')
    search_fields = ('team__short_name', 'team__long_name',
                     'team__institution__name', 'team__institution__code')
    ordering = ('break_category', )
