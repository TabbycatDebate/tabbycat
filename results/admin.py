from django.contrib import admin

from . import models
from participants.models import Team, Speaker, Adjudicator
from debate.models import Round
from results.models import SpeakerScore

# ==============================================================================
# BallotSubmission
# ==============================================================================

class BallotSubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'debate', 'timestamp', 'submitter_type', 'submitter', 'confirmer')
    search_fields = ('debate__debateteam__team__reference', 'debate__debateteam__team__institution__code')
    raw_id_fields = ('debate','motion')
    # This incurs a massive performance hit
    #inlines = (SpeakerScoreByAdjInline, SpeakerScoreInline, TeamScoreInline)

admin.site.register(models.BallotSubmission, BallotSubmissionAdmin)

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
    # TODO: re-enable
    #list_filter = ('debate_team__debate__round__seq', 'debate_team__team__institution__code')
    raw_id_fields = ('debate_team','ballot_submission')

admin.site.register(models.SpeakerScoreByAdj, SpeakerScoreByAdjAdmin)


