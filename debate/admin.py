from django.contrib import admin
from django import forms

import debate.models as models


admin.site.register(models.DebateTeam)

class CustomTournamentAwareChoiceField(forms.ModelChoiceField):
    # For displaying information that may be duplicated across tournaments
    def label_from_instance(self, obj):
         return "%s - %s" % (obj.tournament, obj.name)

class AddCustomDisplayForRound(forms.ModelForm):
    current_round = CustomTournamentAwareChoiceField(queryset=models.Round.objects.all().order_by('tournament','seq'))
    class Meta:
          model = models.Round
          exclude = () # Needed

    def __init__(self, *args, **kwargs):
        super(AddCustomDisplayForRound, self).__init__(*args, **kwargs)
        try:
            self.fields['current_round'].queryset = models.Round.objects.filter(tournament=self.instance).order_by('seq')
        except:
            self.fields['current_round'].queryset = models.Round.objects.all().order_by('tournament','name')

class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name','short_name','current_round')
    ordering = ('name',)
    form = AddCustomDisplayForRound

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

class AddCustomDisplayForDivisions(forms.ModelForm):
    division = CustomTournamentAwareChoiceField(queryset=models.Division.objects.all().order_by('tournament','name'))
    class Meta:
          model = models.Division
          exclude = () # Needed

    def __init__(self, *args, **kwargs):
        super(AddCustomDisplayForDivisions, self).__init__(*args, **kwargs)
        try:
            self.fields['division'].queryset = models.Division.objects.filter(tournament=self.instance.tournament).order_by('name')
        except:
            self.fields['division'].queryset = models.Division.objects.all().order_by('tournament','name')


class TeamAdmin(admin.ModelAdmin):
    list_display = ('long_name','short_reference','institution', 'division', 'tournament')
    search_fields = ('reference', 'short_reference', 'institution__name', 'institution__code', 'tournament__name')
    list_filter = ('tournament', 'institution')
    form = AddCustomDisplayForDivisions
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


class AddCustomDisplayForVenueGroups(forms.ModelForm):
    venue_group = CustomTournamentAwareChoiceField(queryset=models.VenueGroup.objects.all().order_by('tournament','name'))

    class Meta:
          model = models.VenueGroup
          exclude = () # Needed

    def __init__(self, *args, **kwargs):
        super(AddCustomDisplayForVenueGroups, self).__init__(*args, **kwargs)
        try:
            self.fields['venue_group'].queryset = models.VenueGroup.objects.filter(tournament=self.instance.tournament).order_by('name')
        except:
            self.fields['venue_group'].queryset = models.VenueGroup.objects.all().order_by('tournament','name')

class DivisionAdmin(admin.ModelAdmin):
    list_display = ('name', 'tournament', 'venue_group','time_slot')
    list_filter = ('tournament','venue_group',)
    search_fields = ('name',)
    ordering = ('tournament','name',)
    form = AddCustomDisplayForVenueGroups

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



class AddCustomDisplayForVenue(forms.ModelForm):
    group = CustomTournamentAwareChoiceField(queryset=models.VenueGroup.objects.all().order_by('tournament','name'))
    class Meta:
          model = models.VenueGroup
          exclude = () # Needed

class CustomVenueGroupListFilter(admin.SimpleListFilter):
    title = 'group'
    parameter_name = 'group'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        groups = models.VenueGroup.objects.all().order_by('tournament','name')
        for g in groups:
            g.admin_name = "%s - %s" % (g.tournament, g.short_name)
        return [(c.id, c.admin_name) for c in groups]

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            return queryset.filter(group=self.value())
        else:
            return queryset

class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'group', 'priority', 'time', 'tournament')
    list_filter = ('tournament', CustomVenueGroupListFilter, 'priority', 'time')
    search_fields = ('name', 'group', 'time')
    form = AddCustomDisplayForVenue

admin.site.register(models.Venue, VenueAdmin)

class DebateTeamInline(admin.TabularInline):
    model = models.DebateTeam
    extra = 1

class DebateAdjudicatorInline(admin.TabularInline):
    model = models.DebateAdjudicator
    extra = 1

_da_tournament = lambda o: o.round.tournament.name
_da_tournament.short_description = 'Tournament'
class DebateAdmin(admin.ModelAdmin):
    list_display = ('id', _da_tournament, 'round', 'aff_team', 'neg_team', 'adjudicators',)
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
    list_display = ('name', 'tournament', 'seq', 'abbreviation', 'stage', 'draw_type', 'draw_status', 'feedback_weight', 'silent', 'motions_released', 'starts_at')
    list_filter = ('tournament',)
    search_fields = ('name', 'seq', 'abbreviation', 'stage', 'draw_type', 'draw_status')

admin.site.register(models.Round, RoundAdmin)

class DebateAdjudicatorAdmin(admin.ModelAdmin):
    list_display = ('debate', 'adjudicator', 'type')
    search_fields = ('adjudicator__name', 'type')
admin.site.register(models.DebateAdjudicator, DebateAdjudicatorAdmin)



class AddCustomDisplayForRounds(forms.ModelForm):
    round = CustomTournamentAwareChoiceField(queryset=models.Round.objects.all().order_by('tournament','name'))
    class Meta:
          model = models.Round
          exclude = () # Needed

    def __init__(self, *args, **kwargs):
        super(AddCustomDisplayForRounds, self).__init__(*args, **kwargs)
        try:
            self.fields['round'].queryset = models.Round.objects.filter(tournament=self.instance.round.tournament).order_by('seq')
        except:
            self.fields['round'].queryset = models.Round.objects.all().order_by('tournament','seq')

_m_tournament = lambda o: o.round.tournament
class MotionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'round','seq',_m_tournament)
    list_filter = ('round',)
    form = AddCustomDisplayForRounds

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
