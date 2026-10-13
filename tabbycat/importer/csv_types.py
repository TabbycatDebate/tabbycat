"""Registered CSV object types.

Each type owns its column vocabulary, preview form, normalization, duplicate key,
dependencies and save operation. The wizard only orchestrates these hooks.
"""

import re
from pathlib import PurePath

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from actionlog.models import ActionLogEntry
from checkins.models import PersonIdentifier
from participants.emoji import set_emoji
from participants.models import Team
from participants.utils import populate_code_names
from privateurls.utils import populate_url_keys
from tournaments.models import Tournament

from .importers.base import convert_bool


class DependencyPendingError(Exception):
    pass


class DependencyBlockedError(Exception):
    pass


def normalized_header(header):
    return re.sub(r'\W+', '_', header.strip().casefold()).strip('_')


class CSVObjectType:
    key = None
    label = None
    filename_words = ()
    templates = ()
    targets = ()
    aliases = {}
    required_targets = ()
    priority = 0
    identity_fields = ()
    name_field = 'name'

    def mapping_choices(self, source):
        return list(self.targets)

    def guess_column(self, header):
        name = normalized_header(header)
        return self.aliases.get(name, name)

    def form_options(self, values):
        return {}

    def preview_field_count(self, targets):
        return len(self.targets) + 1

    def initial(self, row, context):
        return row['values'].copy()

    def serialize(self, data):
        return data.copy()

    def duplicate_key(self, data):
        return (self.key, *(data[field] for field in self.identity_fields))

    def restore_preview(self, data, prefix, initial):
        pass

    def resolve_preview(self, form, forms):
        pass

    def preview_summary(self, form):
        return {'name': form[self.name_field].value() or '', 'related': ''}

    def preview_dependencies(self, data):
        return ()

    def object_counts(self, form):
        return {self.key: 1}

    def additional_objects(self, form):
        return ()

    def dependencies(self, tournament, data, rows):
        return {}

    def save(self, form, user, **dependencies):
        raise NotImplementedError


class TeamCSVType(CSVObjectType):
    key = 'team'
    label = _('Teams')
    filename_words = ('team', 'teams')
    templates = (
        ('teams', _('Teams'), ('reference', 'institution', 'use_institution_prefix', 'seed')),
        ('teams-with-speakers', _('Teams with speakers'), ('reference', 'institution', 'use_institution_prefix', 'seed',
            'speaker_1_name', 'speaker_1_email', 'speaker_2_name', 'speaker_2_email')),
    )
    targets = [('reference', _('Team name / suffix')), ('institution', _('Institution name or code')),
        ('use_institution_prefix', _('Prefix team name with institution')), ('seed', _('Seed'))]
    aliases = {'team': 'reference', 'team_name': 'reference', 'name': 'reference', 'institution_name': 'institution',
        'institution_code': 'institution', 'university': 'institution', 'prefix': 'use_institution_prefix'}
    required_targets = ('reference',)
    identity_fields = ('institution', 'reference')
    name_field = 'reference'

    @property
    def form_class(self):
        from .csv_forms import CSVTeamForm
        return CSVTeamForm

    def guess_column(self, header):
        name = super().guess_column(header)
        name = re.sub(r'^speaker_?(\d+)(?:_(name|email))?$', lambda m: f'speaker_{m[1]}_{m[2] or "name"}', name)
        return {'speaker': 'speaker_1_name', 'speaker_name': 'speaker_1_name', 'speaker_email': 'speaker_1_email'}.get(name, name)

    def form_options(self, values):
        numbers = [int(match[1]) for field in values if (match := re.fullmatch(r'speaker_(\d+)_(?:name|email)', field))]
        return {'slots': max(numbers, default=0)}

    def mapping_choices(self, source):
        # Offer slots for arbitrarily named columns too; actual preview fields are
        # determined only by the columns the administrator maps.
        detected = self.form_options({self.guess_column(header): '' for header in source['headers']})['slots']
        slots = min(100, max(len(source['headers']) - 1, detected))
        return list(self.targets) + [
            (f'speaker_{number}_{field}', _('Speaker %(number)d — %(field)s') % {'number': number, 'field': label})
            for number in range(1, slots + 1) for field, label in [('name', _('Name')), ('email', _('Email'))]]

    def preview_field_count(self, targets):
        return len(self.targets) + self.form_options(targets)['slots'] * 2 + 1

    def initial(self, row, context):
        values = super().initial(row, context)
        values['institution'] = context.institutions.get((row['file_index'], values.get('institution', '')))
        prefix = values.get('use_institution_prefix', '')
        try:
            values['use_institution_prefix'] = convert_bool(prefix) if prefix else False
        except ValueError:
            values['use_institution_prefix'] = prefix
        return values

    def serialize(self, data):
        return {**data, 'institution': data['institution'].pk if data['institution'] else ''}

    def preview_summary(self, form):
        institution = form.cleaned_data.get('institution')
        related = str(institution) if institution else _('Unaffiliated')
        raw = form['institution'].value()
        if isinstance(raw, str) and raw.startswith('unresolved:'):
            related = raw.split(':', 1)[1]
        return {'name': form['reference'].value() or '', 'related': related}

    def object_counts(self, form):
        return {'team': 1, 'speaker': sum(bool(form.cleaned_data.get(f'speaker_{n}_name')) for n in range(1, form.slots + 1))}

    @transaction.atomic
    def save(self, form, user, **dependencies):
        team = form.save(commit=False)
        team.tournament = form.tournament
        team.save()
        speakers = []
        for number in range(1, form.slots + 1):
            name = form.cleaned_data.get(f'speaker_{number}_name')
            if name:
                speaker = team.speaker_set.create(name=name, email=form.cleaned_data.get(f'speaker_{number}_email') or None)
                PersonIdentifier.objects.create(person=speaker)
                speakers.append(speaker)
        populate_url_keys(speakers)
        populate_code_names(speakers)
        team.break_categories.set(team.tournament.breakcategory_set.filter(is_general=True))
        if team.institution:
            team.teaminstitutionconflict_set.create(institution=team.institution)
        set_emoji([team], team.tournament)
        ActionLogEntry.objects.log(type=ActionLogEntry.ActionType.TEAM_CREATE,
            tournament=team.tournament, content_object=team, user=user)
        return team


class SpeakerCSVType(CSVObjectType):
    key = 'speaker'
    label = _('Speakers')
    filename_words = ('speaker', 'speakers')
    templates = (('speakers', _('Separate speakers'), ('name', 'email', 'team_name', 'institution', 'use_institution_prefix')),)
    targets = [('name', _('Speaker name')), ('email', _('Speaker email')),
        ('team', _('Team name / suffix')), ('institution', _('Institution name or code')),
        ('use_institution_prefix', _('Prefix team name with institution'))]
    # Anorak speakers.csv identifies teams by team_name and institution.
    aliases = {'speaker_name': 'name', 'speaker': 'name', 'speaker_email': 'email', 'team_name': 'team',
        'institution_name': 'institution', 'institution_code': 'institution', 'university': 'institution', 'prefix': 'use_institution_prefix'}
    required_targets = ('name', 'team')
    priority = 1
    identity_fields = ('team', 'name')

    @property
    def form_class(self):
        from .csv_forms import CSVSpeakerForm
        return CSVSpeakerForm

    def initial(self, row, context):
        values = CSV_TYPES['team'].initial(row, context)
        values['team_name'] = values.get('team', '')
        values['team'] = context.match_team(row)
        return values

    def restore_preview(self, data, prefix, initial):
        if prefix + 'team_name' not in data:
            for field in ('team_name', 'institution', 'use_institution_prefix'):
                value = initial.get(field)
                data[prefix + field] = str(value) if value is not None else ''
            if not data.get(prefix + 'team'):
                data[prefix + 'team'] = initial['team']

    def preview_field_count(self, targets):
        return 7

    def serialize(self, data):
        return {**data, 'institution': data['institution'].pk if data['institution'] else ''}

    def duplicate_key(self, data):
        team = (data['institution'], data['team_name']) if data['team'] == 'new' else data['team']
        return self.key, team, data['name']

    def resolve_preview(self, form, forms):
        from .csv_forms import CSVTeamForm
        data = form.cleaned_data
        if data['team'] != 'new':
            return
        matches = [index for index, other in enumerate(forms)
            if isinstance(other, CSVTeamForm) and not other.errors and not other.cleaned_data.get('DELETE') and
            other.cleaned_data['institution'] == data['institution'] and other.cleaned_data['reference'] == data['team_name']]
        if len(matches) == 1:
            data['team'] = f'row:{matches[0]}'
        elif matches:
            form.add_error('team', _('Choose which uploaded team this speaker belongs to.'))
        for other in forms:
            values = other.cleaned_data
            if (other is not form and not other.errors and not values.get('DELETE') and values.get('team') == 'new' and
                    values.get('institution') == data['institution'] and values.get('team_name') == data['team_name'] and
                    values.get('use_institution_prefix') != data['use_institution_prefix']):
                form.add_error('use_institution_prefix', _('Use the same prefix setting for speakers on the same new team.'))
                break

    def preview_summary(self, form):
        token = form.cleaned_data.get('team', form['team'].value())
        if token == 'new':
            related = _('New team: %(name)s') % {'name': form['team_name'].value() or ''}
        else:
            related = dict(form.fields['team'].choices).get(token, _('Choose a team'))
        return {'name': form['name'].value() or '', 'related': related}

    def additional_objects(self, form):
        data = form.cleaned_data
        if data.get('team') == 'new' and not Team.objects.all_with_unconfirmed.filter(tournament=form.tournament,
                institution=data['institution'], reference=data['team_name']).exists():
            return (('team', (data['institution'].pk if data['institution'] else None, data['team_name'])),)
        return ()

    def preview_dependencies(self, data):
        token = data.get('team', '')
        return (int(token.split(':')[1]),) if token.startswith('row:') else ()

    def dependencies(self, tournament, data, rows):
        token = data['team']
        if token == 'new':
            return {'team': None}
        if token.startswith('row:'):
            dependency = rows[int(token.split(':')[1])]
            if dependency['status'] == 'pending':
                raise DependencyPendingError(_('Import the linked team first.'))
            team_id = dependency.get('object_id', dependency.get('team_id')) if dependency['status'] == 'imported' else None
        else:
            team_id = token.split(':')[1]
        team = Team.objects.all_with_unconfirmed.filter(pk=team_id, tournament=tournament).first()
        if team is None:
            raise DependencyBlockedError(_('The linked team was skipped, failed, or no longer exists.'))
        return {'team': team}

    @transaction.atomic
    def save(self, form, user, *, team):
        if team is None:
            # Serialize implicit team creation, including unaffiliated teams whose
            # NULL institution cannot be protected by a simple unique constraint.
            Tournament.objects.select_for_update().get(pk=form.tournament.pk)
            data = form.cleaned_data
            matches = list(Team.objects.all_with_unconfirmed.filter(tournament=form.tournament,
                institution=data['institution'], reference=data['team_name']))
            if len(matches) > 1:
                raise ValidationError(_('More than one team matches this name and institution.'))
            if matches:
                team = matches[0]
            else:
                kind = CSV_TYPES['team']
                team_form = kind.form_class(form.tournament, data={'reference': data['team_name'],
                    'institution': data['institution'].pk if data['institution'] else '',
                    'use_institution_prefix': str(data['use_institution_prefix']), 'seed': ''})
                if not team_form.is_valid():
                    raise ValidationError(_('The new team could not be validated.'))
                team = kind.save(team_form, user)
        if team.tournament_id != form.tournament.pk:
            raise ValidationError(_('The team belongs to another tournament.'))
        if team.speaker_set.filter(name=form.cleaned_data['name']).exists():
            raise ValidationError(_('A speaker with this name already belongs to this team.'))
        speaker = team.speaker_set.create(name=form.cleaned_data['name'], email=form.cleaned_data.get('email') or None)
        PersonIdentifier.objects.create(person=speaker)
        populate_url_keys([speaker])
        populate_code_names([speaker])
        ActionLogEntry.objects.log(type=ActionLogEntry.ActionType.SPEAKER_CREATE,
            tournament=form.tournament, content_object=speaker, user=user)
        return speaker


CSV_TYPES = {}


def register_csv_type(csv_type):
    if csv_type.key in CSV_TYPES:
        raise ValueError(f'CSV type {csv_type.key!r} is already registered')
    CSV_TYPES[csv_type.key] = csv_type
    return csv_type


register_csv_type(TeamCSVType())
register_csv_type(SpeakerCSVType())


def guess_file_type(filename):
    stem = PurePath(filename).stem.casefold()
    templates = [kind.key for kind in CSV_TYPES.values() if any(key == stem for key, label, columns in kind.templates)]
    if len(templates) == 1:
        return templates[0]
    words = set(re.split(r'\W+|_', stem))
    matches = [kind.key for kind in CSV_TYPES.values() if words.intersection(kind.filename_words)]
    return matches[0] if len(matches) == 1 else ''
