from django import forms
from django.contrib import admin, messages
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.contenttypes.models import ContentType
from django.db.models import Prefetch
from django.utils.translation import gettext_lazy as _, ngettext
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin

from draw.models import DebateTeam
from registration.models import Answer
from utils.admin import custom_titled_filter, ModelAdmin

from .models import AdjudicatorBaseScoreHistory, AdjudicatorFeedback, AdjudicatorFeedbackQuestion


# ==============================================================================
# Adjudicator base score histories
# ==============================================================================

@admin.register(AdjudicatorBaseScoreHistory)
class AdjudicatorBaseScoreHistoryAdmin(ModelAdmin):
    list_display = ('adjudicator', 'round', 'score', 'timestamp')
    list_filter  = ('adjudicator', 'round')
    ordering     = ('timestamp',)
    search_fields = ('adjudicator__name', 'adjudicator__institution__name')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('round__tournament', 'adjudicator__institution')


# ==============================================================================
# Adjudicator feedback questions
# ==============================================================================

class QuestionForm(forms.ModelForm):
    class Meta:
        model = AdjudicatorFeedbackQuestion
        exclude = ('for_content_type',)

    def clean(self):
        integer_scale = AdjudicatorFeedbackQuestion.AnswerType.INTEGER_SCALE
        if self.cleaned_data.get('answer_type') == integer_scale:
            if self.cleaned_data.get('min_value') is None or self.cleaned_data.get('max_value') is None:
                raise forms.ValidationError(_("Integer scales must have a minimum and maximum"))
            if self.cleaned_data['max_value'] < self.cleaned_data['min_value']:
                raise forms.ValidationError(_("Maximum value must be greater than the minimum"))
        return self.cleaned_data


@admin.register(AdjudicatorFeedbackQuestion)
class AdjudicatorFeedbackQuestionAdmin(DynamicArrayMixin, ModelAdmin):
    form = QuestionForm
    list_display = ('reference', 'text', 'seq', 'tournament', 'answer_type',
                    'required', 'from_adj', 'from_team')
    list_filter  = ('tournament',)
    ordering     = ('tournament', 'seq')

    def save_model(self, request, obj, form, change):
        obj.for_content_type = ContentType.objects.get(app_label="adjfeedback", model="adjudicatorfeedback")
        super().save_model(request, obj, form, change)


# ==============================================================================
# Adjudicator feedback answers
# ==============================================================================


class AdjudicatorFeedbackAnswerInline(GenericTabularInline):
    model = Answer
    fields = ('question', 'answer')
    extra = 1

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "question":
            kwargs["queryset"] = AdjudicatorFeedbackQuestion.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


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
class AdjudicatorFeedbackAdmin(ModelAdmin):
    list_display  = ('adjudicator', 'confirmed', 'ignored', 'score', 'version', 'get_source')
    search_fields = ('adjudicator__name', 'adjudicator__institution__name',
            'score', 'source_adjudicator__adjudicator__name',
            'source_team__team__short_name', 'source_team__team__long_name')
    raw_id_fields = ('source_team', 'adjudicator', 'source_team', 'source_adjudicator')
    list_filter   = (
        RoundListFilter,
        ('adjudicator', custom_titled_filter(_('target'))),
        ('source_adjudicator__adjudicator__name', custom_titled_filter(_('source adjudicator'))),
        ('source_team__team__short_name', custom_titled_filter(_('source team'))),
    )
    inlines       = [AdjudicatorFeedbackAnswerInline]
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

    @admin.display(description=_("Source"))
    def get_source(self, obj):
        if obj.source_team and obj.source_adjudicator:
            return "<ERROR: both source team and source adjudicator>"
        else:
            return obj.source_team or obj.source_adjudicator

    def mark_as_confirmed(self, request, queryset):
        original_count = queryset.count()
        for fb in queryset.order_by('version').all():
            # Update them in order to override previous versions (prefer newer)
            fb.confirmed = True
            fb.save()
            self.log_change(request, fb, [{"changed": {"fields": ["confirmed"]}}])
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
        for fb in queryset:
            self.log_change(request, fb, [{"changed": {"fields": ["confirmed"]}}])
        message = ngettext(
            "1 feedback submission was marked as unconfirmed.",
            "%(count)d feedback submissions were marked as unconfirmed.",
            count,
        ) % {'count': count}
        self.message_user(request, message)

    def ignore_feedback(self, request, queryset):
        count = queryset.update(ignored=True)
        for fb in queryset:
            self.log_change(request, fb, [{"changed": {"fields": ["ignored"]}}])

        message = ngettext(
            "1 feedback submission is now ignored.",
            "%(count)d feedback submissions are now ignored.",
            count,
        ) % {'count': count}
        self.message_user(request, message)

    def recognize_feedback(self, request, queryset):
        count = queryset.update(ignored=False)
        for fb in queryset:
            self.log_change(request, fb, [{"changed": {"fields": ["ignored"]}}])

        message = ngettext(
            "1 feedback submission is now recognized.",
            "%(count)d feedback submissions are now recognized.",
            count,
        ) % {'count': count}
        self.message_user(request, message)
