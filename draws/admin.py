from django.contrib import admin
from django import forms

from . import models
from debate.models import Speaker, Team, DebateAdjudicator

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
    model = Speaker
    fields = ('name', 'novice', 'gender')

class TeamPositionAllocationInline(admin.TabularInline):
    model = models.TeamPositionAllocation

class TeamVenuePreferenceInline(admin.TabularInline):
    model = models.TeamVenuePreference
    extra = 6

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
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

admin.site.register(Team, TeamAdmin)

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
    model = DebateAdjudicator
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

