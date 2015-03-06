from django.contrib import admin
from django import forms

import debate.models as models

admin.site.register(models.DebateTeam)

class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name','short_name','current_round')
    ordering = ('name',)

admin.site.register(models.Tournament,TournamentAdmin)


class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('name','code')
    ordering = ('name',)
    search_fields = ('name',)

admin.site.register(models.Institution, InstitutionAdmin)


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

admin.site.register(models.Team, TeamAdmin)


class TeamVenuePreferenceAdmin(admin.ModelAdmin):
    list_display = ('team', 'venue_group', 'priority')
    search_fields = ('team','venue_group', 'priority')
    list_filter = ('team','venue_group', 'priority')

admin.site.register(models.TeamVenuePreference, TeamVenuePreferenceAdmin)


class SpeakerAdmin(admin.ModelAdmin):
    list_display = ('name', 'team')
    search_fields = ('name', 'team__name', 'team__institution__name',
                     'team__institution__code',)
admin.site.register(models.Speaker, SpeakerAdmin)


class DivisionAdmin(admin.ModelAdmin):
    list_display = ('name', 'tournament', 'venue_group','time_slot')
    list_filter = ('tournament', 'venue_group')
    search_fields = ('name',)
    ordering = ('tournament', 'name',)

admin.site.register(models.Division, DivisionAdmin)

class AdjudicatorConflictInline(admin.TabularInline):
    model = models.AdjudicatorConflict
    extra = 1

class AdjudicatorInstitutionConflictInline(admin.TabularInline):
    model = models.AdjudicatorInstitutionConflict
    extra = 1

class AdjudicatorTestScoreHistoryInline(admin.TabularInline):
    model = models.AdjudicatorTestScoreHistory
    extra = 1

class AdjudicatorAdmin(admin.ModelAdmin):
    list_display = ('name', 'institution', 'tournament')
    search_fields = ('name', 'tournament__name', 'institution__name', 'institution__code',)
    list_filter = ('tournament', 'name')
    inlines = (AdjudicatorConflictInline,AdjudicatorInstitutionConflictInline, AdjudicatorTestScoreHistoryInline)
admin.site.register(models.Adjudicator, AdjudicatorAdmin)

class AdjudicatorFeedbackAdmin(admin.ModelAdmin):
    list_display = ('adjudicator', 'source_adjudicator', 'source_team', 'confirmed', 'score', 'comments')
    search_fields = ('source_adjudicator__adjudicator__name', 'source_team__team__institution__code', 'source_team__team__reference', 'adjudicator__name', 'adjudicator__institution__code',)
admin.site.register(models.AdjudicatorFeedback, AdjudicatorFeedbackAdmin)


class VenueGroupAdmin(admin.ModelAdmin):
    list_display = ('name','tournament','team_capacity')
    search_fields = ('name',)
    list_filter = ('tournament',)

admin.site.register(models.VenueGroup, VenueGroupAdmin)

class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'group', 'priority', 'time', 'tournament')
    list_filter = ('tournament', 'group', 'priority', 'time')
    search_fields = ('name', 'group', 'time')

admin.site.register(models.Venue, VenueAdmin)

class DebateTeamInline(admin.TabularInline):
    model = models.DebateTeam
    extra = 1

class DebateAdjudicatorInline(admin.TabularInline):
    model = models.DebateAdjudicator
    extra = 1

# _da_tournament = lambda o: o.round.tournament.name
# _da_tournament.short_description = 'Tournament'
_da_division = lambda o: o.division.name
_da_division.short_description = 'Division'
class DebateAdmin(admin.ModelAdmin):
    list_display = ('id','round',_da_division,'bracket','aff_team', 'neg_team',)
    list_filter = ('round__tournament','round', 'division')
    inlines = (DebateTeamInline, DebateAdjudicatorInline)

admin.site.register(models.Debate, DebateAdmin)

_ts_round = lambda o: o.debate_team.debate.round.seq
_ts_round.short_description = 'Round'
_ts_team = lambda o: o.debate_team.team.name
_ts_team.short_description = 'Team'
class TeamScoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'ballot_submission', _ts_round, _ts_team, 'score')
    search_fields = ('debate_team__debate__round__seq',
                     'debate_team__team__reference', 'debate_team__team__institution__code')
admin.site.register(models.TeamScore, TeamScoreAdmin)

_ss_speaker = lambda o: o.speaker.name
_ss_speaker.short_description = 'Speaker'
class SpeakerScoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'ballot_submission', _ts_round, _ts_team, 'position', _ss_speaker, 'score')
    search_fields = ('debate_team__debate__round__seq',
                     'debate_team__team__reference', 'debate_team__team__institution__code',
                     'speaker__name')
    list_filter = ('score',)
admin.site.register(models.SpeakerScore, SpeakerScoreAdmin)

_ssba_speaker = lambda o: models.SpeakerScore.objects.filter(debate_team=o.debate_team, position=o.position)[0].speaker.name
_ssba_speaker.short_description = 'Speaker'
_ssba_adj = lambda o: o.debate_adjudicator.adjudicator.name
_ssba_adj.short_description = 'Adjudicator'
class SpeakerScoreByAdjAdmin(admin.ModelAdmin):
    list_display = ('id', 'ballot_submission', _ts_round, _ssba_adj, _ts_team, 'position', _ssba_speaker, 'score')
    search_fields = ('debate_team__debate__round__seq',
                     'debate_team__team__reference', 'debate_team__team__institution__code',
                     'debate_adjudicator__adjudicator__name')
admin.site.register(models.SpeakerScoreByAdj, SpeakerScoreByAdjAdmin)

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

class RoundAdmin(admin.ModelAdmin):
    list_display = ('name', 'tournament', 'seq', 'abbreviation', 'stage', 'draw_type', 'draw_status', 'feedback_weight', 'silent', 'motions_released', 'starts_at')
    list_filter = ('tournament',)
    search_fields = ('name', 'seq', 'abbreviation', 'stage', 'draw_type', 'draw_status')

admin.site.register(models.Round, RoundAdmin)

class DebateAdjudicatorAdmin(admin.ModelAdmin):
    list_display = ('debate', 'adjudicator', 'type')
    search_fields = ('adjudicator__name', 'type')
admin.site.register(models.DebateAdjudicator, DebateAdjudicatorAdmin)


_m_tournament = lambda o: o.round.tournament
class MotionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'round','seq', _m_tournament)
    list_filter = ('round', 'divisions')

admin.site.register(models.Motion, MotionAdmin)

class BallotSubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'debate', 'timestamp', 'submitter_type', 'user')
    search_fields = ('debate__debateteam__team__reference', 'debate__debateteam__team__institution__code')
    # This incurs a massive performance hit
    #inlines = (SpeakerScoreByAdjInline, SpeakerScoreInline, TeamScoreInline)

admin.site.register(models.BallotSubmission, BallotSubmissionAdmin)

class ActionLogAdmin(admin.ModelAdmin):
    list_display = ('type', 'user', 'timestamp', 'get_parameters_display', 'tournament')
    list_filter = ('tournament', 'user', 'type')
    search_fields = ('type', 'tournament__name', 'user__username')
admin.site.register(models.ActionLog, ActionLogAdmin)
