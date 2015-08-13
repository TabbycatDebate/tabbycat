from django.contrib import admin
from django import forms

import debate.models as models
import feedback.models as fm

from allocations.models import AdjudicatorConflict, AdjudicatorAdjudicatorConflict, AdjudicatorInstitutionConflict

# ==============================================================================
# Tournament
# ==============================================================================

class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name','short_name','current_round')
    ordering = ('name',)

admin.site.register(models.Tournament,TournamentAdmin)

# ==============================================================================
# Institution
# ==============================================================================

class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('name','code','abbreviation','region')
    ordering = ('name',)
    search_fields = ('name',)

admin.site.register(models.Institution, InstitutionAdmin)

# ==============================================================================
# Region
# ==============================================================================

class RegionAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.Region, RegionAdmin)


# ==============================================================================
# Speaker
# ==============================================================================

class SpeakerAdmin(admin.ModelAdmin):
    list_display = ('name', 'team', 'novice')
    search_fields = ('name',)
    raw_id_fields = ('team',)

admin.site.register(models.Speaker, SpeakerAdmin)

# ==============================================================================
# Division
# ==============================================================================

class DivisionAdmin(admin.ModelAdmin):
    list_display = ('name', 'tournament', 'venue_group','time_slot')
    list_filter = ('tournament', 'venue_group')
    search_fields = ('name',)
    ordering = ('tournament', 'name',)

admin.site.register(models.Division, DivisionAdmin)

# ==============================================================================
# Adjudicator
# ==============================================================================

class AdjudicatorConflictInline(admin.TabularInline):
    model = AdjudicatorConflict
    extra = 1
    verbose_name_plural = "Adjudicator team conflicts"

class AdjudicatorAdjudicatorConflictInline(admin.TabularInline):
    model = AdjudicatorAdjudicatorConflict
    fk_name = "adjudicator"
    extra = 1
    raw_id_fields = ('conflict_adjudicator',)

class AdjudicatorInstitutionConflictInline(admin.TabularInline):
    model = AdjudicatorInstitutionConflict
    extra = 1

class AdjudicatorTestScoreHistoryInline(admin.TabularInline):
    model = fm.AdjudicatorTestScoreHistory
    extra = 1

class AdjudicatorForm(forms.ModelForm):
    class Meta:
        model = models.Adjudicator
        fields = '__all__'

    def clean_url_key(self):
        return self.cleaned_data['url_key'] or None # So that the url key can be unique and also set to blank


class AdjudicatorAdmin(admin.ModelAdmin):
    form = AdjudicatorForm
    list_display = ('name', 'institution', 'tournament','novice','independent')
    search_fields = ('name', 'tournament__name', 'institution__name', 'institution__code',)
    list_filter = ('tournament', 'name')
    inlines = (AdjudicatorConflictInline,AdjudicatorInstitutionConflictInline, AdjudicatorAdjudicatorConflictInline, AdjudicatorTestScoreHistoryInline)

admin.site.register(models.Adjudicator, AdjudicatorAdmin)

# ==============================================================================
# Round
# ==============================================================================

class RoundAdmin(admin.ModelAdmin):
    list_display = ('name', 'tournament', 'seq', 'abbreviation', 'stage', 'draw_type', 'draw_status', 'feedback_weight', 'silent', 'motions_released', 'starts_at')
    list_filter = ('tournament',)
    search_fields = ('name', 'seq', 'abbreviation', 'stage', 'draw_type', 'draw_status')

admin.site.register(models.Round, RoundAdmin)


