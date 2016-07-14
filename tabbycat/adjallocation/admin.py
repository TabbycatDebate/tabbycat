from django.contrib import admin

from .models import AdjudicatorAdjudicatorConflict, AdjudicatorConflict
from .models import AdjudicatorInstitutionConflict
from .models import DebateAdjudicator


# ==============================================================================
# Debate Adjudicators
# ==============================================================================

class DebateAdjudicatorAdmin(admin.ModelAdmin):
    list_display = ('debate', 'adjudicator', 'type')
    search_fields = ('adjudicator__name', 'type')
    raw_id_fields = ('debate',)

admin.site.register(DebateAdjudicator, DebateAdjudicatorAdmin)


# ==============================================================================
# Adjudicator Team Conflicts
# ==============================================================================

class AdjudicatorConflictAdmin(admin.ModelAdmin):
    list_display = ('adjudicator', 'team')
    search_fields = ('adjudicator__name', 'team__short_name', 'team__long_name')

admin.site.register(AdjudicatorConflict, AdjudicatorConflictAdmin)


# ==============================================================================
# Adjudicator Adjudicator Conflicts
# ==============================================================================

class AdjudicatorAdjudicatorConflictAdmin(admin.ModelAdmin):
    list_display = ('adjudicator', 'conflict_adjudicator')
    search_fields = ('adjudicator__name', 'conflict_adjudicator__name')

admin.site.register(AdjudicatorAdjudicatorConflict,
                    AdjudicatorAdjudicatorConflictAdmin)


# ==============================================================================
# AdjudicatorConflict
# ==============================================================================

class AdjudicatorInstitutionConflictAdmin(admin.ModelAdmin):
    list_display = ('adjudicator', 'institution')
    search_fields = ('adjudicator__name', 'institution__name')

admin.site.register(AdjudicatorInstitutionConflict,
                    AdjudicatorInstitutionConflictAdmin)
