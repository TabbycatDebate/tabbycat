from django.contrib import admin

import debate.models as models

class InstitutionAdmin(admin.ModelAdmin):
    if models.Tournament.objects.count() > 1:
        list_display = ('name', 'tournament')
    else:
        list_display = ('name',)

    ordering = ('name',)
    search_fields = ('name',)

admin.site.register(models.Institution, InstitutionAdmin)

class SpeakerInline(admin.TabularInline):
    model = models.Speaker
    fields = ('name', 'barcode_id', 'email', 'phone')

class TeamPositionAllocationInline(admin.TabularInline):
    model = models.TeamPositionAllocation

class TeamLocationPreferencesInline(admin.TabularInline):
    model = models.Team.venue_group_preferences.through
    verbose_name = "Team Venue Group Preferences"
    verbose_name_plural = "Team Venue Group Preferences"
    extra = 1

class TeamAdmin(admin.ModelAdmin):
    if models.Tournament.objects.count() > 1:
        _team_tournament = lambda o: o.institution.tournament
        _team_tournament.short_description = 'Tournament'
        list_display = ('name', 'institution', _team_tournament)
    else:
        list_display = ('name', 'institution')

    search_fields = ('name','institution__name', 'institution__code',)
    inlines = (SpeakerInline, TeamPositionAllocationInline, TeamLocationPreferencesInline)
    exclude = ("venue_group_preferences",)

admin.site.register(models.Team, TeamAdmin)

class SpeakerAdmin(admin.ModelAdmin):
    list_display = ('name', 'team', )
    search_fields = ('name', 'team__name', 'team__institution__name',
                     'team__institution__code',)
admin.site.register(models.Speaker, SpeakerAdmin)

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
    if models.Tournament.objects.count() > 1:
        _adj_tournament = lambda o: o.institution.tournament
        _adj_tournament.short_description = 'Tournament'
        list_display = ('name', 'institution', _adj_tournament)
    else:
        list_display = ('name', 'institution')

    search_fields = ('name', 'institution__name', 'institution__code',)
    inlines = (AdjudicatorConflictInline,AdjudicatorInstitutionConflictInline, AdjudicatorTestScoreHistoryInline)
admin.site.register(models.Adjudicator, AdjudicatorAdmin)

class AdjudicatorFeedbackAdmin(admin.ModelAdmin):
    list_display = ('adjudicator', 'source_adjudicator', 'source_team', 'confirmed', 'score', 'comments')
    search_fields = ('source_adjudicator__adjudicator__name', 'source_team__team__institution__code', 'source_team__team__reference', 'adjudicator__name', 'adjudicator__institution__code',)
admin.site.register(models.AdjudicatorFeedback, AdjudicatorFeedbackAdmin)

class VenueGroupAdmin(admin.ModelAdmin):
    if models.Tournament.objects.count() > 1:
        list_display = ('tournament',)
    else:
        list_display = ('name',)

    search_fields = ('name',)

admin.site.register(models.VenueGroup, VenueGroupAdmin)

class VenueAdmin(admin.ModelAdmin):
    if models.Tournament.objects.count() > 1:
        list_display = ('tournament', 'name', 'group', 'priority', 'time')
    else:
        list_display = ('name', 'group', 'priority', 'time')

    search_fields = ('name', 'group__name', 'time')
admin.site.register(models.Venue, VenueAdmin)

class DebateTeamInline(admin.TabularInline):
    model = models.DebateTeam
    extra = 1

class DebateAdjudicatorInline(admin.TabularInline):
    model = models.DebateAdjudicator
    extra = 1

class DebateAdmin(admin.ModelAdmin):
    list_display = ('id', 'round', 'aff_team', 'neg_team', 'adjudicators',)
    search_fields = ('debateteam__team__reference', 'debateteam__team__institution__code',
                     'debateadjudicator__adjudicator__name',)
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
    list_display = ('name', 'seq', 'abbreviation', 'stage', 'draw_type', 'draw_status', 'feedback_weight', 'silent', 'motions_released', 'starts_at')
admin.site.register(models.Round, RoundAdmin)

admin.site.register(models.Tournament)
admin.site.register(models.DebateTeam)

class DebateAdjudicatorAdmin(admin.ModelAdmin):
    list_display = ('debate', 'adjudicator', 'type')
    search_fields = ('adjudicator__name', 'type')
admin.site.register(models.DebateAdjudicator, DebateAdjudicatorAdmin)

class MotionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'round')
    list_filter = ('round',)

admin.site.register(models.Motion, MotionAdmin)

#class SpeakerScoreByAdjInline(admin.TabularInline):
    #model = models.SpeakerScoreByAdj
    #extra = 0

#class SpeakerScoreInline(admin.TabularInline):
    #model = models.SpeakerScore
    #extra = 0

#class TeamScoreInline(admin.TabularInline):
    #model = models.TeamScore
    #extra = 0

class BallotSubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'debate', 'timestamp', 'submitter_type', 'user')
    search_fields = ('debate__debateteam__team__reference', 'debate__debateteam__team__institution__code')
    # This incurs a massive performance hit
    #inlines = (SpeakerScoreByAdjInline, SpeakerScoreInline, TeamScoreInline)

admin.site.register(models.BallotSubmission, BallotSubmissionAdmin)

class ActionLogAdmin(admin.ModelAdmin):
    list_display = ('type', 'user', 'timestamp', 'get_parameters_display')
    search_fields = ('type', 'user__username')
admin.site.register(models.ActionLog, ActionLogAdmin)