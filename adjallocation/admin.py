from django.contrib import admin

from .models import DebateAdjudicator

# ==============================================================================
# Debate Adjudicators 
# ==============================================================================

class DebateAdjudicatorAdmin(admin.ModelAdmin):
    list_display = ('debate', 'adjudicator', 'type')
    search_fields = ('adjudicator__name', 'type')
    raw_id_fields = ('debate',)

admin.site.register(DebateAdjudicator, DebateAdjudicatorAdmin)
