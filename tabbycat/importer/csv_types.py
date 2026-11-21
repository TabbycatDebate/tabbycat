"""CSV type registry and team/speaker mapping, preview and save hooks."""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from pathlib import PurePath
from typing import Any, TYPE_CHECKING

from django.core.exceptions import ValidationError
from django.db import transaction
from django.forms import BaseForm
from django.utils.translation import gettext_lazy as _, ngettext_lazy

from actionlog.models import ActionLogEntry
from checkins.models import PersonIdentifier
from participants.models import Speaker, Team
from participants.utils import populate_code_names
from privateurls.utils import populate_url_keys
from tournaments.models import Tournament

from .csv_base_types import CSVObjectType, DependencyBlockedError, reference_dependencies
from .csv_model_types import model_csv_types
from .csv_row_forms import CSVSpeakerForm, CSVTeamForm
from .csv_typing import AdditionalObject, CSVResultRow, CSVRow, CSVSource, DisplayLabel, DuplicateKey, ExecutionDependencies, FormOptions, PreviewSummary, RowData, SerializedRowData
from .importers.base import convert_bool
from .importers.lookups import TournamentDataLookups
from .participant_services import initialize_teams
from .references import reference_value

if TYPE_CHECKING:
    from django.contrib.auth.base_user import AbstractBaseUser
    from django.http import QueryDict

    from .csv_pipeline import CSVImportContext
    from .references import ImportReferences


class TeamCSVType(CSVObjectType[CSVTeamForm, Team]):
    count_label = ngettext_lazy('Team', 'Teams', 'count')
    key = 'team'
    label = _('Teams')
    filename_words = ('team', 'teams')
    templates = (
        ('teams', _('Teams'), ('reference', 'institution', 'use_institution_prefix', 'seed')),
        ('teams-with-speakers', _('Teams with speakers'), ('reference', 'institution', 'use_institution_prefix', 'seed',
            'speaker_1_name', 'speaker_1_email', 'speaker_2_name', 'speaker_2_email')),
    )
    targets = [('reference', _('Team name / suffix')), ('institution', _('Institution name or code')),
        ('use_institution_prefix', _('Prefix team name with institution')), ('seed', _('Seed')),
        ('short_reference', _('Short team name / suffix')), ('break_categories', _('Break categories'))]
    aliases = {'team': 'reference', 'team_name': 'reference', 'name': 'reference', 'institution_name': 'institution',
        'institution_code': 'institution', 'university': 'institution', 'prefix': 'use_institution_prefix', 'break_category': 'break_categories'}
    required_targets = ('reference',)
    identity_fields = ('institution', 'reference')
    name_field = 'reference'
    reference_fields = ('institution', 'break_categories')

    form_class = CSVTeamForm

    def guess_column(self, header: str) -> str:
        name = super().guess_column(header)
        name = re.sub(r'^speaker_?(\d+)(?:_(name|email|gender|category))?$', lambda m: f'speaker_{m[1]}_{m[2] or "name"}', name)
        return {'speaker': 'speaker_1_name', 'speaker_name': 'speaker_1_name', 'speaker_email': 'speaker_1_email'}.get(name, name)

    def form_options(self, values: Iterable[str]) -> FormOptions:
        numbers = [int(match[1]) for field in values if (match := re.fullmatch(r'speaker_(\d+)_(?:name|email|gender|category)', field))]
        return {'slots': max(numbers, default=0), 'participant_fields': tuple(field for field in values
            if field == 'break_categories' or field.endswith(('_gender', '_category')))}

    def mapping_choices(self, source: CSVSource) -> list[tuple[str, DisplayLabel]]:
        # Arbitrary headers can map to speaker slots; only mapped slots reach preview.
        detected = self.form_options({self.guess_column(header): '' for header in source['headers']})['slots']
        slots = min(100, max(len(source['headers']) - 1, detected))
        return list(self.targets) + [
            (f'speaker_{number}_{field}', _('Speaker %(number)d — %(field)s') % {'number': number, 'field': label})
            for number in range(1, slots + 1) for field, label in [('name', _('Name')), ('email', _('Email')), ('gender', _('Gender')), ('category', _('Categories'))]]

    def preview_field_count(self, targets: Iterable[str]) -> int:
        return len(self.targets) + self.form_options(targets)['slots'] * 2 + len(self.form_options(targets)['participant_fields']) + 1

    def initial(self, row: CSVRow, context: CSVImportContext) -> RowData:
        values = super().initial(row, context)
        values['institution'] = context.institutions.get((row['file_index'], values.get('institution', '')))
        for name in values:
            if name in ('break_categories', 'categories') or name.endswith('_category'):
                target = 'break_category' if name == 'break_categories' else 'speaker_category'
                values[name] = [context.references.match(target, item.strip()) for item in values[name].split('/') if item.strip()]
            elif name == 'gender' or name.endswith('_gender'):
                try:
                    values[name] = TournamentDataLookups.lookup_gender(values[name]) if values[name] else ''
                except ValueError:
                    pass
        prefix = values.get('use_institution_prefix', '')
        try:
            values['use_institution_prefix'] = convert_bool(prefix) if prefix else False
        except ValueError:
            values['use_institution_prefix'] = prefix
        return values

    def serialize(self, data: RowData) -> SerializedRowData:
        return {name: [reference_value(item) for item in value] if isinstance(value, (list, tuple)) else
            reference_value(value) if hasattr(value, '_meta') else value for name, value in data.items()}

    def duplicate_key(self, data: RowData) -> DuplicateKey:
        return self.key, reference_value(data.get('institution')), data.get('reference')

    def preview_dependencies(self, data: Mapping[str, object]) -> tuple[int, ...]:
        return reference_dependencies(data, (*self.reference_fields, *(name for name in data if name.endswith('_category'))))

    def preview_summary(self, form: CSVTeamForm) -> PreviewSummary:
        institution = form.cleaned_data.get('institution')
        related = str(institution) if institution else _('Unaffiliated')
        raw = form['institution'].value()
        if isinstance(raw, str) and raw.startswith('unresolved:'):
            related = raw.split(':', 1)[1]
        return {'name': form['reference'].value() or '', 'related': related}

    def object_counts(self, form: CSVTeamForm) -> dict[str, int]:
        return {'team': 1, 'speaker': sum(bool(form.cleaned_data.get(f'speaker_{n}_name')) for n in range(1, form.slots + 1))}

    @transaction.atomic
    def save(self, form: CSVTeamForm, user: AbstractBaseUser, **dependencies) -> Team:
        team = form.save(commit=False)
        team.tournament = form.tournament
        team.save()
        speakers = []
        for number in range(1, form.slots + 1):
            name = form.cleaned_data.get(f'speaker_{number}_name')
            if name:
                speaker = team.speaker_set.create(name=name, email=form.cleaned_data.get(f'speaker_{number}_email') or None,
                    gender=form.cleaned_data.get(f'speaker_{number}_gender') or '')
                speaker.categories.add(*form.cleaned_data.get(f'speaker_{number}_category', []))
                PersonIdentifier.objects.create(person=speaker)
                speakers.append(speaker)
        if speakers:
            populate_url_keys(speakers)
            populate_code_names(speakers)
        initialize_teams([team], team.tournament, general_break_categories=True)
        team.break_categories.add(*form.cleaned_data.get('break_categories', []))
        ActionLogEntry.objects.log(type=ActionLogEntry.ActionType.TEAM_CREATE,
            tournament=team.tournament, content_object=team, user=user)
        return team


class SpeakerCSVType(CSVObjectType[CSVSpeakerForm, Speaker]):
    count_label = ngettext_lazy('Speaker', 'Speakers', 'count')
    key = 'speaker'
    label = _('Speakers')
    filename_words = ('speaker', 'speakers')
    templates = (('speakers', _('Separate speakers'), ('name', 'email', 'team_name', 'institution', 'use_institution_prefix')),)
    targets = [('name', _('Speaker name')), ('email', _('Speaker email')),
        ('team', _('Team name / suffix')), ('institution', _('Institution name or code')),
        ('use_institution_prefix', _('Prefix team name with institution')), ('gender', _('Gender')),
        ('phone', _('Phone')), ('pronoun', _('Pronoun')), ('categories', _('Speaker categories'))]
    aliases = {'speaker_name': 'name', 'speaker': 'name', 'speaker_email': 'email', 'team_name': 'team',
        'institution_name': 'institution', 'institution_code': 'institution', 'university': 'institution', 'prefix': 'use_institution_prefix', 'category': 'categories'}
    required_targets = ('name', 'team')
    priority = 1
    identity_fields = ('team', 'name')
    reference_fields = ('team', 'institution', 'categories')

    form_class = CSVSpeakerForm

    def form_options(self, values: Iterable[str]) -> FormOptions:
        return {'participant_fields': tuple(name for name in values if name in ('gender', 'phone', 'pronoun', 'categories'))}

    def initial(self, row: CSVRow, context: CSVImportContext) -> RowData:
        values = CSV_TYPES['team'].initial(row, context)
        values['team_name'] = values.get('team', '')
        values['team'] = context.match_team(row)
        return values

    def restore_preview(self, data: QueryDict, prefix: str, initial: RowData) -> None:
        if prefix + 'team_name' not in data:
            for field in ('team_name', 'institution', 'use_institution_prefix'):
                value = initial.get(field)
                data[prefix + field] = str(value) if value is not None else ''
            if not data.get(prefix + 'team'):
                data[prefix + 'team'] = initial['team']

    def preview_field_count(self, targets: Iterable[str]) -> int:
        return 7 + len(self.form_options(targets)['participant_fields'])

    def serialize(self, data: RowData) -> SerializedRowData:
        return CSV_TYPES['team'].serialize(data)

    def duplicate_key(self, data: RowData) -> DuplicateKey:
        team = (reference_value(data['institution']), data['team_name']) if data['team'] == 'new' else data['team']
        return self.key, team, data['name']

    def resolve_preview(self, form: CSVSpeakerForm, forms: Sequence[BaseForm]) -> None:
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

    def preview_summary(self, form: CSVSpeakerForm) -> PreviewSummary:
        token = form.cleaned_data.get('team', form['team'].value())
        if token == 'new':
            related = _('New team: %(name)s') % {'name': form['team_name'].value() or ''}
        else:
            related = dict(form.fields['team'].choices).get(token, _('Choose a team'))
        return {'name': form['name'].value() or '', 'related': related}

    def additional_objects(self, form: CSVSpeakerForm) -> Iterable[AdditionalObject]:
        data = form.cleaned_data
        if data.get('team') == 'new' and not form.references.team_identities.get(
                (reference_value(data['institution']) or None, data['team_name'])):
            return (('team', (reference_value(data['institution']) or None, data['team_name'])),)
        return ()

    def preview_dependencies(self, data: Mapping[str, object]) -> tuple[int, ...]:
        return reference_dependencies(data, self.reference_fields)

    def dependencies(self, tournament: Tournament, data: SerializedRowData, rows: Sequence[CSVResultRow], references: ImportReferences) -> ExecutionDependencies:
        token = data['team']
        if token == 'new':
            return {'team': None}
        if token.startswith('row:'):
            dependency = rows[int(token.split(':')[1])]
            team_id = dependency.get('object_id', dependency.get('team_id')) if dependency['status'] == 'imported' else None
        else:
            team_id = token.split(':')[1]
        team = references.teams_by_id.get(int(team_id)) if team_id is not None else None
        if team is None:
            raise DependencyBlockedError(_('The linked team was skipped, failed, or no longer exists.'))
        return {'team': team}

    @transaction.atomic
    def save(self, form: CSVSpeakerForm, user: AbstractBaseUser, *, team: Team | None) -> Speaker:
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
                    'institution': reference_value(data['institution']),
                    'use_institution_prefix': str(data['use_institution_prefix']), 'seed': ''}, references=form.references)
                if not team_form.is_valid():
                    raise ValidationError(_('The new team could not be validated.'))
                team = kind.save(team_form, user)
        if team.tournament_id != form.tournament.pk:
            raise ValidationError(_('The team belongs to another tournament.'))
        if team.speaker_set.filter(name=form.cleaned_data['name']).exists():
            raise ValidationError(_('A speaker with this name already belongs to this team.'))
        speaker = team.speaker_set.create(name=form.cleaned_data['name'], email=form.cleaned_data.get('email') or None,
            **{name: form.cleaned_data[name] for name in ('gender', 'phone', 'pronoun') if name in form.cleaned_data})
        speaker.categories.add(*form.cleaned_data.get('categories', []))
        PersonIdentifier.objects.create(person=speaker)
        populate_url_keys([speaker])
        populate_code_names([speaker])
        ActionLogEntry.objects.log(type=ActionLogEntry.ActionType.SPEAKER_CREATE,
            tournament=form.tournament, content_object=speaker, user=user)
        return speaker


CSV_TYPES: dict[str, CSVObjectType[Any, Any]] = {}


def register_csv_type(csv_type: CSVObjectType[Any, Any]) -> None:
    if csv_type.key in CSV_TYPES:
        raise ValueError(f'CSV type {csv_type.key!r} is already registered')
    CSV_TYPES[csv_type.key] = csv_type
    return csv_type


register_csv_type(TeamCSVType())
register_csv_type(SpeakerCSVType())
for csv_type in model_csv_types():
    register_csv_type(csv_type)


def guess_file_type(filename: str) -> str:
    stem = PurePath(filename).stem.casefold()
    templates = [kind.key for kind in CSV_TYPES.values() if any(key == stem for key, label, columns in kind.templates)]
    if len(templates) == 1:
        return templates[0]
    normalized = re.sub(r'\W+', '_', stem)
    matches = [(len(word.split('_')), kind.key) for kind in CSV_TYPES.values() for word in kind.filename_words
        if re.search(r'(^|_)' + re.escape(word) + r'(_|$)', normalized)]
    if not matches:
        return ''
    longest = max(length for length, key in matches)
    candidates = {key for length, key in matches if length == longest}
    return candidates.pop() if len(candidates) == 1 else ''
