from django.contrib import admin
from django import forms

from .models import Region, Institution, Speaker, Adjudicator, Team
from adjallocation.models import AdjudicatorConflict, AdjudicatorAdjudicatorConflict, AdjudicatorInstitutionConflict
from adjfeedback.models import AdjudicatorTestScoreHistory

# ==============================================================================
# Region
# ==============================================================================

class RegionAdmin(admin.ModelAdmin):
    pass


admin.site.register(Region, RegionAdmin)

# ==============================================================================
# Institution
# ==============================================================================

class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'abbreviation', 'region')
    ordering = ('name', )
    search_fields = ('name', )


admin.site.register(Institution, InstitutionAdmin)

# ==============================================================================
# Speaker
# ==============================================================================

class SpeakerAdmin(admin.ModelAdmin):
    list_display = ('name', 'team', 'novice')
    search_fields = ('name', )
    raw_id_fields = ('team', )


admin.site.register(Speaker, SpeakerAdmin)

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
    raw_id_fields = ('conflict_adjudicator', )


class AdjudicatorInstitutionConflictInline(admin.TabularInline):
    model = AdjudicatorInstitutionConflict
    extra = 1


class AdjudicatorTestScoreHistoryInline(admin.TabularInline):
    model = AdjudicatorTestScoreHistory
    extra = 1


class AdjudicatorForm(forms.ModelForm):
    class Meta:
        model = Adjudicator
        fields = '__all__'

    def clean_url_key(self):
        return self.cleaned_data[
            'url_key'] or None  # So that the url key can be unique and also set to blank


class AdjudicatorAdmin(admin.ModelAdmin):
    form = AdjudicatorForm
    list_display = ('name', 'institution', 'tournament', 'novice',
                    'independent')
    search_fields = ('name',
                     'tournament__name',
                     'institution__name',
                     'institution__code', )
    list_filter = ('tournament', 'name')
    inlines = (AdjudicatorConflictInline, AdjudicatorInstitutionConflictInline,
               AdjudicatorAdjudicatorConflictInline,
               AdjudicatorTestScoreHistoryInline)


admin.site.register(Adjudicator, AdjudicatorAdmin)
