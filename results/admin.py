from django.contrib import admin

from .models import BallotSubmission, TeamScore, SpeakerScore, SpeakerScoreByAdj

from utils.admin import BaseModelAdmin


# ==============================================================================
# BallotSubmission
# ==============================================================================

class BallotSubmissionAdmin(admin.ModelAdmin, BaseModelAdmin):
    list_display = ('id', 'debate', 'get_round', 'timestamp', 'submitter_type', 'submitter', 'confirmer')
    search_fields = ('debate__debateteam__team__reference', 'debate__debateteam__team__institution__code')
    raw_id_fields = ('debate', 'motion')
    list_filter = ('debate__round', 'submitter', 'confirmer')
    # This incurs a massive performance hit
    # inlines = (SpeakerScoreByAdjInline, SpeakerScoreInline, TeamScoreInline)

admin.site.register(BallotSubmission, BallotSubmissionAdmin)


# ==============================================================================
# TeamScore
# ==============================================================================

class TeamScoreAdmin(admin.ModelAdmin, BaseModelAdmin):
    list_display = ('id', 'ballot_submission', 'get_round', 'get_team', 'score')
    search_fields = ('debate_team__debate__round__seq',
                     'debate_team__team__reference', 'debate_team__team__institution__code')


admin.site.register(TeamScore, TeamScoreAdmin)


# ==============================================================================
# SpeakerScore
# ==============================================================================

class SpeakerScoreAdmin(admin.ModelAdmin, BaseModelAdmin):
    list_display = ('id', 'ballot_submission', 'get_round', 'get_team', 'position', 'get_speaker_name', 'score')
    search_fields = ('debate_team__debate__round__abbreviation',
                     'debate_team__team__reference', 'debate_team__team__institution__code',
                     'speaker__name')
    list_filter = ('score', 'debate_team__debate__round')
    raw_id_fields = ('debate_team', 'ballot_submission')

    def get_queryset(self, request):
        return super(SpeakerScoreAdmin, self).get_queryset(request).select_related(
            'debate_team__debate__round',
            'debate_team__team__institution', 'debate_team__team__tournament',
            'ballot_submission')

admin.site.register(SpeakerScore, SpeakerScoreAdmin)


# ==============================================================================
# SpeakerScoreByAdj
# ==============================================================================

class SpeakerScoreByAdjAdmin(admin.ModelAdmin, BaseModelAdmin):
    list_display = ('id', 'ballot_submission', 'get_round', 'get_adj_name', 'get_team', 'get_speaker_name_filter', 'position', 'score')
    search_fields = ('debate_team__debate__round__seq',
                     'debate_team__team__reference', 'debate_team__team__institution__code',
                     'debate_adjudicator__adjudicator__name')

    list_filter = ('debate_team__debate__round', 'debate_adjudicator__adjudicator__name')
    raw_id_fields = ('debate_team','ballot_submission')

    def get_speaker_name_filter(self, obj):
        return SpeakerScore.objects.filter(debate_team=obj.debate_team, position=obj.position)[0].speaker.name
    get_speaker_name_filter.short_description = 'Speaker'

admin.site.register(SpeakerScoreByAdj, SpeakerScoreByAdjAdmin)
