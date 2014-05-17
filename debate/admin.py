from django.contrib import admin

import debate.models as models

class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

admin.site.register(models.Institution, InstitutionAdmin)

class SpeakerInline(admin.TabularInline):
    model = models.Speaker

class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'institution',)
    search_fields = ('name','institution__name', 'institution__code',)
    inlines = (SpeakerInline,)

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

class AdjudicatorAdmin(admin.ModelAdmin):
    list_display = ('name', 'institution')
    search_fields = ('name', 'institution__name', 'institution__code',)
    inlines = (AdjudicatorConflictInline,AdjudicatorInstitutionConflictInline)
admin.site.register(models.Adjudicator, AdjudicatorAdmin)

class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'group', 'priority')
    search_fields = ('name',)
admin.site.register(models.Venue, VenueAdmin)

class DebateTeamInline(admin.TabularInline):
    model = models.DebateTeam
    extra = 1

class DebateAdjudicatorInline(admin.TabularInline):
    model = models.DebateAdjudicator
    extra = 1

class DebateAdmin(admin.ModelAdmin):
    list_display = ('id', 'aff_team', 'neg_team', 'adjudicators_display',)
    search_fields = ('debateteam__team__name', 'debateadjudicator__adjudicator__name',)
    inlines = (DebateTeamInline, DebateAdjudicatorInline)
admin.site.register(models.Debate, DebateAdmin)

_ts_round = lambda o: o.debate_team.debate.round.seq
_ts_round.short_description = 'Round'
_ts_team = lambda o: o.debate_team.team.name
_ts_team.short_description = 'Team'
class TeamScoreAdmin(admin.ModelAdmin):
    list_display = ('id', _ts_round, _ts_team,)
    search_fields = ('debate_team__debate__round__seq',
                     'debate_team__team__name')
admin.site.register(models.TeamScore, TeamScoreAdmin)

_ss_speaker = lambda o: o.speaker.name
_ss_speaker.short_description = 'Speaker'
class SpeakerScoreAdmin(admin.ModelAdmin):
    list_display = ('id', _ts_round, _ts_team, 'position', _ss_speaker, 'score')
    search_fields = ('debate_team__debate__round__seq',
                     'debate_team__team__name', 'speaker__name')
    list_filter = ('score',)
admin.site.register(models.SpeakerScore, SpeakerScoreAdmin)

class RoundAdminInline(admin.TabularInline):
    model = models.Round

class TournamentAdmin(admin.ModelAdmin):
    inlines = [RoundAdminInline]

admin.site.register(models.Tournament, TournamentAdmin)

admin.site.register(models.DebateTeam)
admin.site.register(models.DebateAdjudicator)

class MotionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'round')
    list_filter = ('round',)

admin.site.register(models.Motion, MotionAdmin)