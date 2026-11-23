"""Editable participant rows, independent of the CSV type registry."""

from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _

from participants.models import Institution, Speaker, Team

from .csv_model_forms import CSVReferenceField
from .forms import BaseTournamentObjectDetailsForm
from .importers.base import convert_bool
from .participant_services import team_reference
from .references import ImportReferences, reference_value


class CachedInstitutionField(forms.ModelChoiceField):
    """Validate against the same snapshot used to render institution choices."""

    def to_python(self, value):
        if value in self.empty_values:
            return None
        try:
            if isinstance(value, str) and value.startswith('row:'):
                return self.references.get_object('institution', value)
            key = value.pk if isinstance(value, Institution) else int(value)
            return self.references.institutions_by_id[key]
        except (ValueError, TypeError, KeyError, ObjectDoesNotExist):
            raise forms.ValidationError(self.error_messages['invalid_choice'], code='invalid_choice', params={'value': value})


def configure_institution_field(field, initial, references):
    field.label_from_instance = lambda inst: f'{inst.name} ({inst.code})'
    field.empty_label = _('Unaffiliated')
    field.references = references
    field.choices = [('', field.empty_label), *references.institution_choices]
    if isinstance(initial, str) and initial.startswith('unresolved:'):
        field.choices = [*field.choices, (initial, _('Unmatched: %(value)s') % {'value': initial.split(':', 1)[1]})]
        field.error_messages['invalid_choice'] = _('Choose an existing institution, select Unaffiliated, or skip this row.')


class CSVSpeakerForm(forms.Form):
    name = forms.CharField(max_length=Speaker._meta.get_field('name').max_length, label=_('Speaker name'))
    email = forms.EmailField(required=False, max_length=Speaker._meta.get_field('email').max_length, label=_('Email'))
    team = forms.ChoiceField(label=_('Team'))
    institution = CachedInstitutionField(queryset=Institution.objects.all(), required=False, label=_('Institution for new team'))
    team_name = forms.CharField(required=False, max_length=150, label=_('New team name / suffix'))
    use_institution_prefix = forms.TypedChoiceField(required=False, empty_value=False,
        coerce=lambda value: convert_bool(str(value)), choices=[('False', _('No')), ('True', _('Yes'))],
        initial='False', label=_('Prefix new team name with institution'))

    def __init__(self, tournament, *args, slots=0, team_choices=(), references=None, participant_fields=(), **kwargs):
        super().__init__(*args, **kwargs)
        self.tournament = tournament
        self.references = references or ImportReferences(tournament)
        if self.data.get(self.add_prefix('team')) == 'removed':
            self.fields['team'].error_messages['invalid_choice'] = _(
                'The referenced team file was removed. Choose another team or create a team from its name and institution.')
        self.fields['team'].choices = [('', _('Choose a team')), ('new', _('Create or use team from the name and institution below'))] + list(team_choices)
        configure_institution_field(self.fields['institution'], self.initial.get('institution'), self.references)
        for name in participant_fields:
            if name == 'categories':
                self.fields[name] = CSVReferenceField('speaker_category', self.references, multiple=True, required=False,
                    label=_('Speaker categories'), initial=self.initial.get(name))
            else:
                self.fields[name] = Speaker._meta.get_field(name).formfield()
                self.fields[name].required = False

    def clean(self):
        data = super().clean()
        token = data.get('team', '')
        if token == 'new':
            if not data.get('team_name'):
                self.add_error('team_name', _('Enter the name of the team to create.'))
            if data.get('use_institution_prefix') and not data.get('institution'):
                self.add_error('institution', _('Select an institution to use an institutional prefix.'))
        if token.startswith('existing:') and data.get('name'):
            if (int(token.split(':')[1]), data['name']) in self.references.speaker_names:
                self.add_error('name', _('A speaker with this name already belongs to this team. Skip or correct this row.'))
        return data


class CSVTeamForm(BaseTournamentObjectDetailsForm):
    use_institution_prefix = forms.TypedChoiceField(coerce=lambda value: convert_bool(str(value)), choices=[('False', _('No')), ('True', _('Yes'))],
        initial='False', label=_('Prefix team name with institution'))

    class Meta:
        model = Team
        fields = ('reference', 'short_reference', 'institution', 'use_institution_prefix', 'seed')
        field_classes = {'institution': CachedInstitutionField}

    def __init__(self, tournament, *args, slots=0, team_choices=(), references=None, participant_fields=(), **kwargs):
        super().__init__(tournament, *args, **kwargs)
        self.references = references or ImportReferences(tournament)
        self.slots = slots
        configure_institution_field(self.fields['institution'], self.initial.get('institution'), self.references)
        if 'break_categories' in participant_fields:
            self.fields['break_categories'] = CSVReferenceField('break_category', self.references, multiple=True, required=False,
                label=_('Break categories'), initial=self.initial.get('break_categories'))
        for n in range(1, slots + 1):
            self.fields[f'speaker_{n}_name'] = forms.CharField(required=False,
                max_length=Speaker._meta.get_field('name').max_length, label=_('Speaker %(number)d name') % {'number': n})
            self.fields[f'speaker_{n}_email'] = forms.EmailField(required=False,
                max_length=Speaker._meta.get_field('email').max_length, label=_('Speaker %(number)d email') % {'number': n})
            if f'speaker_{n}_gender' in participant_fields:
                self.fields[f'speaker_{n}_gender'] = Speaker._meta.get_field('gender').formfield()
            if f'speaker_{n}_category' in participant_fields:
                self.fields[f'speaker_{n}_category'] = CSVReferenceField('speaker_category', self.references, multiple=True, required=False,
                    label=_('Speaker %(number)d categories') % {'number': n}, initial=self.initial.get(f'speaker_{n}_category'))

    def clean(self):
        data = super().clean()
        data['short_reference'] = data.get('short_reference') or team_reference(data.get('reference', ''))
        self.instance.short_reference = data['short_reference']
        for n in range(1, self.slots + 1):
            name, email = data.get(f'speaker_{n}_name'), data.get(f'speaker_{n}_email')
            if email and not name:
                self.add_error(f'speaker_{n}_name', _('Enter a name for this speaker or clear the email.'))
        if 'reference' in data and 'institution' in data and self.references.team_identities.get(
                (reference_value(data['institution']) or None, data['reference'])):
            self.add_error('reference', _('A team with this name and institution already exists. Skip this row or change its name.'))
        return data

    def _get_validation_exclusions(self):
        # The field validates institutions against the shared snapshot; tournament
        # is supplied by the view. Identity duplicates are checked in clean().
        return super()._get_validation_exclusions() | {'institution', 'tournament'}
