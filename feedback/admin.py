from django.contrib import admin

from . import models

class AdjudicatorFeedbackQuestionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'text', 'seq', 'tournament', 'answer_type', 'required', 'chair_on_panellist', 'panellist_on_chair', 'panellist_on_panellist', 'team_on_orallist')
    list_filter = ('tournament',)
    ordering = ('tournament', 'seq')

admin.site.register(models.AdjudicatorFeedbackQuestion, AdjudicatorFeedbackQuestionAdmin)

class BaseAdjudicatorFeedbackAnswerInline(admin.TabularInline):
    model = NotImplemented
    fields = ('question', 'answer')
    extra = 1

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "question":
            kwargs["queryset"] = models.AdjudicatorFeedbackQuestion.objects.filter(answer_type__in=models.AdjudicatorFeedbackQuestion.ANSWER_TYPE_CLASSES_REVERSE[self.model])
        return super(BaseAdjudicatorFeedbackAnswerInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

class AdjudicatorFeedbackAdmin(admin.ModelAdmin):
    list_display = ('adjudicator', 'source_adjudicator', 'source_team', 'confirmed', 'score')
    search_fields = ('source_adjudicator__adjudicator__name', 'source_team__team__institution__code', 'source_team__team__reference', 'adjudicator__name', 'adjudicator__institution__code',)
    raw_id_fields = ('source_team',)

    # dynamically generate inline tables for different answer types
    inlines = []
    for _answer_type_class in models.AdjudicatorFeedbackQuestion.ANSWER_TYPE_CLASSES_REVERSE:
        _inline_class = type(_answer_type_class.__name__ + "Inline", (BaseAdjudicatorFeedbackAnswerInline,),
                {"model": _answer_type_class, "__module__": __name__})
        inlines.append(_inline_class)

admin.site.register(models.AdjudicatorFeedback, AdjudicatorFeedbackAdmin)