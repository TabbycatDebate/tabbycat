from django.contrib import admin
from django import forms

import debate.models as models

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
    list_display = ('name','code','abbreviation')
    ordering = ('name',)
    search_fields = ('name',)

admin.site.register(models.Institution, InstitutionAdmin)

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
    fields = ('name', 'barcode_id', 'email', 'phone')

class TeamPositionAllocationInline(admin.TabularInline):
    model = models.TeamPositionAllocation

class TeamVenuePreferenceInline(admin.TabularInline):
    model = models.TeamVenuePreference
    extra = 6


class TeamAdmin(admin.ModelAdmin):
    list_display = ('long_name','short_reference','institution', 'division', 'tournament')
    search_fields = ('reference', 'short_reference', 'institution__name', 'institution__code', 'tournament__name')
    list_filter = ('tournament', 'division', 'institution')
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
    raw_id_fields = ('team',)

class AdjudicatorInstitutionConflictInline(admin.TabularInline):
    model = models.AdjudicatorInstitutionConflict
    extra = 1

class AdjudicatorTestScoreHistoryInline(admin.TabularInline):
    model = models.AdjudicatorTestScoreHistory
    extra = 1

class AdjudicatorAdmin(admin.ModelAdmin):
    list_display = ('name', 'institution', 'tournament','novice')
    search_fields = ('name', 'tournament__name', 'institution__name', 'institution__code',)
    list_filter = ('tournament', 'name')
    inlines = (AdjudicatorConflictInline,AdjudicatorInstitutionConflictInline, AdjudicatorTestScoreHistoryInline)

admin.site.register(models.Adjudicator, AdjudicatorAdmin)

# ==============================================================================
# AdjudicatorFeedback
# ==============================================================================

class AdjudicatorFeedbackAdmin(admin.ModelAdmin):
    list_display = ('adjudicator', 'source_adjudicator', 'source_team', 'confirmed', 'score', 'comments')
    search_fields = ('source_adjudicator__adjudicator__name', 'source_team__team__institution__code', 'source_team__team__reference', 'adjudicator__name', 'adjudicator__institution__code',)
    raw_id_fields = ('source_team',)

admin.site.register(models.AdjudicatorFeedback, AdjudicatorFeedbackAdmin)

# ==============================================================================
# VenueGroup
# ==============================================================================

class VenueGroupAdmin(admin.ModelAdmin):
    list_display = ('name','short_name','team_capacity')
    search_fields = ('name',)

admin.site.register(models.VenueGroup, VenueGroupAdmin)

# ==============================================================================
# Venue
# ==============================================================================

class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'group', 'priority', 'time','tournament')
    list_filter = ('group', 'priority', 'time','tournament')
    search_fields = ('name', 'time')

    def get_queryset(self, request):
        return super(VenueAdmin, self).get_queryset(request).select_related('group')

admin.site.register(models.Venue, VenueAdmin)

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

for value, verbose_name in models.Debate.STATUS_CHOICES:
    def _make_set_result_status(value, verbose_name):
        def _set_result_status(modeladmin, request, queryset):
            count = queryset.update(result_status=value)
        _set_result_status.__name__ = "set_result_status_%s" % verbose_name.lower() # so that they look different to DebateAdmin
        _set_result_status.short_description = "Set result status to %s" % verbose_name.lower()
        return _set_result_status
    DebateAdmin.actions.append(_make_set_result_status(value, verbose_name))
del value, verbose_name # for fail-fast

admin.site.register(models.Debate, DebateAdmin)

# ==============================================================================
# TeamScore
# ==============================================================================

_ts_round = lambda o: o.debate_team.debate.round.seq
_ts_round.short_description = 'Round'
_ts_team = lambda o: o.debate_team.team
_ts_team.short_description = 'Team'
class TeamScoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'ballot_submission', _ts_round, _ts_team, 'score')
    search_fields = ('debate_team__debate__round__seq',
                     'debate_team__team__reference', 'debate_team__team__institution__code')
    raw_id_fields = ('ballot_submission','debate_team')

admin.site.register(models.TeamScore, TeamScoreAdmin)

# ==============================================================================
# SpeakerScore
# ==============================================================================

_ss_speaker = lambda o: o.speaker.name
_ss_speaker.short_description = 'Speaker'

class SpeakerScoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'ballot_submission', _ts_round, _ts_team, 'position', _ss_speaker, 'score')
    search_fields = ('debate_team__debate__round__abbreviation',
                     'debate_team__team__reference', 'debate_team__team__institution__code',
                     'speaker__name')
    list_filter = ('score','debate_team__debate__round__abbreviation')
    raw_id_fields = ('debate_team','ballot_submission')

    def get_queryset(self, request):
        return super(SpeakerScoreAdmin, self).get_queryset(request).select_related(
            'debate_team__debate__round',
            'debate_team__team__institution','debate_team__team__tournament',
            'ballot_submission')

admin.site.register(models.SpeakerScore, SpeakerScoreAdmin)

# ==============================================================================
# SpeakerScoreByAdj
# ==============================================================================

_ssba_speaker = lambda o: models.SpeakerScore.objects.filter(debate_team=o.debate_team, position=o.position)[0].speaker.name
_ssba_speaker.short_description = 'Speaker'
_ssba_adj = lambda o: o.debate_adjudicator.adjudicator.name
_ssba_adj.short_description = 'Adjudicator'

class SpeakerScoreByAdjAdmin(admin.ModelAdmin):
    list_display = ('id', 'ballot_submission', _ts_round, _ssba_adj, _ts_team, 'position', _ssba_speaker, 'score')
    search_fields = ('debate_team__debate__round__seq',
                     'debate_team__team__reference', 'debate_team__team__institution__code',
                     'debate_adjudicator__adjudicator__name')
    list_filter = ('debate_team__debate__round__seq', 'debate_team__team__institution__code')
    raw_id_fields = ('debate_team','ballot_submission')
admin.site.register(models.SpeakerScoreByAdj, SpeakerScoreByAdjAdmin)

# ==============================================================================
# DebateTeamMotionPreference
# ==============================================================================

_dtmp_team_name =  lambda o: o.debate_team.team.short_name
_dtmp_team_name.short_description = 'Team'
_dtmp_position = lambda o: o.debate_team.position
_dtmp_position.short_description = 'Position'
_dtmp_motion = lambda o: o.motion.reference
_dtmp_motion.short_description = 'Motion'
_dtmp_confirmed = lambda o: o.ballot_submission.confirmed
_dtmp_confirmed.short_description = 'Confirmed'

class DebateTeamMotionPreferenceAdmin(admin.ModelAdmin):
    list_display = ('ballot_submission', _dtmp_confirmed, _dtmp_team_name, _dtmp_position, 'preference', _dtmp_motion)
admin.site.register(models.DebateTeamMotionPreference, DebateTeamMotionPreferenceAdmin)

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

# ==============================================================================
# Motion
# ==============================================================================

_m_tournament = lambda o: o.round.tournament
class MotionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'round','seq', _m_tournament)
    list_filter = ('round', 'divisions')

admin.site.register(models.Motion, MotionAdmin)

# ==============================================================================
# BallotSubmission
# ==============================================================================

class BallotSubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'debate', 'timestamp', 'submitter_type', 'user')
    search_fields = ('debate__debateteam__team__reference', 'debate__debateteam__team__institution__code')
    raw_id_fields = ('debate','motion')
    # This incurs a massive performance hit
    #inlines = (SpeakerScoreByAdjInline, SpeakerScoreInline, TeamScoreInline)

admin.site.register(models.BallotSubmission, BallotSubmissionAdmin)

# ==============================================================================
# ActionLog
# ==============================================================================

class ActionLogAdmin(admin.ModelAdmin):
    list_display = ('type', 'user', 'timestamp', 'get_parameters_display', 'tournament')
    list_filter = ('tournament', 'user', 'type')
    search_fields = ('type', 'tournament__name', 'user__username')

    def get_queryset(self, request):
        return super(ActionLogAdmin, self).get_queryset(request).select_related(
            'tournament','user'
        )

admin.site.register(models.ActionLog, ActionLogAdmin)
