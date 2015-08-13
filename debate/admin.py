from django.contrib import admin
from django import forms

import debate.models as models
import feedback.models as fm

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
# DebateTeam
# ==============================================================================

_dt_round = lambda o: o.debate.round.abbreviation
_dt_round.short_description = 'Round'
_dt_tournament = lambda o: o.debate.round.tournament
_dt_tournament.short_description = 'Tournament'

class DebateTeamAdmin(admin.ModelAdmin):
    list_display = ('team', _dt_tournament, _dt_round, 'position')
    search_fields = ('team',)
    raw_id_fields = ('debate','team',)

    def get_queryset(self, request):
        return super(DebateTeamAdmin, self).get_queryset(request).select_related('debate__round', 'debate__round__tournament')


admin.site.register(models.DebateTeam, DebateTeamAdmin)

# ==============================================================================
# Team
# ==============================================================================

class SpeakerInline(admin.TabularInline):
    model = models.Speaker
    fields = ('name', 'novice', 'gender')

class TeamPositionAllocationInline(admin.TabularInline):
    model = models.TeamPositionAllocation

class TeamVenuePreferenceInline(admin.TabularInline):
    model = models.TeamVenuePreference
    extra = 6

class TeamForm(forms.ModelForm):
    class Meta:
        model = models.Team
        fields = '__all__'

    def clean_url_key(self):
        return self.cleaned_data['url_key'] or None # So that the url key can be unique and also set to blank

class TeamAdmin(admin.ModelAdmin):
    form = TeamForm
    list_display = ('long_name','short_reference','institution', 'division', 'tournament')
    search_fields = ('reference', 'short_reference', 'institution__name', 'institution__code', 'tournament__name')
    list_filter = ('tournament', 'division', 'institution', 'break_categories')
    inlines = (SpeakerInline, TeamPositionAllocationInline, TeamVenuePreferenceInline)
    raw_id_fields = ('division',)

    def get_queryset(self, request):
        return super(TeamAdmin, self).get_queryset(request).prefetch_related('institution','division')

admin.site.register(models.Team, TeamAdmin)

# ==============================================================================
# TeamVenuePreference
# ==============================================================================

class TeamVenuePreferenceAdmin(admin.ModelAdmin):
    list_display = ('team', 'venue_group', 'priority')
    search_fields = ('team','venue_group', 'priority')
    list_filter = ('team','venue_group', 'priority')
    raw_id_fields = ('team',)

admin.site.register(models.TeamVenuePreference, TeamVenuePreferenceAdmin)

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
    model = models.AdjudicatorConflict
    extra = 1
    verbose_name_plural = "Adjudicator team conflicts"

class AdjudicatorAdjudicatorConflictInline(admin.TabularInline):
    model = models.AdjudicatorAdjudicatorConflict
    fk_name = "adjudicator"
    extra = 1
    raw_id_fields = ('conflict_adjudicator',)

class AdjudicatorInstitutionConflictInline(admin.TabularInline):
    model = models.AdjudicatorInstitutionConflict
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
# Debate
# ==============================================================================

def make_result_status_none(modeladmin, request, queryset):
    queryset.update(result_status=models.Debate.STATUS_NONE)

def make_result_status_postponed(modeladmin, request, queryset):
    queryset.update(result_status=models.Debate.STATUS_POSTPONED)

def make_result_status_draft(modeladmin, request, queryset):
    queryset.update(result_status=models.Debate.STATUS_DRAFT)

def make_result_status_confirmed(modeladmin, request, queryset):
    queryset.update(result_status=models.Debate.STATUS_CONFIRMED)

class DebateTeamInline(admin.TabularInline):
    model = models.DebateTeam
    extra = 1
    raw_id_fields = ('team',)

class DebateAdjudicatorInline(admin.TabularInline):
    model = models.DebateAdjudicator
    extra = 1

class DebateAdmin(admin.ModelAdmin):
    list_display = ('id','round','bracket','aff_team', 'neg_team','result_status')
    list_filter = ('round__tournament','round', 'division')
    inlines = (DebateTeamInline, DebateAdjudicatorInline)
    raw_id_fields = ('venue','division')

    def get_queryset(self, request):
        return super(DebateAdmin, self).get_queryset(request).select_related(
            'round__tournament','division__tournament','venue__group'
        )

    actions = list()
    for value, verbose_name in models.Debate.STATUS_CHOICES:
        def _make_set_result_status(value, verbose_name):
            def _set_result_status(modeladmin, request, queryset):
                count = queryset.update(result_status=value)
            _set_result_status.__name__ = "set_result_status_%s" % verbose_name.lower() # so that they look different to DebateAdmin
            _set_result_status.short_description = "Set result status to %s" % verbose_name.lower()
            return _set_result_status
        actions.append(_make_set_result_status(value, verbose_name))
    del value, verbose_name # for fail-fast

admin.site.register(models.Debate, DebateAdmin)

# ==============================================================================
# Round
# ==============================================================================

class RoundAdmin(admin.ModelAdmin):
    list_display = ('name', 'tournament', 'seq', 'abbreviation', 'stage', 'draw_type', 'draw_status', 'feedback_weight', 'silent', 'motions_released', 'starts_at')
    list_filter = ('tournament',)
    search_fields = ('name', 'seq', 'abbreviation', 'stage', 'draw_type', 'draw_status')

admin.site.register(models.Round, RoundAdmin)

# ==============================================================================
# DebateAdjudicator
# ==============================================================================

class DebateAdjudicatorAdmin(admin.ModelAdmin):
    list_display = ('debate', 'adjudicator', 'type')
    search_fields = ('adjudicator__name', 'type')
    raw_id_fields = ('debate',)

admin.site.register(models.DebateAdjudicator, DebateAdjudicatorAdmin)

