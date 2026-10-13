"""Editable participant rows, independent of the CSV type registry."""

from django import forms
from django.utils.translation import gettext_lazy as _

from participants.models import Institution, Speaker, Team

from .forms import BaseTournamentObjectDetailsForm
from .importers.base import convert_bool
from .participant_services import team_reference
from .references import ImportReferences


class CachedInstitutionField(forms.ModelChoiceField):
    """Validate against the same snapshot used to render institution choices."""

    def to_python(self, value):
        if value in self.empty_values:
            return None
        try:
            key = value.pk if isinstance(value, Institution) else int(value)
            return self.references.institutions_by_id[key]
        except (ValueError, TypeError, KeyError):
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

    def __init__(self, tournament, *args, slots=0, team_choices=(), references=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tournament = tournament
        self.references = references or ImportReferences(tournament)
        self.fields['team'].choices = [('', _('Choose a team')), ('new', _('Create or use team from the name and institution below'))] + list(team_choices)
        configure_institution_field(self.fields['institution'], self.initial.get('institution'), self.references)

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
        fields = ('reference', 'institution', 'use_institution_prefix', 'seed')
        field_classes = {'institution': CachedInstitutionField}

    def __init__(self, tournament, *args, slots=0, team_choices=(), references=None, **kwargs):
        super().__init__(tournament, *args, **kwargs)
        self.references = references or ImportReferences(tournament)
        self.slots = slots
        configure_institution_field(self.fields['institution'], self.initial.get('institution'), self.references)
        for n in range(1, slots + 1):
            self.fields[f'speaker_{n}_name'] = forms.CharField(required=False,
                max_length=Speaker._meta.get_field('name').max_length, label=_('Speaker %(number)d name') % {'number': n})
            self.fields[f'speaker_{n}_email'] = forms.EmailField(required=False,
                max_length=Speaker._meta.get_field('email').max_length, label=_('Speaker %(number)d email') % {'number': n})

    def clean(self):
        data = super().clean()
        self.instance.short_reference = team_reference(data.get('reference', ''))
        for n in range(1, self.slots + 1):
            name, email = data.get(f'speaker_{n}_name'), data.get(f'speaker_{n}_email')
            if email and not name:
                self.add_error(f'speaker_{n}_name', _('Enter a name for this speaker or clear the email.'))
        if 'reference' in data and 'institution' in data and self.references.team_identities.get(
                (data['institution'].pk if data['institution'] else None, data['reference'])):
            self.add_error('reference', _('A team with this name and institution already exists. Skip this row or change its name.'))
        return data

    def _get_validation_exclusions(self):
        # The field validates institutions against the shared snapshot; tournament
        # is supplied by the view. Identity duplicates are checked in clean().
        return super()._get_validation_exclusions() | {'institution', 'tournament'}
