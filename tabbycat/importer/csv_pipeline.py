"""Reference context and execution shared by registered CSV types."""

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils.functional import cached_property
from django.utils.translation import gettext as _

from participants.models import Institution

from .csv_types import CSV_TYPES, DependencyBlockedError
from .references import ImportReferences


class CSVImportContext:
    def __init__(self, tournament, rows):
        self.tournament = tournament
        self.rows = rows
        self.references = ImportReferences(tournament)

    @cached_property
    def institutions(self):
        resolved = {}
        for row in self.rows:
            value = row['values'].get('institution', '')
            key = (row['file_index'], value)
            if key in resolved:
                continue
            try:
                resolved[key] = self.references.lookup_institution(value).pk if value else None
            except (Institution.DoesNotExist, Institution.MultipleObjectsReturned):
                resolved[key] = 'unresolved:' + value
        return resolved

    def match_team(self, row):
        values = row['values']
        value = values.get('team', '')
        institution = self.institutions.get((row['file_index'], values.get('institution', '')))
        candidates = self.team_options[1]
        matches = [token for token, names, inst_id in candidates if value in names and inst_id == institution]
        if len(matches) == 1:
            return matches[0]
        # Anorak matches by institution and reference; ambiguous existing/staged
        # matches need a choice, while a missing match proposes a new team.
        return '' if matches else 'new'

    @cached_property
    def team_options(self):
        choices, candidates = [], []
        for team in self.references.teams:
            token = f'existing:{team.pk}'
            choices.append((token, _('Existing: %(name)s') % {'name': team.long_name}))
            candidates.append((token, [team.reference, team.short_name, team.long_name], team.institution_id))
        for index, row in enumerate(self.rows):
            if row['kind'] != 'team':
                continue
            token = f'row:{index}'
            values = row['values']
            choices.append((token, _('%(file)s, line %(line)d: %(team)s (%(institution)s)') % {
                'file': row['file'], 'line': row['line'], 'team': values.get('reference', ''),
                'institution': values.get('institution', '')}))
            candidates.append((token, [values.get('reference', '')],
                self.institutions.get((row['file_index'], values.get('institution', '')))))
        return choices, candidates

    def initial_rows(self):
        return [{**CSV_TYPES[row['kind']].initial(row, self), '_kind': row['kind']} for row in self.rows]


def process_csv_row(tournament, user, draft, row):
    kind = CSV_TYPES[row['kind']]
    form = kind.form_class(tournament, data=row['data'], team_choices=draft['team_choices'], **kind.form_options(row['data']))
    if not form.is_valid():
        row.update(status='failed', errors='; '.join(
            f'{form.fields[field].label or field if field in form.fields else field}: {message}'
            for field, errors in form.errors.items() for message in errors))
        return
    try:
        dependencies = kind.dependencies(tournament, row['data'], draft['rows'], references=form.references)
    except DependencyBlockedError as error:
        row.update(status='blocked', errors=str(error))
        return
    try:
        obj = kind.save(form, user, **dependencies)
    except (IntegrityError, ValidationError):
        row.update(status='failed', errors=str(_('This row could not be saved. Check for duplicate participants or changed data.')))
    else:
        row.update(status='imported', object_id=obj.pk)
