import random

from django import forms
from django.utils.translation import gettext_lazy as _

from participants.emoji import EMOJI_RANDOM_FIELD_CHOICES, pick_unused_emoji
from participants.models import Adjudicator, Coach, Institution, Region, RegistrationStatus, Speaker, Team, TournamentInstitution
from privateurls.utils import populate_url_keys

from .form_utils import CustomQuestionsFormMixin, get_answers_initial
from .models import SlotTransferRequest


class TournamentInstitutionForm(CustomQuestionsFormMixin, forms.ModelForm):

    institution_name = Institution._meta.get_field('name')
    institution_code = Institution._meta.get_field('code')
    institution_region = Institution._meta.get_field('region')

    name = forms.CharField(max_length=institution_name.max_length, label=_("Institution name"), help_text=institution_name.help_text)
    code = forms.CharField(max_length=institution_code.max_length, label=_("Institution abbreviation"), help_text=institution_code.help_text)
    region = forms.ModelChoiceField(
        queryset=Region.objects.all(),
        label=_("Institution region"),
        help_text=institution_region.help_text,
    )
    key = forms.CharField(widget=forms.HiddenInput(), required=False)

    field_order = ('name', 'code', 'teams_requested', 'adjudicators_requested')

    def __init__(self, tournament, *args, key=None, invitation=None, **kwargs):
        self.tournament = tournament
        self.invitation = invitation
        super().__init__(*args, **kwargs)
        if key:
            self.fields['key'].initial = key
        self.add_question_fields()

        if not self.tournament.pref('reg_institution_slots') or invitation:
            self.fields.pop('teams_requested', None)
            self.fields.pop('adjudicators_requested', None)
        if invitation:
            self.initial.setdefault('name', invitation.institution_name or '')

        if 'region' not in self.tournament.pref('reg_institution_fields'):
            self.fields.pop('region')

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        existing_institution = TournamentInstitution.objects.filter(tournament=self.tournament, institution__name__iexact=name).exists()
        if existing_institution:
            raise forms.ValidationError(_("An institution with this name is already registered for this tournament."))
        return name

    class Meta:
        model = TournamentInstitution
        exclude = ('tournament', 'institution', 'teams_allocated', 'adjudicators_allocated')

    def save(self):
        self.cleaned_data.pop('key', None)
        name = self.cleaned_data.pop('name')
        code = self.cleaned_data.pop('code')
        region = self.cleaned_data.pop('region', None)
        inst, created = Institution.objects.get_or_create(
            name=name,
            defaults={'region': region, 'code': code},
        )

        obj = super().save(commit=False)
        obj.institution = inst
        obj.tournament = self.tournament
        if self.invitation:
            obj.teams_allocated = self.invitation.teams_allocated or 0
            obj.adjudicators_allocated = self.invitation.adjudicators_allocated or 0
        obj.save()
        self.save_answers(obj)

        return obj


class InstitutionCoachForm(CustomQuestionsFormMixin, forms.ModelForm):
    key = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, tournament, *args, key=None, **kwargs):
        self.tournament = tournament
        super().__init__(*args, **kwargs)
        if key:
            self.fields['key'].initial = key
        self.add_question_fields()

    class Meta:
        model = Coach
        fields = ('name', 'email')
        labels = {
            'name': _('Name of primary contact'),
        }

    def save(self):
        self.cleaned_data.pop('key', None)
        obj = super().save()
        populate_url_keys([obj])
        self.save_answers(obj, replace_existing=bool(obj.pk))
        return obj


class InstitutionEditForm(forms.Form):
    """Wrapper form for admin editing of institution + primary contact (coach) with separate sections."""

    def __init__(self, tournament, t_inst, data=None, read_only=False, *args, **kwargs):
        super().__init__(data=data, *args, **kwargs)
        self.tournament = tournament
        self.t_inst = t_inst
        self.read_only = read_only
        coach = t_inst.coach_set.first()

        inst_initial = {
            'name': t_inst.institution.name,
            'code': t_inst.institution.code,
            'region': t_inst.institution.region,
            **get_answers_initial(t_inst),
        }

        coach_initial = get_answers_initial(coach) if coach else {}

        self.institution_form = TournamentInstitutionForm(
            tournament,
            instance=t_inst,
            initial=inst_initial,
            data=data,
            prefix='institution',
        )
        self.coach_form = InstitutionCoachForm(
            tournament,
            instance=coach,
            initial=coach_initial,
            data=data,
            prefix='coach',
        )

        if read_only:
            for form in (self.institution_form, self.coach_form):
                for field in form.fields.values():
                    field.disabled = True

    def is_valid(self):
        return self.institution_form.is_valid() and self.coach_form.is_valid()


class TeamForm(CustomQuestionsFormMixin, forms.ModelForm):

    key = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, tournament, *args, institution=None, key=None, **kwargs):
        self.tournament = tournament
        self.institution = institution
        super().__init__(*args, **kwargs)

        self.fields['tournament'].initial = self.tournament
        if key:
            self.fields['key'].initial = key

        use_inst_field = self.fields['use_institution_prefix']
        use_inst_field.initial = bool(self.institution)

        if self.tournament.pref('team_name_generator') != 'user' and self.institution:
            self.fields.pop('reference')

        if not self.institution or 'use_institution_prefix' not in self.tournament.pref('reg_team_fields') or self.tournament.pref('team_name_generator') != 'user':
            use_inst_field.widget = forms.HiddenInput()

        for field in {'code_name', 'break_categories', 'seed', 'emoji'} - set(self.tournament.pref('reg_team_fields')):
            self.fields.pop(field)

        if self.institution is not None:
            self.fields['institution'].widget = forms.HiddenInput()
            self.fields['institution'].initial = self.institution

        if 'emoji' in self.fields:
            used_emoji = Team.objects.all_with_unconfirmed.filter(tournament=self.tournament, emoji__isnull=False).values_list('emoji', flat=True)
            self.fields['emoji'].choices = [e for e in EMOJI_RANDOM_FIELD_CHOICES if e[0] not in used_emoji]
            self.fields['emoji'].initial = random.choice(self.fields['emoji'].choices)[0]

        if 'seed' in self.fields and self.tournament.pref('show_seed_in_importer') == 'title':
            self.fields['seed'] = forms.ChoiceField(required=False, label=self.fields['seed'].label, choices=(
                (0, _("Unseeded")),
                (1, _("Free seed")),
                (2, _("Half seed")),
                (3, _("Full seed")),
            ), help_text=self.fields['seed'].help_text)

        if 'break_categories' in self.fields:
            bcs = self.tournament.breakcategory_set.exclude(is_general=True)
            if len(bcs) == 0:
                self.fields.pop('break_categories')
            else:
                self.fields['break_categories'].queryset = bcs

        self.add_question_fields()

    class Meta:
        model = Team
        fields = ('tournament', 'reference', 'institution', 'use_institution_prefix', 'code_name', 'emoji', 'seed', 'break_categories')
        labels = {
            'reference': _("Team name (excluding institution)"),
        }
        widgets = {
            'tournament': forms.HiddenInput(),
        }

    def save(self):
        self.instance.tournament = self.tournament
        if self.tournament.pref('registration_confirmation') == 'always' or (self.tournament.pref('registration_confirmation') == 'open' and self.institution is None):
            self.instance.registration_status = RegistrationStatus.UNCONFIRMED

        if self.institution:
            self.instance.institution = self.institution

        if 'use_institution_prefix' not in self.tournament.pref('reg_team_fields') and self.tournament.pref('team_name_generator') != 'user':
            self.instance.use_institution_prefix = bool(self.institution)

        if not self.cleaned_data.get('emoji', None):
            self.instance.emoji = pick_unused_emoji(tournament_id=self.tournament.id)[0]

        obj = super().save()
        self.save_answers(obj)

        obj.break_categories.set(self.tournament.breakcategory_set.filter(is_general=True))
        if obj.institution:
            obj.teaminstitutionconflict_set.create(institution=obj.institution)
        return obj


class SpeakerForm(CustomQuestionsFormMixin, forms.ModelForm):

    key = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, team, key, *args, tournament=None, **kwargs):
        self.team = team
        self.tournament = team.tournament
        super().__init__(*args, **kwargs)

        self.fields['key'].initial = key

        if not (self.tournament.pref('team_name_generator') == 'initials' or self.tournament.pref('code_name_generator') == 'last_names'):
            self.fields.pop('last_name')

        for field in ({'email', 'phone', 'gender', 'categories'} - set(self.tournament.pref('reg_speaker_fields'))):
            self.fields.pop(field)

        if 'categories' in self.fields:
            self.fields['categories'].queryset = self.tournament.speakercategory_set.filter(public=True)

        self.add_question_fields()

    class Meta:
        model = Speaker
        fields = ('name', 'last_name', 'email', 'phone', 'gender', 'categories')
        labels = {
            'name': _("Full name for tab"),
        }

    def save(self, commit=True):
        self.instance.team = self.team
        obj = super().save()
        populate_url_keys([obj])
        self.save_answers(obj)
        return obj


class AdjudicatorForm(CustomQuestionsFormMixin, forms.ModelForm):

    key = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, tournament, *args, institution=None, key=None, **kwargs):
        self.tournament = tournament
        self.institution = institution
        super().__init__(*args, **kwargs)

        if key:
            self.fields['key'].initial = key

        for field in ({'email', 'phone', 'gender'} - set(self.tournament.pref('reg_adjudicator_fields'))):
            self.fields.pop(field)

        if self.institution is not None:
            self.fields['institution'].widget = forms.HiddenInput()
            self.fields['institution'].initial = self.institution

        self.add_question_fields()

    class Meta:
        model = Adjudicator
        fields = ('name', 'institution', 'email', 'phone', 'gender')
        labels = {
            'name': _("Full name for tab"),
        }

    def save(self):
        self.instance.tournament = self.tournament
        if self.tournament.pref('registration_confirmation') == 'always' or (self.tournament.pref('registration_confirmation') == 'open' and self.institution is None):
            self.instance.registration_status = RegistrationStatus.UNCONFIRMED
        if self.institution:
            self.instance.institution = self.institution

        obj = super().save()
        populate_url_keys([obj])
        self.save_answers(obj)

        if obj.institution:
            obj.adjudicatorinstitutionconflict_set.create(institution=obj.institution)
        return obj


class ParticipantAllocationForm(forms.Form):
    """Updates the number of participants allocated for each institution"""

    def __init__(self, tournament, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tournament = tournament
        self._create_and_initialise_fields()

    @staticmethod
    def _fieldname_teams_allocated(institution):
        return 'teams_alloc_%(institution)d' % {'institution': institution.id}

    @staticmethod
    def _fieldname_adjs_allocated(institution):
        return 'adjs_alloc_%(institution)d' % {'institution': institution.id}

    def get_teams_allocated_field(self, institution):
        return self[self._fieldname_teams_allocated(institution)].as_widget(attrs={'class': 'form-control'})

    def get_adjs_allocated_field(self, institution):
        return self[self._fieldname_adjs_allocated(institution)].as_widget(attrs={'class': 'form-control'})

    def _create_and_initialise_fields(self):
        for t_inst in self.tournament.tournamentinstitution_set.select_related('institution').all():
            institution = t_inst.institution
            self.fields[self._fieldname_teams_allocated(institution)] = forms.IntegerField(min_value=0, required=False)
            self.initial[self._fieldname_teams_allocated(institution)] = t_inst.teams_allocated
            self.fields[self._fieldname_adjs_allocated(institution)] = forms.IntegerField(min_value=0, required=False)
            self.initial[self._fieldname_adjs_allocated(institution)] = t_inst.adjudicators_allocated

    def save(self):
        qs = self.tournament.tournamentinstitution_set.select_related('institution').all()
        for t_inst in qs:
            institution = t_inst.institution
            t_inst.teams_allocated = self.cleaned_data[self._fieldname_teams_allocated(institution)]
            t_inst.adjudicators_allocated = self.cleaned_data[self._fieldname_adjs_allocated(institution)]
        TournamentInstitution.objects.bulk_update(qs, ['teams_allocated', 'adjudicators_allocated'])


class SlotTransferRequestForm(forms.Form):
    receiving_institution = forms.ModelChoiceField(
        queryset=TournamentInstitution.objects.none(),
        label=_("Institution"),
        required=False,
        empty_label=_("Institution not listed"),
    )
    receiving_institution_name = forms.CharField(
        max_length=100,
        label=_("Institution name"),
        required=False,
        help_text=_("If the institution is not listed above, enter the name of the receiving institution here."),
    )
    receiving_institution_email = forms.EmailField(
        label=_("Contact email"),
        required=False,
        help_text=_("If the institution is not listed above, enter the contact email for the receiving institution here."),
    )
    teams_to_transfer = forms.IntegerField(
        min_value=0,
        initial=0,
        label=_("Team slots to transfer"),
    )
    adjudicators_to_transfer = forms.IntegerField(
        min_value=0,
        initial=0,
        label=_("Adjudicator slots to transfer"),
    )

    def __init__(self, source_tournament_institution, *args, **kwargs):
        self.source_tournament_institution = source_tournament_institution
        self.tournament = source_tournament_institution.tournament
        super().__init__(*args, **kwargs)
        other_tis = TournamentInstitution.objects.filter(
            tournament=self.tournament,
        ).exclude(
            pk=source_tournament_institution.pk,
        ).select_related('institution').order_by('institution__name')
        self.fields['receiving_institution'].queryset = other_tis

        self.fields['teams_to_transfer'].widget.attrs.update({'max': source_tournament_institution.teams_allocated})
        self.fields['adjudicators_to_transfer'].widget.attrs.update({'max': source_tournament_institution.adjudicators_allocated})

    def clean(self):
        data = super().clean()
        if not data.get('receiving_institution'):
            if not (data.get('receiving_institution_name') or '').strip():
                self.add_error('receiving_institution_name', _("Please enter the name of the receiving institution."))
            if not (data.get('receiving_institution_email') or '').strip():
                self.add_error('receiving_institution_email', _("Please enter the contact email for the receiving institution."))

        teams = data['teams_to_transfer']
        adjs = data['adjudicators_to_transfer']
        if teams <= 0 and adjs <= 0:
            self.add_error('teams_to_transfer', _("Transfer at least one team or adjudicator slot."))
        if teams > self.source_tournament_institution.teams_allocated:
            self.add_error('teams_to_transfer', _("You cannot transfer more team slots than you have."))
        if adjs > self.source_tournament_institution.adjudicators_allocated:
            self.add_error('adjudicators_to_transfer', _("You cannot transfer more adjudicator slots than you have."))
        return data

    def save(self):
        data = self.cleaned_data
        if data['receiving_institution']:
            return SlotTransferRequest.objects.create(
                tournament=self.tournament,
                source_tournament_institution=self.source_tournament_institution,
                teams_transferred=data['teams_to_transfer'],
                adjudicators_transferred=data['adjudicators_to_transfer'],
                receiving_institution=data['receiving_institution'],
                status=SlotTransferRequest.Status.PENDING,
            )
        else:
            SlotTransferRequest.objects.create(
                tournament=self.tournament,
                source_tournament_institution=self.source_tournament_institution,
                teams_transferred=data['teams_to_transfer'],
                adjudicators_transferred=data['adjudicators_to_transfer'],
                receiving_institution_name=data['receiving_institution_name'],
                receiving_institution_email=data['receiving_institution_email'],
                status=SlotTransferRequest.Status.PENDING,
            )
