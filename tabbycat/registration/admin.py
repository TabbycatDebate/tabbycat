from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

from utils.admin import ModelAdmin

from .models import Answer, Invitation, Question, SlotTransferRequest


@admin.register(Answer)
class AnswerAdmin(ModelAdmin):
    list_display = ('question', 'answer', 'content_object')
    list_filter = ('question',)


@admin.register(Question)
class QuestionAdmin(ModelAdmin):
    list_display = ('name', 'tournament', 'for_content_type', 'answer_type')
    list_filter = ('tournament', 'for_content_type')


@admin.register(Invitation)
class InvitationAdmin(ModelAdmin):
    list_display = ('url_key', 'tournament', 'for_content_type', 'institution')


@admin.register(SlotTransferRequest)
class SlotTransferRequestAdmin(ModelAdmin):
    list_display = ('id', 'tournament', 'source_institution_name', 'receiving_institution_name', 'teams_transferred', 'adjudicators_transferred')
    list_filter = ('tournament', 'status')
    list_select_related = ('source_tournament_institution__institution', 'receiving_institution__institution')

    @admin.display(description=_("Source"))
    def source_institution_name(self, obj):
        return obj.source_tournament_institution.institution.name

    @admin.display(description=_("Receiving"))
    def receiving_institution_name(self, obj):
        return obj.receiving_institution.institution.name if obj.receiving_institution else obj.receiving_institution_name


class AnswerInline(GenericTabularInline):
    model = Answer
    fields = ('question', 'answer')
    extra = 1

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "question":
            kwargs["queryset"] = Question.objects.filter(for_content_type=ContentType.objects.get_for_model(self.parent_model))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
