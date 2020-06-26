from django.contrib import admin
from django.db.models import OuterRef, Prefetch, Subquery

from draw.models import DebateTeam
from utils.admin import TabbycatModelAdminFieldsMixin

from .models import BallotSubmission, SpeakerScore, SpeakerScoreByAdj, TeamScore, TeamScoreByAdj


# ==============================================================================
# BallotSubmission
# ==============================================================================

@admin.register(BallotSubmission)
class BallotSubmissionAdmin(TabbycatModelAdminFieldsMixin, admin.ModelAdmin):
    list_display = ('id', 'debate', 'version', 'get_round', 'timestamp',
            'submitter_type', 'submitter', 'confirmer', 'confirmed')
    list_editable = ('confirmed',)
    search_fields = ('debate__debateteam__team__reference', 'debate__debateteam__team__institution__code')
    raw_id_fields = ('debate', 'motion')
    list_filter = ('debate__round', 'debate__round__tournament', 'submitter', 'confirmer')
    # This incurs a massive performance hit
    # inlines = (SpeakerScoreByAdjInline, SpeakerScoreInline, TeamScoreInline)

    def get_queryset(self, request):
        return super(BallotSubmissionAdmin, self).get_queryset(request).select_related(
            'submitter', 'confirmer', 'debate__round__tournament').prefetch_related(
            Prefetch('debate__debateteam_set', queryset=DebateTeam.objects.select_related('team')))


# ==============================================================================
# TeamScore
# ==============================================================================

@admin.register(TeamScore)
class TeamScoreAdmin(TabbycatModelAdminFieldsMixin, admin.ModelAdmin):
    list_display = ('id', 'ballot_submission', 'get_round', 'get_team', 'points', 'win', 'score')
    search_fields = ('debate_team__debate__round__seq', 'debate_team__debate__round__tournament__name',
                     'debate_team__team__reference', 'debate_team__team__institution__code')
    list_filter = ('debate_team__debate__round', )
    raw_id_fields = ('ballot_submission', 'debate_team')

    def get_queryset(self, request):
        return super(TeamScoreAdmin, self).get_queryset(request).select_related(
            'ballot_submission__debate__round__tournament',
            'debate_team__team__tournament',
            'debate_team__debate__round').prefetch_related(
            Prefetch('ballot_submission__debate__debateteam_set', queryset=DebateTeam.objects.select_related('team')))


# ==============================================================================
# TeamScoreByAdj
# ==============================================================================

@admin.register(TeamScoreByAdj)
class TeamScoreByAdjAdmin(TabbycatModelAdminFieldsMixin, admin.ModelAdmin):
    list_display = ('id', 'ballot_submission', 'get_round', 'get_adj_name', 'get_team', 'win', 'margin', 'score')
    search_fields = ('debate_team__debate__round__seq', 'debate_team__debate__round__tournament__name',
                     'debate_team__team__reference', 'debate_team__team__institution__code')
    list_filter = ('debate_team__debate__round', 'debate_adjudicator__adjudicator__name')
    raw_id_fields = ('ballot_submission', 'debate_adjudicator', 'debate_team')

    def get_queryset(self, request):
        return super(TeamScoreByAdjAdmin, self).get_queryset(request).select_related(
            'ballot_submission__debate__round__tournament',
            'debate_adjudicator__adjudicator',
            'debate_team__team',
            'debate_team__team__tournament',
        ).prefetch_related(
            Prefetch('ballot_submission__debate__debateteam_set', queryset=DebateTeam.objects.select_related('team')),
        )


# ==============================================================================
# SpeakerScore
# ==============================================================================

@admin.register(SpeakerScore)
class SpeakerScoreAdmin(TabbycatModelAdminFieldsMixin, admin.ModelAdmin):
    list_display = ('id', 'ballot_submission', 'get_round', 'get_team', 'position',
                    'get_speaker_name', 'score', 'ghost')
    search_fields = ('debate_team__debate__round__abbreviation',
                     'debate_team__team__reference', 'debate_team__team__institution__code',
                     'speaker__name')
    list_filter = ('score', 'debate_team__debate__round', 'ghost')
    raw_id_fields = ('debate_team', 'ballot_submission')

    def get_queryset(self, request):
        return super(SpeakerScoreAdmin, self).get_queryset(request).select_related(
            'debate_team__debate__round',
            'debate_team__team__institution', 'debate_team__team__tournament',
            'ballot_submission').prefetch_related(
            Prefetch('ballot_submission__debate__debateteam_set',
                queryset=DebateTeam.objects.select_related('team')))


# ==============================================================================
# SpeakerScoreByAdj
# ==============================================================================

@admin.register(SpeakerScoreByAdj)
class SpeakerScoreByAdjAdmin(TabbycatModelAdminFieldsMixin, admin.ModelAdmin):
    list_display = ('id', 'ballot_submission', 'get_round', 'get_adj_name', 'get_team',
                    'get_speaker_name', 'position', 'score')
    search_fields = ('debate_team__debate__round__seq',
                     'debate_team__team__reference', 'debate_team__team__institution__code',
                     'debate_adjudicator__adjudicator__name')

    list_filter = ('debate_team__debate__round', 'debate_adjudicator__adjudicator__name',
                   'debate_adjudicator__type')
    raw_id_fields = ('debate_team', 'debate_adjudicator', 'ballot_submission')

    def get_queryset(self, request):
        speaker_person = SpeakerScore.objects.filter(
            ballot_submission_id=OuterRef('ballot_submission_id'),
            debate_team_id=OuterRef('debate_team_id'),
            position=OuterRef('position'),
        ).select_related('speaker')

        return super(SpeakerScoreByAdjAdmin, self).get_queryset(request).select_related(
            'ballot_submission__debate__round__tournament',
            'debate_adjudicator__adjudicator',
            'debate_team__team__tournament',
        ).prefetch_related(
            Prefetch('ballot_submission__debate__debateteam_set',
                queryset=DebateTeam.objects.select_related('team')),
        ).annotate(speaker_name=Subquery(speaker_person.values('speaker__name')))
