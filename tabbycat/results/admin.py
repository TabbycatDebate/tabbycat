from django.contrib import admin
from django.db.models import Prefetch
from django.db.models.expressions import RawSQL

from .models import BallotSubmission, SpeakerScore, SpeakerScoreByAdj, TeamScore

from draw.models import DebateTeam
from utils.admin import TabbycatModelAdminFieldsMixin


# ==============================================================================
# BallotSubmission
# ==============================================================================

@admin.register(BallotSubmission)
class BallotSubmissionAdmin(TabbycatModelAdminFieldsMixin, admin.ModelAdmin):
    list_display = ('id', 'debate', 'version', 'get_round', 'timestamp',
            'submitter_type', 'submitter', 'confirmer')
    search_fields = ('debate__debateteam__team__reference', 'debate__debateteam__team__institution__code')
    raw_id_fields = ('debate', 'motion', 'copied_from', 'forfeit')
    list_filter = ('debate__round', 'submitter', 'confirmer')
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
    list_display = ('id', 'ballot_submission', 'get_round', 'get_team', 'score')
    search_fields = ('debate_team__debate__round__seq', 'debate_team__debate__round__tournament__name',
                     'debate_team__team__reference', 'debate_team__team__institution__code')
    list_filter = ('debate_team__debate__round', )
    raw_id_fields = ('ballot_submission', 'debate_team')

    def get_round(self, obj):
        return obj.ballot_submission.debate.round.name
    get_round.short_description = "Round"

    def get_queryset(self, request):
        return super(TeamScoreAdmin, self).get_queryset(request).select_related(
            'ballot_submission__debate__round__tournament',
            'debate_team__team__tournament').prefetch_related(
            Prefetch('ballot_submission__debate__debateteam_set', queryset=DebateTeam.objects.select_related('team')))


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
    list_filter = ('score', 'debate_team__debate__round')
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

    list_filter = ('debate_team__debate__round', 'debate_adjudicator__adjudicator__name')
    raw_id_fields = ('debate_team', 'debate_adjudicator', 'ballot_submission')

    def get_round(self, obj):
        return obj.ballot_submission.debate.round.name
    get_round.short_description = "Round"

    def get_adj_name(self, obj):
        return obj.debate_adjudicator.adjudicator.name
    get_adj_name.short_description = "Adjudicator"

    def get_queryset(self, request):
        return super(SpeakerScoreByAdjAdmin, self).get_queryset(request).select_related(
            'ballot_submission__debate__round__tournament',
            'debate_adjudicator__adjudicator',
            'debate_team__team__tournament'
        ).prefetch_related(
            Prefetch('ballot_submission__debate__debateteam_set',
                queryset=DebateTeam.objects.select_related('team'))
        ).annotate(
            speaker_name=RawSQL("""
                SELECT participants_person.name
                FROM results_speakerscore
                INNER JOIN participants_person ON results_speakerscore.speaker_id = participants_person.id
                WHERE results_speakerscore.debate_team_id = results_speakerscorebyadj.debate_team_id
                AND results_speakerscore.position = results_speakerscorebyadj.position
                AND results_speakerscore.ballot_submission_id = results_speakerscorebyadj.ballot_submission_id""",
                ()),
        )

    def get_speaker_name(self, obj):
        return obj.speaker_name
    get_speaker_name.short_description = "Speaker"
