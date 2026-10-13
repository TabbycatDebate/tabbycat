"""Reference context and execution shared by registered CSV types."""

from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist, ValidationError
from django.db import DataError, IntegrityError
from django.utils.functional import cached_property
from django.utils.translation import gettext as _

from .csv_types import CSV_TYPES, DependencyBlockedError, DependencyPendingError
from .references import ImportReferences


class CSVImportContext:
    def __init__(self, tournament, rows):
        self.tournament = tournament
        self.rows = rows
        self.references = ImportReferences(tournament)
        self.references.configure(rows)
        self.references.add_speaker_teams(rows)

    @cached_property
    def institutions(self):
        resolved = {}
        for row in self.rows:
            value = row['values'].get('institution', '')
            key = (row['file_index'], value)
            if key in resolved:
                continue
            resolved[key] = self.references.match('institution', value) if value else None
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
        return [{**CSV_TYPES[row['kind']].initial(row, self), '_kind': row['kind'], '_row_token': f'row:{index}'}
            for index, row in enumerate(self.rows)]


def process_csv_row(tournament, user, draft, row):
    kind = CSV_TYPES[row['kind']]
    references = ImportReferences(tournament)
    references.configure(draft['rows'], results=True)
    data = row['data']
    dependencies = kind.preview_dependencies(data)
    deferred = set(kind.deferred_fields) if row['status'] == 'pending' else set()
    if deferred:
        primary = {name: value for name, value in data.items() if name not in deferred}
        dependencies = kind.preview_dependencies(primary)
    for index in dependencies:
        parent = draft['rows'][index]
        if parent['status'] == 'pending':
            raise DependencyPendingError(_('Import the referenced rows first.'))
        if parent['status'] not in ('imported', 'created'):
            message = _('A referenced row was skipped or could not be imported.')
            if row['status'] == 'created':
                message = _('The object was created, but a remaining reference could not be imported.')
            row.update(status='blocked', errors=str(message))
            return
    options = kind.form_options(data)
    if row['status'] == 'created':
        options['instance'] = references.objects(kind.key).get(row['object_id'])
    form = kind.form_class(tournament, data=data, references=references,
        team_choices=draft['team_choices'], **options)
    if not form.is_valid():
        errors = '; '.join(
            f'{form.fields[field].label or field if field in form.fields else field}: {message}'
            for field, errors in form.errors.items() for message in errors)
        if row['status'] == 'created':
            errors = str(_('The object was created, but its remaining references could not be saved.')) + ' ' + errors
        row.update(status='failed', errors=errors)
        return
    try:
        dependencies = kind.dependencies(tournament, data, draft['rows'], references=references)
    except DependencyBlockedError as error:
        row.update(status='blocked', errors=str(error))
        return
    try:
        if row['status'] == 'created':
            obj = form.instance
            kind.finish_references(form, obj)
        else:
            obj = kind.save(form, user, **dependencies)
    except (DataError, IntegrityError, MultipleObjectsReturned, ObjectDoesNotExist, ValidationError):
        message = _('This row could not be saved. Check for duplicates or changed data.')
        if row['status'] == 'created':
            message = _('The object was created, but its remaining references could not be saved.')
        row.update(status='failed', errors=str(message))
    else:
        status = 'created' if deferred and any(data.get(name) for name in deferred) else 'imported'
        row.update(status=status, object_id=obj.pk)
        if row['kind'] == 'speaker':
            row['team_id'] = obj.team_id
