import json
import logging

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext as _, gettext_lazy

from utils.forms import OptionalChoiceField

logger = logging.getLogger(__name__)


class SpacedRadioWidget(forms.RadioSelect):
    template_name = 'spaced_choice_widget.html'


class IntegerScaleField(forms.IntegerField):
    """Class to do integer scale fields."""
    widget = SpacedRadioWidget()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget.choices = tuple((i, str(i)) for i in range(self.min_value, self.max_value+1))


class BlankUnknownBooleanSelect(forms.NullBooleanSelect):
    """Uses '--------' instead of 'Unknown' for the None choice."""

    def __init__(self, attrs=None):
        choices = (
            ('1', '--------'),
            # Translators: Please leave this blank, it should be left for the base Django translations.
            ('2', gettext_lazy('Yes')),
            # Translators: Please leave this blank, it should be left for the base Django translations.
            ('3', gettext_lazy('No')),
        )
        # skip the NullBooleanSelect constructor
        super().__init__(attrs, choices)


class BooleanSelectField(forms.NullBooleanField):
    """Widget to do boolean select fields following our conventions.
    Specifically, if 'required', checks that an option was chosen."""
    widget = BlankUnknownBooleanSelect

    def clean(self, value):
        value = super(BooleanSelectField, self).clean(value)
        if self.required and value is None:
            # Translators: Please leave this blank, it should be left for the base Django translations.
            raise forms.ValidationError(_("This field is required."))
        return value


class BlockCheckboxWidget(forms.CheckboxSelectMultiple):
    template_name = 'spaced_choice_widget.html'


class CustomQuestionsFormMixin:

    _enforce_required = True

    def get_custom_question_queryset(self):
        return self.tournament.question_set.filter(for_content_type=ContentType.objects.get_for_model(self._meta.model)).order_by('seq')

    @staticmethod
    def question_field_name(question):
        return f'q{question.for_content_type_id}-{question.seq}'

    def add_question_fields(self):
        for question in self.get_custom_question_queryset():
            self.fields[self.question_field_name(question)] = self._make_question_field(question)

    def _make_question_field(self, question):
        match question.answer_type:
            case question.AnswerType.BOOLEAN_SELECT:
                field = BooleanSelectField()
            case question.AnswerType.BOOLEAN_CHECKBOX:
                field = forms.BooleanField(required=False)
            case question.AnswerType.INTEGER_TEXTBOX:
                min_value = int(question.min_value) if question.min_value else None
                max_value = int(question.max_value) if question.max_value else None
                field = forms.IntegerField(min_value=min_value, max_value=max_value)
            case question.AnswerType.INTEGER_SCALE:
                min_value = int(question.min_value) if question.min_value is not None else None
                max_value = int(question.max_value) if question.max_value is not None else None
                if min_value is None or max_value is None:
                    logger.error("Integer scale %r has no min_value or no max_value" % question.reference)
                    field = forms.IntegerField()
                else:
                    field = IntegerScaleField(min_value=min_value, max_value=max_value)
            case question.AnswerType.FLOAT:
                field = forms.FloatField(min_value=question.min_value, max_value=question.max_value)
            case question.AnswerType.TEXT:
                field = forms.CharField()
            case question.AnswerType.LONGTEXT:
                field = forms.CharField(widget=forms.Textarea)
            case question.AnswerType.SINGLE_SELECT:
                field = OptionalChoiceField(choices=question.choices_for_field)
            case question.AnswerType.MULTIPLE_SELECT:
                field = forms.MultipleChoiceField(choices=question.choices_for_field, widget=BlockCheckboxWidget())
        field.label = question.text
        if question.help_text:
            field.help_text = question.help_text

        # Required checkbox fields don't really make sense; so override the behaviour?
        if question.answer_type is not question.AnswerType.BOOLEAN_CHECKBOX:
            if question.required:
                field.label += "*"
            field.required = self._enforce_required and question.required

        return field

    def save_answers(self, obj):
        for question in self.get_custom_question_queryset():
            response = self.cleaned_data[self.question_field_name(question)]
            if response is not None:
                if question.answer_type is question.AnswerType.MULTIPLE_SELECT:
                    response = json.dumps(response)
                if response != "":
                    question.answer_set.create(content_object=obj, answer=response)
