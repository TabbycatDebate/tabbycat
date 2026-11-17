from itertools import groupby

from django.contrib import admin
from django.db.models import Prefetch
from django.forms.models import BaseInlineFormSet
from django.utils.translation import gettext_lazy as _, ngettext_lazy

from draw.admin_widgets import BallotSubmissionScoreInlineDebateTeamRawIdMixin, PrefetchedForeignKeyRawIdWidget
from draw.models import DebateTeam
from utils.admin import ModelAdmin, TabbycatModelAdminFieldsMixin

from .models import BallotSubmission, ScoreCriterion, SpeakerCriterionScore, SpeakerCriterionScoreByAdj, SpeakerScore, SpeakerScoreByAdj, TeamScore, TeamScoreByAdj
from .prefetch import populate_results


# ==============================================================================
# BallotSubmission inlines (Jet shows each inline as a tab on the change form)
# ==============================================================================

class BallotScoreInlineFormSet(BaseInlineFormSet):
    """Reuse the inline queryset's related objects for raw-ID labels."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ('debate_team', 'debate_adjudicator', 'speaker'):
            if name not in self.form.base_fields:
                continue
            field = self.form.base_fields[name]
            widget = field.widget
            objects = {getattr(score, f'{name}_id'): getattr(score, name) for score in self.get_queryset()}
            if isinstance(widget, PrefetchedForeignKeyRawIdWidget):
                widget.objects = objects
                widget.queryset = field.queryset
            else:
                field.widget = PrefetchedForeignKeyRawIdWidget(
                    widget.rel, widget.admin_site, attrs=widget.attrs,
                    using=widget.db, queryset=field.queryset, objects=objects,
                )


class BallotScoreInline(BallotSubmissionScoreInlineDebateTeamRawIdMixin, admin.TabularInline):
    formset = BallotScoreInlineFormSet
    extra = 0
    show_change_link = True

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related('debate_team__team__tournament')
        relations = ['debate_team']
        if hasattr(self.model, 'debate_adjudicator'):
            qs = qs.select_related('debate_adjudicator__adjudicator')
            relations.append('debate_adjudicator')
        for relation in relations:
            qs = qs.select_related(f'{relation}__debate__round__tournament').prefetch_related(
                Prefetch(f'{relation}__debate__debateteam_set', queryset=DebateTeam.objects.select_related('team')),
            )
        return qs


class TeamScoreInline(BallotScoreInline):
    model = TeamScore
    ordering = ('debate_team__side',)
    raw_id_fields = ('debate_team',)


class TeamScoreByAdjInline(BallotScoreInline):
    model = TeamScoreByAdj
    ordering = ('debate_adjudicator_id', 'debate_team__side')
    raw_id_fields = ('debate_team', 'debate_adjudicator')


class SpeakerScoreInline(BallotScoreInline):
    model = SpeakerScore
    ordering = ('debate_team__side', 'position')
    raw_id_fields = ('debate_team', 'speaker')


class SpeakerScoreByAdjInline(BallotScoreInline):
    model = SpeakerScoreByAdj
    ordering = ('debate_adjudicator_id', 'debate_team__side', 'position')
    raw_id_fields = ('debate_team', 'debate_adjudicator')


class SpeakerCriterionScoreInline(admin.TabularInline):
    model = SpeakerCriterionScore
    extra = 0
    raw_id_fields = ('criterion',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('criterion')


class SpeakerCriterionScoreByAdjInline(admin.TabularInline):
    model = SpeakerCriterionScoreByAdj
    extra = 0
    raw_id_fields = ('criterion',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('criterion')


# ==============================================================================
# BallotSubmission
# ==============================================================================

@admin.register(BallotSubmission)
class BallotSubmissionAdmin(TabbycatModelAdminFieldsMixin, ModelAdmin):
    list_display = ('id', 'debate', 'version', 'get_round', 'timestamp',
            'submitter_type', 'submitter', 'confirmer', 'confirmed')
    list_editable = ('confirmed',)
    search_fields = ('debate__debateteam__team__short_name', 'debate__debateteam__team__institution__name')
    raw_id_fields = ('debate', 'motion')
    list_filter = ('debate__round', 'debate__round__tournament', 'submitter', 'confirmer')
    inlines = (TeamScoreInline, TeamScoreByAdjInline, SpeakerScoreInline, SpeakerScoreByAdjInline)
    actions = ['resave_ballots']

    def get_queryset(self, request):
        return super(BallotSubmissionAdmin, self).get_queryset(request).select_related(
            'submitter', 'confirmer', 'debate__round__tournament').prefetch_related(
            Prefetch('debate__debateteam_set', queryset=DebateTeam.objects.select_related('team__tournament', 'debate__round__tournament')))

    @admin.display(description=_("Resave results"))
    def resave_ballots(self, request, queryset):
        q = queryset.select_related('debate__round__tournament').order_by('debate__round__tournament_id')
        count = q.count()
        for tournament, bss in groupby(q, lambda bs: bs.debate.round.tournament):
            populate_results(bss, tournament)
            for bs in bss:
                bs.result.save()

        self.message_user(request, ngettext_lazy(
            "Resaved results for %(count)d ballot submission.",
            "Resaved results for %(count)d ballot submissions.",
            count) % {'count': count})


# ==============================================================================
# TeamScore
# ==============================================================================

@admin.register(TeamScore)
class TeamScoreAdmin(TabbycatModelAdminFieldsMixin, ModelAdmin):
    list_display = ('id', 'ballot_submission', 'get_round', 'get_team', 'points', 'win', 'score')
    search_fields = ('debate_team__debate__round__seq', 'debate_team__debate__round__tournament__name',
                     'debate_team__team__short_name', 'debate_team__team__institution__name')
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
class TeamScoreByAdjAdmin(TabbycatModelAdminFieldsMixin, ModelAdmin):
    list_display = ('id', 'ballot_submission', 'get_round', 'get_adj_name', 'get_team', 'win', 'margin', 'score')
    search_fields = ('debate_team__debate__round__seq', 'debate_team__debate__round__tournament__name',
                     'debate_team__team__short_name', 'debate_team__team__institution__name')
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
class SpeakerScoreAdmin(TabbycatModelAdminFieldsMixin, ModelAdmin):
    list_display = ('id', 'ballot_submission', 'get_round', 'get_team', 'position',
                    'get_speaker_name', 'score', 'ghost')
    search_fields = ('debate_team__debate__round__abbreviation',
                     'debate_team__team__short_name', 'debate_team__team__institution__name',
                     'speaker__name')
    list_filter = ('score', 'debate_team__debate__round', 'ghost')
    raw_id_fields = ('debate_team', 'ballot_submission')
    inlines = (SpeakerCriterionScoreInline,)

    def get_queryset(self, request):
        crit = SpeakerCriterionScore.objects.select_related('criterion')
        return super(SpeakerScoreAdmin, self).get_queryset(request).select_related(
            'debate_team__debate__round',
            'debate_team__team__institution', 'debate_team__team__tournament',
            'ballot_submission').prefetch_related(
            Prefetch('ballot_submission__debate__debateteam_set',
                queryset=DebateTeam.objects.select_related('team')),
            Prefetch('speakercriterionscore_set', queryset=crit),
        )


# ==============================================================================
# SpeakerScoreByAdj
# ==============================================================================

@admin.register(SpeakerScoreByAdj)
class SpeakerScoreByAdjAdmin(TabbycatModelAdminFieldsMixin, ModelAdmin):
    list_display = ('id', 'ballot_submission', 'get_round', 'get_adj_name', 'get_team', 'position', 'get_speaker_name', 'score')
    search_fields = ('debate_team__debate__round__seq',
                     'debate_team__team__short_name', 'debate_team__team__institution__name',
                     'debate_adjudicator__adjudicator__name')

    list_filter = ('debate_team__debate__round', 'debate_adjudicator__adjudicator__name',
                   'debate_adjudicator__type')
    raw_id_fields = ('debate_team', 'debate_adjudicator', 'ballot_submission')
    inlines = (SpeakerCriterionScoreByAdjInline,)

    @admin.display(description=_("Speaker"))
    def get_speaker_name(self, obj):
        speaker_score = getattr(obj, 'speaker_score', None)
        return speaker_score.speaker.name if speaker_score else None

    def get_queryset(self, request):
        crit_adj = SpeakerCriterionScoreByAdj.objects.select_related('criterion')

        return super(SpeakerScoreByAdjAdmin, self).get_queryset(request).select_related(
            'ballot_submission__debate__round__tournament',
            'debate_adjudicator__adjudicator',
            'debate_team__team__tournament',
            'debate_team__debate__round__tournament',
            'speaker_score__speaker',
        ).prefetch_related(
            Prefetch('ballot_submission__debate__debateteam_set',
                queryset=DebateTeam.objects.select_related('team')),
            Prefetch('speakercriterionscorebyadj_set', queryset=crit_adj),
        )


# ==============================================================================
# SpeakerCriterionScore
# ==============================================================================

@admin.register(SpeakerCriterionScore)
class SpeakerCriterionScoreAdmin(TabbycatModelAdminFieldsMixin, ModelAdmin):
    list_display = ('id', 'criterion', 'speaker_score', 'score')
    search_fields = ('criterion', 'score', 'speaker_score')


# ==============================================================================
# SpeakerCriterionScoreByAdj
# ==============================================================================

@admin.register(SpeakerCriterionScoreByAdj)
class SpeakerCriterionScoreByAdjAdmin(TabbycatModelAdminFieldsMixin, ModelAdmin):
    list_display = ('id', 'criterion', 'speaker_score_by_adj', 'score')
    search_fields = ('criterion', 'score', 'speaker_score_by_adj')


# ==============================================================================
# SpeakerCriterion
# ==============================================================================

@admin.register(ScoreCriterion)
class ScoreCriterionAdmin(TabbycatModelAdminFieldsMixin, ModelAdmin):
    list_display = ('id', 'tournament', 'name', 'seq', 'speech_type')
    search_fields = ('tournament', 'name')
