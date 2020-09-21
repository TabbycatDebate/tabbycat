from django import forms
from django.contrib import admin, messages
from django.db.models import Prefetch
from django.utils.translation import gettext, ngettext
from django.utils.translation import gettext_lazy as _

from draw.models import DebateTeam
from utils.admin import custom_titled_filter

from .models import (AdjudicatorBaseScoreHistory, AdjudicatorFeedback, AdjudicatorFeedbackBooleanAnswer,
    AdjudicatorFeedbackFloatAnswer, AdjudicatorFeedbackIntegerAnswer, AdjudicatorFeedbackManyAnswer,
    AdjudicatorFeedbackQuestion, AdjudicatorFeedbackStringAnswer)


# ==============================================================================
# Adjudicator base score histories
# ==============================================================================

@admin.register(AdjudicatorBaseScoreHistory)
class AdjudicatorBaseScoreHistoryAdmin(admin.ModelAdmin):
    list_display = ('adjudicator', 'round', 'score', 'timestamp')
    list_filter  = ('adjudicator', 'round')
    ordering     = ('timestamp',)
    search_fields = ('adjudicator__name', 'adjudicator__institution__code')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('round__tournament', 'adjudicator__institution')


# ==============================================================================
# Adjudicator feedback questions
# ==============================================================================

class QuestionForm(forms.ModelForm):
    class Meta:
        model = AdjudicatorFeedbackQuestion
        fields = '__all__'

    def clean(self):
        integer_scale = AdjudicatorFeedbackQuestion.ANSWER_TYPE_INTEGER_SCALE
        if self.cleaned_data.get('answer_type') == integer_scale:
            if not self.cleaned_data.get('min_value') or not self.cleaned_data.get('max_value'):
                raise forms.ValidationError(_("Integer scales must have a minimum and maximum"))
        return self.cleaned_data


@admin.register(AdjudicatorFeedbackQuestion)
class AdjudicatorFeedbackQuestionAdmin(admin.ModelAdmin):
    form = QuestionForm
    list_display = ('reference', 'text', 'seq', 'tournament', 'answer_type',
                    'required', 'from_adj', 'from_team')
    list_filter  = ('tournament',)
    ordering     = ('tournament', 'seq')


# ==============================================================================
# Adjudicator feedback answers
# ==============================================================================

@admin.register(AdjudicatorFeedbackBooleanAnswer)
@admin.register(AdjudicatorFeedbackFloatAnswer)
@admin.register(AdjudicatorFeedbackIntegerAnswer)
@admin.register(AdjudicatorFeedbackManyAnswer)
@admin.register(AdjudicatorFeedbackStringAnswer)
class AdjudicatorFeedbackAnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'get_target', 'get_source', 'answer', 'get_feedback_description')
    list_select_related = ('question', 'feedback__adjudicator',
                           'feedback__source_adjudicator__adjudicator',
                           'feedback__source_team__team')
    list_filter  = (
        'question', 'answer',
        ('feedback__adjudicator__name', custom_titled_filter(_('target'))),
        ('feedback__source_adjudicator__adjudicator__name', custom_titled_filter(_('source adjudicator'))),
        ('feedback__source_team__team__short_name', custom_titled_filter(_('source team'))),
    )
    raw_id_fields = ('feedback',)

    def get_target(self, obj):
        return obj.feedback.adjudicator.name

    def get_source(self, obj):
        if obj.feedback.source_team and obj.feedback.source_adjudicator:
            return "<ERROR: both source team and source adjudicator>"
        elif obj.feedback.source_team:
            return obj.feedback.source_team.team.short_name
        elif obj.feedback.source_adjudicator:
            return obj.feedback.source_adjudicator.adjudicator.name

    def get_feedback_description(self, obj):
        return gettext("%(timestamp)s (version %(version)s)") % {
            'timestamp': obj.feedback.timestamp.isoformat(),
            'version': obj.feedback.version,
        }

    get_target.short_description = _("Target")
    get_source.short_description = _("Source")
    get_feedback_description.short_description = _("Feedback timestamp and version")


class BaseAdjudicatorFeedbackAnswerInline(admin.TabularInline):
    model = None  # Must be set by subclasses
    fields = ('question', 'answer')
    extra = 1

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "question":
            kwargs["queryset"] = AdjudicatorFeedbackQuestion.objects.filter(
                answer_type__in=AdjudicatorFeedbackQuestion.ANSWER_TYPE_CLASSES_REVERSE[self.model])
        return super(BaseAdjudicatorFeedbackAnswerInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


class RoundListFilter(admin.SimpleListFilter):
    """Filters AdjudicatorFeedbacks by round."""
    title = "round"
    parameter_name = "round"

    def lookups(self, request, model_admin):
        from tournaments.models import Round
        return [(str(r.id), "[{}] {}".format(r.tournament.short_name, r.name)) for r in Round.objects.all()]

    def queryset(self, request, queryset):
        return queryset.filter(source_team__debate__round_id=self.value()) | queryset.filter(source_adjudicator__debate__round_id=self.value())


# ==============================================================================
# Adjudicator Feedbacks
# ==============================================================================

@admin.register(AdjudicatorFeedback)
class AdjudicatorFeedbackAdmin(admin.ModelAdmin):
    list_display  = ('adjudicator', 'confirmed', 'ignored', 'score', 'version', 'get_source')
    search_fields = ('adjudicator__name', 'adjudicator__institution__code',
            'score', 'source_adjudicator__adjudicator__name',
            'source_team__team__short_name', 'source_team__team__long_name')
    raw_id_fields = ('source_team', 'adjudicator', 'source_team', 'source_adjudicator')
    list_filter   = (
        RoundListFilter,
        ('adjudicator', custom_titled_filter(_('target'))),
        ('source_adjudicator__adjudicator__name', custom_titled_filter(_('source adjudicator'))),
        ('source_team__team__short_name', custom_titled_filter(_('source team'))),
    )
    actions       = ('mark_as_confirmed', 'mark_as_unconfirmed', 'ignore_feedback', 'recognize_feedback')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'source_team__debate__round__tournament',
            'source_team__team',
            'source_adjudicator__debate__round__tournament',
            'source_adjudicator__adjudicator__institution',
            'adjudicator__institution',
        ).prefetch_related(
            Prefetch('source_team__debate__debateteam_set', queryset=DebateTeam.objects.select_related('team')),
            Prefetch('source_adjudicator__debate__debateteam_set', queryset=DebateTeam.objects.select_related('team')),
        )

    def get_source(self, obj):
        if obj.source_team and obj.source_adjudicator:
            return "<ERROR: both source team and source adjudicator>"
        else:
            return obj.source_team or obj.source_adjudicator
    get_source.short_description = _("Source")

    # Dynamically generate inline tables for different answer types
    inlines = []
    for _answer_type_class in AdjudicatorFeedbackQuestion.ANSWER_TYPE_CLASSES_REVERSE:
        _inline_class = type(
            _answer_type_class.__name__ + "Inline", (BaseAdjudicatorFeedbackAnswerInline,),
            {"model": _answer_type_class, "__module__": __name__})
        inlines.append(_inline_class)

    def mark_as_confirmed(self, request, queryset):
        original_count = queryset.count()
        for fb in queryset.order_by('version').all():
            fb.confirmed = True
            fb.save()
        final_count = queryset.filter(confirmed=True).count()

        message = ngettext(
            "1 feedback submission was marked as confirmed. Note that this may "
            "have caused other feedback submissions to be marked as unconfirmed.",
            "%(count)d feedback submissions were marked as confirmed. Note that "
            "this may have caused other feedback submissions to be marked as "
            "unconfirmed.",
            final_count,
        ) % {'count': final_count}
        self.message_user(request, message)

        difference = original_count - final_count
        if difference > 0:
            message = ngettext(
                "1 feedback submission was not marked as confirmed, probably "
                "because other feedback submissions that conflict with it were "
                "also marked as confirmed.",
                "%(count)d feedback submissions were not marked as confirmed, "
                "probably because other feedback submissions that conflict "
                "with them were also marked as confirmed.",
                difference,
            ) % {'count': difference}
            self.message_user(request, message, level=messages.WARNING)

    def mark_as_unconfirmed(self, request, queryset):
        count = queryset.update(confirmed=False)
        message = ngettext(
            "1 feedback submission was marked as unconfirmed.",
            "%(count)d feedback submissions were marked as unconfirmed.",
            count,
        ) % {'count': count}
        self.message_user(request, message)

    def ignore_feedback(self, request, queryset):
        count = queryset.update(ignored=True)

        message = ngettext(
            "1 feedback submission is now ignored.",
            "%(count)d feedback submissions are now ignored.",
            count,
        ) % {'count': count}
        self.message_user(request, message)

    def recognize_feedback(self, request, queryset):
        count = queryset.update(ignored=False)

        message = ngettext(
            "1 feedback submission is now recognized.",
            "%(count)d feedback submissions are now recognized.",
            count,
        ) % {'count': count}
        self.message_user(request, message)
