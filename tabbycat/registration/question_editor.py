"""Forms for the registration question editor."""
import hashlib
import json

from django import forms
from django.forms import BaseModelFormSet
from django.utils.translation import gettext_lazy as _

from options.preferences import (
    AdjudicatorRegistrationFields, InstitutionRegistrationFields,
    SpeakerRegistrationFields, TeamRegistrationFields,
)
from participants.models import Adjudicator, Coach, Speaker, Team, TournamentInstitution

from .forms import AdjudicatorForm, InstitutionCoachForm, SpeakerForm, TeamForm, TournamentInstitutionForm
from .models import Question


class QuestionEditorForm(forms.ModelForm):
    choices = forms.JSONField(required=False, widget=forms.HiddenInput(), label=_("Options"),
        help_text=_("Paste multiple lines into an empty option to add them together. Blank lines are skipped."))

    class Meta:
        model = Question
        fields = ('text', 'answer_type', 'choices', 'min_value', 'max_value', 'help_text', 'name', 'required')
        widgets = {'help_text': forms.Textarea(attrs={'rows': 2})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].label = _("Question")
        self.fields['text'].help_text = ''
        self.fields['answer_type'].initial = Question.AnswerType.TEXT
        self.fields['name'].required = False
        self.fields['name'].label = _("Short name for tables")
        self.fields['name'].help_text = _("Optional; defaults to the first 30 characters of the question.")

    def clean_choices(self):
        options = self.cleaned_data['choices']
        if options is None:
            return []
        if not isinstance(options, list) or any(not isinstance(option, str) for option in options):
            raise forms.ValidationError(_("Enter a list of text options."))
        return options

    def clean(self):
        data = super().clean()
        if not data.get('name') and data.get('text'):
            data['name'] = data['text'][:30]
        if data.get('answer_type') in ('ss', 'ms') and 'choices' in data and not any(option.strip() for option in data['choices']):
            self.add_error('choices', _("Add at least one option."))
        minimum, maximum = data.get('min_value'), data.get('max_value')
        if data.get('answer_type') in ('i', 'is', 'f') and minimum is not None and maximum is not None and minimum > maximum:
            self.add_error('max_value', _("Maximum must be at least the minimum."))
        if data.get('answer_type') == 'is' and (minimum is None or maximum is None):
            self.add_error('min_value', _("Set both bounds for an integer scale."))
        return data


class QuestionEditorFormSet(BaseModelFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)
        # Apply the same ownership boundary to submitted IDs as to displayed rows.
        form.fields[self.model._meta.pk.name].queryset = self.get_queryset()
        form.fields['ORDER'].widget = forms.HiddenInput()
        form.fields['DELETE'].widget = forms.HiddenInput()


SECTION_CONFIG = {
    Team: (TeamForm, TeamRegistrationFields, ('reference', 'institution')),
    Speaker: (SpeakerForm, SpeakerRegistrationFields, ('name',)),
    TournamentInstitution: (TournamentInstitutionForm, InstitutionRegistrationFields, ('name', 'code')),
    Coach: (InstitutionCoachForm, None, ('name', 'email')),
    Adjudicator: (AdjudicatorForm, AdjudicatorRegistrationFields, ('name', 'institution')),
}


def system_questions(tournament, model, data=None, editable=False):
    form_class, preference, fixed_names = SECTION_CONFIG[model]
    fields = form_class.base_fields
    fixed_names = list(fixed_names)
    if model is Speaker and (tournament.pref('team_name_generator') == 'initials' or tournament.pref('code_name_generator') == 'last_names'):
        fixed_names.append('last_name')
    if model is TournamentInstitution and tournament.pref('reg_institution_slots'):
        fixed_names.extend(('teams_requested', 'adjudicators_requested'))
    system_form = forms.Form(data=data, prefix=f'{model._meta.model_name}-system')
    selected = []
    if preference:
        manager = tournament.preferences
        stored = manager.get_db_pref(section=preference.section.name, name=preference.name)
        if editable and data is not None:
            stored.refresh_from_db(from_queryset=manager.queryset.select_for_update())
        selected = stored.value
    questions = []
    for name, label in [(name, fields[name].label) for name in fixed_names] + list(preference.choices if preference else []):
        field = fields[name]
        optional = name not in fixed_names
        toggle = None
        if optional:
            system_form.fields[name] = forms.BooleanField(label=label, required=False, initial=name in selected, disabled=not editable)
            toggle = system_form[name]
        if isinstance(field, forms.BooleanField):
            answer_type = _("Checkbox")
        elif isinstance(field, (forms.ModelMultipleChoiceField, forms.MultipleChoiceField)):
            answer_type = _("Select multiple")
        elif isinstance(field, (forms.ModelChoiceField, forms.ChoiceField)):
            answer_type = _("Select one")
        elif isinstance(field, forms.IntegerField):
            answer_type = _("Number")
        elif isinstance(field, forms.EmailField):
            answer_type = _("Email address")
        else:
            answer_type = _("Short answer")
        condition = ''
        if name == 'institution':
            condition = _("Asked only when the institution is not already known.")
        elif model is Team and name in ('reference', 'use_institution_prefix'):
            condition = _("Visibility depends on the team name generator and whether the institution is already known.")
        elif model is Team and name == 'break_categories':
            condition = _("Shown when non-general break categories are available.")
        elif model is TournamentInstitution and name in ('teams_requested', 'adjudicators_requested'):
            condition = _("Included when requesting slots, except for registrations by invitation.")
        questions.append({
            'label': label, 'type': answer_type, 'help_text': field.help_text,
            'toggle': toggle, 'required': field.required, 'condition': condition,
        })
    return system_form, questions, preference


def question_section_revision(formset, system_form):
    fields = ('pk', 'seq', *formset.form._meta.fields)
    questions = [[getattr(question, field) for field in fields] for question in formset.get_queryset()]
    settings = {name: field.initial for name, field in system_form.fields.items() if not field.disabled}
    snapshot = json.dumps([questions, settings], sort_keys=True)
    return hashlib.sha256(snapshot.encode()).hexdigest()


def serialize_question_section(section):
    """Keep bound values (including invalid input) and form indices on a failed POST."""
    formset = section['formset']

    def serialize_form(form, index):
        values = {}
        for name in form.fields:
            if name == 'choices':
                field = form.fields[name]
                options = field.bound_data(form[name].data, None) if form.is_bound else form.initial.get(name)
                values[name] = [option for option in options if isinstance(option, str)] if isinstance(options, list) else []
                continue
            value = form[name].value()
            if isinstance(form.fields[name], forms.BooleanField):
                value = form.fields[name].to_python(value)
            values[name] = '' if value is None else value
        return {
            'formIndex': index, 'values': values, 'deleted': values['DELETE'],
            'errors': {name: list(errors) for name, errors in form.errors.items() if name != '__all__'},
            'nonFieldErrors': list(form.non_field_errors()),
        }

    empty = formset.empty_form
    fields = {}
    for name in empty._meta.fields:
        field = empty.fields[name]
        fields[name] = {
            'label': str(field.label), 'helpText': str(field.help_text),
            'maxLength': getattr(field, 'max_length', None),
            'choices': list(getattr(field, 'choices', [])),
            'kind': 'checkbox' if isinstance(field, forms.BooleanField) else 'select' if name == 'answer_type' else
                    'options' if name == 'choices' else 'textarea' if name == 'help_text' else
                    'number' if name in ('min_value', 'max_value') else 'text',
        }
    systems = []
    for question in section['system_questions']:
        toggle = question['toggle']
        systems.append({
            **{key: value for key, value in question.items() if key != 'toggle'},
            'name': toggle.html_name if toggle is not None else None,
            'enabled': bool(toggle.value()) if toggle is not None else True,
            'disabled': toggle.field.disabled if toggle is not None else True,
        })
    return {
        'title': section['title'], 'prefix': section['prefix'], 'fields': fields,
        'revision': formset.data.get(f'{formset.prefix}-revision', '') if formset.is_bound else section['revision'],
        'primaryKey': formset.model._meta.pk.name,
        'systemQuestions': systems,
        'questions': [serialize_form(form, index) for index, form in enumerate(formset.forms)],
        'emptyQuestion': serialize_form(empty, None),
        'nonFormErrors': list(formset.non_form_errors()),
        'management': {
            'prefix': formset.prefix, 'totalForms': formset.total_form_count(),
            'initialForms': formset.initial_form_count(), 'minNumForms': formset.min_num,
            'maxNumForms': formset.max_num,
        },
    }
