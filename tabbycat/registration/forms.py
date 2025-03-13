from django import forms
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _

from participants.emoji import EMOJI_RANDOM_FIELD_CHOICES
from participants.models import Adjudicator, Coach, Institution, Speaker, Team, TournamentInstitution

from .form_utils import CustomQuestionsFormMixin


class TournamentInstitutionForm(CustomQuestionsFormMixin, forms.ModelForm):

    institution_name = Institution._meta.get_field('name')
    institution_code = Institution._meta.get_field('code')

    name = forms.CharField(max_length=institution_name.max_length, label=capfirst(institution_name.verbose_name), help_text=institution_name.help_text)
    code = forms.CharField(max_length=institution_code.max_length, label=capfirst(institution_code.verbose_name), help_text=institution_code.help_text)

    field_order = ('name', 'code', 'teams_requested', 'adjudicators_requested')

    def __init__(self, tournament, *args, **kwargs):
        self.tournament = tournament
        super().__init__(*args, **kwargs)
        self.add_question_fields()

    class Meta:
        model = TournamentInstitution
        exclude = ('tournament', 'institution', 'teams_allocated', 'adjudicators_allocated')

    def save(self):
        inst, created = Institution.objects.get_or_create(name=self.cleaned_data.pop('name'), code=self.cleaned_data.pop('code'))

        obj = super().save(commit=False)
        obj.institution = inst
        obj.tournament = self.tournament
        obj.save()
        self.save_answers(obj)

        return obj


class InstitutionCoachForm(CustomQuestionsFormMixin, forms.ModelForm):

    def __init__(self, tournament, *args, **kwargs):
        self.tournament = tournament
        super().__init__(*args, **kwargs)
        self.add_question_fields()

    class Meta:
        model = Coach
        fields = ('name', 'email')

    def save(self):
        obj = super().save()
        self.save_answers(obj)
        return obj


class TeamForm(CustomQuestionsFormMixin, forms.ModelForm):

    def __init__(self, tournament, *args, institution=None, **kwargs):
        self.tournament = tournament
        self.institution = institution
        super().__init__(*args, **kwargs)

        for field in {'use_institution_prefix', 'code_name', 'break_categories', 'seed', 'emoji'} - set(self.tournament.pref('reg_team_fields')):
            self.fields.pop(field)

        if self.tournament.pref('team_name_generator') != 'user':
            self.fields.pop('reference')

        if self.institution is not None:
            self.fields.pop('institution')

        if 'emoji' in self.fields:
            used_emoji = self.tournament.team_set.filter(emoji__isnull=False).values_list('emoji', flat=True)
            self.fields['emoji'].choices = [e for e in EMOJI_RANDOM_FIELD_CHOICES if e[0] not in used_emoji]

        if 'seed' in self.fields and self.tournament.pref('show_seed_in_importer') == 'title':
            self.fields['seed'] = forms.ChoiceField(required=False, label=self.fields['seed'].label, choices=(
                (0, _("Unseeded")),
                (1, _("Free seed")),
                (2, _("Half seed")),
                (3, _("Full seed")),
            ), help_text=self.fields['seed'].help_text)

        self.add_question_fields()

    class Meta:
        model = Team
        fields = ('reference', 'institution', 'use_institution_prefix', 'seed', 'emoji')

    def save(self):
        self.instance.tournament = self.tournament
        obj = super().save()
        self.save_answers(obj)
        return obj


class SpeakerForm(CustomQuestionsFormMixin, forms.ModelForm):

    def __init__(self, tournament, *args, **kwargs):
        self.tournament = tournament
        super().__init__(*args, **kwargs)

        for field in ({'email', 'phone', 'gender', 'categories'} - set(self.tournament.pref('reg_speaker_fields'))):
            self.fields.pop(field)

        if 'categories' in self.fields:
            self.fields['categories'].queryset = tournament.speakercategory_set.filter(public=True)

        self.add_question_fields()

    class Meta:
        model = Speaker
        fields = ('name', 'email', 'phone', 'gender', 'categories')

    def save(self):
        obj = super().save()
        self.save_answers(obj)
        return obj


class AdjudicatorForm(CustomQuestionsFormMixin, forms.ModelForm):

    def __init__(self, tournament, *args, institution=None, **kwargs):
        self.tournament = tournament
        self.institution = institution
        super().__init__(*args, **kwargs)

        for field in ({'email', 'phone', 'gender'} - set(self.tournament.pref('reg_adjudicator_fields'))):
            self.fields.pop(field)

        if self.institution is not None:
            self.fields.pop('institution')

        self.add_question_fields()

    class Meta:
        model = Adjudicator
        fields = ('name', 'institution', 'email', 'phone', 'gender')

    def clean(self):
        raise

    def save(self):
        obj = super().save()
        self.save_answers(obj)
        return obj
