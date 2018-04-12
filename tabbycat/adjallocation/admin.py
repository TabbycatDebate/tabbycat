from django.contrib import admin

from .models import (AdjudicatorAdjudicatorConflict, AdjudicatorConflict,
                     AdjudicatorInstitutionConflict, DebateAdjudicator)


# ==============================================================================
# Debate Adjudicators
# ==============================================================================

@admin.register(DebateAdjudicator)
class DebateAdjudicatorAdmin(admin.ModelAdmin):
    list_display = ('debate', 'adjudicator', 'type')
    search_fields = ('adjudicator__name', 'type')
    raw_id_fields = ('debate',)


# ==============================================================================
# Adjudicator Team Conflicts
# ==============================================================================

@admin.register(AdjudicatorConflict)
class AdjudicatorConflictAdmin(admin.ModelAdmin):
    list_display = ('adjudicator', 'team')
    list_select_related = ('adjudicator__institution', 'team__tournament')
    search_fields = ('adjudicator__name', 'team__short_name', 'team__long_name')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'team':
            kwargs['queryset'] = db_field.related_model.objects.select_related('tournament')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# ==============================================================================
# Adjudicator Adjudicator Conflicts
# ==============================================================================

@admin.register(AdjudicatorAdjudicatorConflict)
class AdjudicatorAdjudicatorConflictAdmin(admin.ModelAdmin):
    list_display = ('adjudicator', 'conflict_adjudicator')
    list_select_related = ('adjudicator__institution', 'conflict_adjudicator__institution')
    search_fields = ('adjudicator__name', 'conflict_adjudicator__name',
                     'adjudicator__institution', 'conflict_adjudicator__institution')


# ==============================================================================
# AdjudicatorConflict
# ==============================================================================

@admin.register(AdjudicatorInstitutionConflict)
class AdjudicatorInstitutionConflictAdmin(admin.ModelAdmin):
    list_display = ('adjudicator', 'institution')
    list_select_related = ('adjudicator__institution', 'institution')
    search_fields = ('adjudicator__name', 'institution__name')
