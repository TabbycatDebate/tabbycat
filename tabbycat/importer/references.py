"""Request/file-scoped participant references, never persisted in wizard sessions."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from typing import TYPE_CHECKING

from django.db.models import Model
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from participants.models import Institution, Speaker, Team

from .csv_models import CSV_MODELS, csv_queryset, IMPLICIT_REFERENCE_TYPES, NAME_FIELDS
from .csv_typing import CSVChoice, CSVResultRow, CSVRow, DisplayLabel, ReferenceToken
from .csv_values import convert_bool


if TYPE_CHECKING:
    from tournaments.models import Tournament


class ImportReferences:
    def __init__(self, tournament: Tournament) -> None:
        self.tournament = tournament
        self.staged: dict[str, Model] = {}
        self.object_cache: dict[str, dict[int, Model]] = {}
        self.name_cache = {}
        self.implicit_cache: dict[tuple[str, str], Model] = {}

    @cached_property
    def institutions(self) -> list[Institution]:
        return list(Institution.objects.all())

    @cached_property
    def institution_choices(self) -> list[CSVChoice]:
        return [(institution.pk, f'{institution.name} ({institution.code})') for institution in self.institutions] + [
            (token, f'{obj.name} ({obj.code})') for token, obj in self.staged.items() if obj._csv_kind == 'institution']

    @cached_property
    def institutions_by_id(self) -> dict[int, Institution]:
        return {institution.pk: institution for institution in self.institutions}

    @cached_property
    def institution_names(self):
        names = defaultdict(dict)
        for institution in self.institutions:
            for value in (institution.name, institution.code):
                names[value][institution.pk] = institution
        return names

    def lookup_institution(self, value: str) -> Institution:
        matches = list(self.institution_names.get(value, {}).values())
        if not matches:
            raise Institution.DoesNotExist(f'Institution matching {value!r} does not exist.')
        if len(matches) > 1:
            raise Institution.MultipleObjectsReturned(f'Multiple institutions match {value!r}.')
        return matches[0]

    @cached_property
    def teams(self) -> list[Team]:
        return list(Team.objects.all_with_unconfirmed.filter(tournament=self.tournament).select_related('institution'))

    @cached_property
    def teams_by_id(self) -> dict[int, Team]:
        return {team.pk: team for team in self.teams}

    @cached_property
    def team_identities(self):
        identities = defaultdict(list)
        for team in self.teams:
            identities[(team.institution_id, team.reference)].append(team)
        return identities

    @cached_property
    def speaker_names(self) -> set[tuple[int, str]]:
        return set(Speaker.objects.filter(team__tournament=self.tournament).values_list('team_id', 'name'))

    def lookup_team(self, institution: Institution | None, reference: str) -> Team:
        matches = self.team_identities.get((institution.pk if institution else None, reference), [])
        if not matches:
            raise Team.DoesNotExist(f'Team matching {reference!r} does not exist.')
        if len(matches) > 1:
            raise Team.MultipleObjectsReturned(f'Multiple teams match {reference!r}.')
        return matches[0]

    def configure(self, rows: Sequence[CSVRow] | Sequence[CSVResultRow], *, results: bool = False) -> None:
        for index, row in enumerate(rows):
            kind = row.get('kind')
            if results and kind == 'speaker' and row.get('data', {}).get('team') == 'new':
                kind = 'team'
            if kind not in CSV_MODELS or row.get('status') in ('skipped', 'failed', 'blocked'):
                continue
            model = CSV_MODELS[kind]
            values = row.get('data', {}) if results else row['values']
            if results and row.get('kind') == 'speaker':
                values = {**values, 'reference': values.get('team_name', '')}
            attributes = {field.name: values[field.name] for field in model._meta.fields
                if not field.is_relation and field.name in values and values[field.name] != ''}
            if kind == 'round' and not attributes.get('seq'):
                attributes['seq'] = row.get('row_index', row.get('line', index + 2) - 2) + 1
            obj = model(**attributes)
            obj._csv_token = f'row:{index}'
            obj._csv_object_id = row.get('team_id') if row.get('kind') == 'speaker' else row.get('object_id')
            obj._csv_kind = kind
            obj._csv_values = values
            obj._csv_file = row.get('file', '')
            obj._csv_line = row.get('line', index + 2)
            self.staged[obj._csv_token] = obj

    def add_speaker_teams(self, rows: Sequence[CSVRow]) -> None:
        identities = set()
        for obj in self.staged.values():
            if obj._csv_kind == 'team':
                values = obj._csv_values
                identities.add((self.match('institution', values.get('institution')), values.get('reference')))
        for index, row in enumerate(rows):
            if row['kind'] != 'speaker':
                continue
            values = row['values']
            institution = self.match('institution', values.get('institution'))
            name = values.get('team')
            identity = (institution, name)
            if not name or identity in identities or any(
                    team.institution_id == (institution or None) and name in (team.reference, team.short_name, team.long_name)
                    for team in self.teams):
                continue
            obj = Team(reference=name)
            obj._csv_kind = 'team'
            obj._csv_token = f'row:{index}'
            obj._csv_object_id = None
            obj._csv_values = {**values, 'reference': name}
            obj._csv_file = row['file']
            obj._csv_line = row['line']
            self.staged[obj._csv_token] = obj
            identities.add(identity)

    def objects(self, kind: str) -> dict[int, Model]:
        if kind not in self.object_cache:
            if kind == 'institution':
                objects = self.institutions
            elif kind == 'team':
                objects = self.teams
            else:
                objects = list(csv_queryset(kind, self.tournament))
            self.object_cache[kind] = {obj.pk: obj for obj in objects}
        return self.object_cache[kind]

    def get_object(self, kind: str, value: ReferenceToken | Model | None) -> Model | None:
        if value in (None, ''):
            return None
        model = CSV_MODELS[kind]
        if isinstance(value, model):
            return value
        token = str(value)
        if token.startswith('row:'):
            obj = self.staged.get(token)
            if obj is None or obj._csv_kind != kind:
                raise model.DoesNotExist
            if obj._csv_object_id is not None:
                actual = self.objects(kind).get(obj._csv_object_id)
                if actual is None:
                    raise model.DoesNotExist
                return actual
            return obj
        if token.startswith('new:') and kind in IMPLICIT_REFERENCE_TYPES:
            if (kind, token) in self.implicit_cache:
                return self.implicit_cache[(kind, token)]
            obj = model(name=token[4:])
            if any(field.name == 'tournament' for field in model._meta.fields):
                obj.tournament = self.tournament
            obj._csv_token = token
            obj.clean_fields(exclude=['tournament'])
            self.implicit_cache[(kind, token)] = obj
            return obj
        try:
            return self.objects(kind)[int(token.removeprefix('existing:'))]
        except (ValueError, KeyError):
            raise model.DoesNotExist

    def choices(self, kind: str) -> list[CSVChoice]:
        choices = [(obj.pk, self.object_label(kind, obj)) for obj in self.objects(kind).values()]
        for token, obj in self.staged.items():
            if obj._csv_kind == kind:
                choices.append((token, _('%(file)s, line %(line)s: %(name)s') % {
                    'file': obj._csv_file, 'line': obj._csv_line, 'name': self.object_label(kind, obj)}))
        return choices

    @staticmethod
    def object_label(kind: str, obj: Model) -> DisplayLabel:
        fields = NAME_FIELDS.get(kind, ('name',))
        if kind == 'institution':
            return f'{obj.name} ({obj.code})'
        if kind == 'team':
            return obj.long_name or (str(getattr(obj, '_csv_values', {}).get('institution', '')) + ' ' + obj.reference).strip()
        return str(getattr(obj, fields[0], ''))

    def match(self, kind: str, value: str | None, *, create: bool = False) -> ReferenceToken | None:
        if not value:
            return None
        if kind not in self.name_cache:
            names = defaultdict(dict)
            objects = [*self.objects(kind).values(), *(obj for obj in self.staged.values() if obj._csv_kind == kind)]
            for obj in objects:
                for field in NAME_FIELDS.get(kind, ('name',)):
                    name = str(getattr(obj, field, ''))
                    if name:
                        names[name][reference_value(obj)] = obj
                if kind == 'team' and hasattr(obj, '_csv_values'):
                    values = obj._csv_values
                    try:
                        prefix = convert_bool(str(values.get('use_institution_prefix', False)))
                        institution = self.get_object('institution', self.match('institution', values.get('institution')))
                    except (ValueError, Institution.DoesNotExist):
                        institution = None
                        prefix = False
                    if prefix and institution:
                        for prefix_name in (institution.name, institution.code):
                            names[f'{prefix_name} {obj.reference}'][reference_value(obj)] = obj
            self.name_cache[kind] = names
        matches = list(self.name_cache[kind].get(str(value), {}).values())
        if len(matches) == 1:
            return reference_value(matches[0])
        if not matches and create and kind in IMPLICIT_REFERENCE_TYPES:
            return 'new:' + str(value)
        return 'unresolved:' + str(value)


def reference_value(obj: Model | None) -> ReferenceToken:
    return (getattr(obj, '_csv_token', None) or obj.pk) if obj is not None else ''
