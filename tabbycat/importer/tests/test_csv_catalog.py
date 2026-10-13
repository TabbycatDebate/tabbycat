"""Mixed-file coverage for the full command importer CSV catalog."""

import csv
import io

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.http import QueryDict
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from adjallocation.models import AdjudicatorAdjudicatorConflict
from availability.models import RoundAvailability
from motions.models import RoundMotion
from participants.models import Adjudicator, Institution, Speaker, Team
from tournaments.models import Round, Tournament
from utils.misc import reverse_tournament
from venues.models import Venue, VenueConstraint

from ..csv_forms import CSVPreviewFormSet
from ..csv_pipeline import CSVImportContext
from ..csv_state import remap_step_data
from ..csv_types import CSV_TYPES, guess_file_type
from ..importers import importer_registry


class CSVCatalogTests(TestCase):
    def setUp(self):
        self.tournament = Tournament.objects.create(slug='csv-catalog')
        self.tournament.current_round = Round.objects.create(tournament=self.tournament, seq=0, name='Setup', abbreviation='Setup')
        self.tournament.save()
        user = get_user_model().objects.create_superuser('catalog-admin', 'catalog@example.com', 'password')
        self.client.force_login(user)

    @staticmethod
    def csv_file(name, headers, rows):
        stream = io.StringIO()
        writer = csv.writer(stream)
        writer.writerow(headers)
        writer.writerows(rows)
        return SimpleUploadedFile(name + '.csv', stream.getvalue().encode())

    def prepare(self, sources):
        response = self.client.post(reverse_tournament('importer-csv-upload', self.tournament), {
            'files': [self.csv_file(*source) for source in sources], 'encoding': 'utf-8-sig', 'delimiter': ',', 'header_row': 1})
        self.assertEqual(response.status_code, 302, response.content)
        self.url = response.url
        response = self.client.get(self.url)
        self.prefix = response.context['wizard']['management_form'].prefix
        types = {f'types-file_{i}': guess_file_type(name + '.csv') for i, (name, headers, rows) in enumerate(sources)}
        self.assertTrue(all(types.values()), types)
        response = self.post('types', types)
        form = response.context['wizard']['form']
        response = self.post('mapping', {field.html_name: field.value() for field in form})
        self.assertEqual(response.context['wizard']['steps'].current, 'preview', response.content)
        form = response.context['wizard']['form']
        self.assertTrue(form.is_valid(), form.errors)
        self.assertFalse(Team.objects.exists())
        return form

    def post(self, step, data):
        return self.client.post(self.url, {f'{self.prefix}-current_step': step, **data})

    def execute(self, form):
        values = {'preview-TOTAL_FORMS': len(form.forms), 'preview-INITIAL_FORMS': len(form.forms)}
        for row in form.forms:
            for field in row:
                value = field.value()
                if value is not None:
                    values[field.html_name] = value
        response = self.post('preview', values)
        self.assertEqual(response.context['wizard']['steps'].current, 'confirm', response.context['wizard']['form'].errors)
        response = self.post('confirm', {'confirm-confirm': 'on'})
        self.assertEqual(response.status_code, 302)
        self.results_url = response.url
        rows = self.client.get(self.results_url).context['rows']

        def ready(row):
            return all(rows[index]['status'] != 'pending' for index in (
                row['link_dependencies'] if row['status'] == 'created' else row['dependencies']))

        while any(row['status'] in ('pending', 'created') for row in rows):
            pending = sorted((row for row in rows if row['status'] == 'pending' and ready(row)), key=lambda row: row['priority'])
            row = pending[0] if pending else next((row for row in rows if row['status'] == 'created' and ready(row)), None)
            self.assertIsNotNone(row, rows)
            index = rows.index(row)
            response = self.client.post(self.results_url, {'row': index})
            self.assertEqual(response.status_code, 200, response.content)
            self.assertIn(response.json()['status'], ('imported', 'created'), response.json())
            row['status'] = response.json()['status']
        return rows

    def test_registry_covers_every_command_file(self):
        command_files = {name for importer in importer_registry.values() for name in importer.order}
        templates = {name for kind in CSV_TYPES.values() for name, label, columns in kind.templates}
        self.assertTrue(command_files.issubset(templates), command_files - templates)
        for name in command_files:
            with self.subTest(name=name):
                self.assertTrue(guess_file_type(name.upper() + '.CSV'))
                self.assertTrue(guess_file_type('Export_' + name + '_2026.csv'))

    def test_all_command_types_in_one_import(self):
        # Deliberately reverse dependency order, including two mutually conflicted adjudicators.
        sources = [
            ('team_venue_constraints', ['team', 'category', 'priority'], [['SCI A', 'Main', 2]]),
            ('adj_venue_constraints', ['adjudicator', 'category', 'priority'], [['Judge One', 'Main', 1]]),
            ('adj_feedback_questions', ['seq', 'reference', 'name', 'text', 'answer_type', 'required', 'from_team', 'from_adj'],
                [[1, 'agree', 'Agree', 'Did you agree?', 'yesno', 'yes', 'yes', 'no']]),
            ('sides', ['team_name', 'R1'], [['SCI A', 'aff']]),
            ('team_institution_conflicts', ['team', 'institution'], [['SCI A', 'OTH']]),
            ('adjudicator_conflicts', ['adjudicator1', 'adjudicator2'], [['Judge One', 'Judge Two']]),
            ('institution_conflicts', ['adjudicator', 'institution'], [['Judge One', 'OTH']]),
            ('team_conflicts', ['adjudicator', 'team'], [['Judge Two', 'SCI A']]),
            ('scores', ['adjudicator', 'score'], [['Judge One', 4.5]]),
            ('motions', ['reference', 'text', 'rounds', 'seq'], [['M1', 'This house would test CSV imports.', 'R1', 1]]),
            ('adjudicators', ['name', 'institution', 'base_score', 'gender', 'adj_conflicts', 'available:R1'],
                [['Judge One', 'SCI', 3.5, 'other', 'Judge Two', 'yes'], ['Judge Two', 'SCI', 2.5, 'female', 'Judge One', 'no']]),
            ('venues', ['name', 'priority', 'category', 'available:R1'], [['Room One', 10, 'Main', 'yes']]),
            ('speakers', ['name', 'team_name', 'institution', 'gender', 'category'], [['Bob', 'A', 'SCI', 'male', 'Novice']]),
            ('teams', ['reference', 'institution', 'use_institution_prefix', 'break_category', 'speaker1_name', 'speaker1_gender', 'speaker1_category'],
                [['A', 'SCI', 'yes', 'Open', 'Alice', 'female', 'Novice']]),
            ('rounds', ['seq', 'name', 'abbreviation', 'stage', 'draw_type'], [[1, 'Round One', 'R1', 'preliminary', 'random']]),
            ('speaker_categories', ['name', 'slug', 'seq', 'limit'], [['Novice', 'novice', 1, 0]]),
            ('break_categories', ['name', 'slug', 'seq', 'break_size', 'is_general', 'priority'], [['Open', 'open', 1, 8, 'yes', 0]]),
            ('venue_categories', ['name', 'display_in_venue_name'], [['Main', 'prefix']]),
            ('institutions', ['name', 'code', 'region'], [['School', 'SCI', 'North'], ['Other School', 'OTH', 'North']]),
            ('regions', ['name'], [['North']]),
        ]
        form = self.prepare(sources)
        self.execute(form)
        team = Team.objects.get()
        self.assertEqual(team.long_name, 'School A')
        self.assertEqual(team.break_categories.get().slug, 'open')
        self.assertEqual(set(Speaker.objects.values_list('name', flat=True)), {'Alice', 'Bob'})
        self.assertTrue(all(speaker.categories.get().slug == 'novice' for speaker in Speaker.objects.all()))
        self.assertEqual(Adjudicator.objects.get(name='Judge One').base_score, 4.5)
        self.assertEqual(AdjudicatorAdjudicatorConflict.objects.count(), 2)
        self.assertEqual(RoundMotion.objects.count(), 1)
        self.assertEqual(VenueConstraint.objects.count(), 2)
        self.assertEqual(Venue.objects.get().display_name, 'Main Room One')
        self.assertEqual(RoundAvailability.objects.count(), 2)
        self.assertEqual(Institution.objects.get(code='SCI').region.name, 'North')
        # Reposting a completed row cannot recreate its objects or relationships.
        self.client.post(self.results_url, {'row': 10})
        self.assertEqual(Adjudicator.objects.count(), 2)
        self.assertEqual(AdjudicatorAdjudicatorConflict.objects.count(), 2)

    def test_implicit_regions_and_room_categories(self):
        form = self.prepare([
            ('venues', ['name', 'priority', 'category'], [['Blue Room', 1, 'Blue']]),
            ('institutions', ['name', 'code', 'region'], [['New School', 'NEW', 'New Region']]),
        ])
        self.execute(form)
        self.assertEqual(Institution.objects.get().region.name, 'New Region')
        self.assertEqual(Venue.objects.get().venuecategory_set.get().name, 'Blue')

    def test_conflicts_can_link_to_team_created_from_speaker_file(self):
        form = self.prepare([
            ('team_conflicts', ['adjudicator', 'team'], [['Judge', 'SCI A']]),
            ('adjudicators', ['name', 'institution'], [['Judge', 'SCI']]),
            ('speakers', ['name', 'team_name', 'institution', 'use_institution_prefix'], [['Alice', 'A', 'SCI', 'yes']]),
            ('institutions', ['name', 'code'], [['School', 'SCI']]),
        ])
        self.execute(form)
        self.assertEqual(Adjudicator.objects.get().team_conflicts.get(), Speaker.objects.get().team)

    def test_skipped_uploaded_reference_blocks_preview(self):
        form = self.prepare([
            ('adjudicators', ['name', 'institution'], [['Judge', 'SCI']]),
            ('institutions', ['name', 'code'], [['School', 'SCI']]),
        ])
        values = {'preview-TOTAL_FORMS': 2, 'preview-INITIAL_FORMS': 2, 'preview-1-DELETE': 'on'}
        for row in form.forms:
            for field in row:
                if field.name != 'DELETE' and field.value() is not None:
                    values[field.html_name] = field.value()
        response = self.post('preview', values)
        self.assertEqual(response.context['wizard']['steps'].current, 'preview')
        self.assertIn('linked row is skipped', str(response.context['wizard']['form'].forms[0].errors))

    def test_missing_and_other_tournament_references_are_not_accepted(self):
        other = Tournament.objects.create(slug='unrelated')
        Round.objects.create(tournament=other, seq=1, name='Other round', abbreviation='OTHER')
        rows = [{'kind': 'motion', 'file': 'motions.csv', 'file_index': 0, 'line': 2,
            'values': {'reference': 'M', 'text': 'Motion', 'rounds': 'OTHER'}}]
        context = CSVImportContext(self.tournament, rows)
        initial = context.initial_rows()
        form = CSV_TYPES['motion'].form_class(self.tournament, references=context.references, initial=initial[0],
            data={'reference': 'M', 'text': 'Motion', 'rounds': ['unresolved:OTHER']})
        self.assertFalse(form.is_valid())
        self.assertIn('rounds', form.errors)

    def test_reference_choices_and_validation_share_queries_across_rows(self):
        Institution.objects.create(name='School', code='SCI')
        Round.objects.create(tournament=self.tournament, seq=1, name='Round One', abbreviation='R1')
        rows = [{'kind': 'adjudicator', 'file': 'adjudicators.csv', 'file_index': 0, 'line': index + 2,
            'values': {'name': f'Judge {index}', 'institution': 'SCI', 'available:R1': 'yes'}} for index in range(20)]
        context = CSVImportContext(self.tournament, rows)
        # Build and validate through the same formset used by the wizard.
        initial = context.initial_rows()
        with CaptureQueriesContext(connection) as queries:
            data = {'preview-TOTAL_FORMS': 20, 'preview-INITIAL_FORMS': 20}
            defaults = CSVPreviewFormSet(prefix='preview', initial=initial,
                form_kwargs={'tournament': self.tournament, 'references': context.references})
            for row in defaults.forms:
                for field in row:
                    if field.name != 'DELETE' and field.value() is not None:
                        data[field.html_name] = field.value()
            forms = CSVPreviewFormSet(data=data, prefix='preview', initial=initial,
                form_kwargs={'tournament': self.tournament, 'references': context.references})
            self.assertTrue(forms.is_valid(), forms.errors)
            for row in forms.forms:
                str(row['institution'])
                str(row['round_for_available:R1'])
        reference_queries = [query for query in queries if query['sql'].startswith('SELECT') and
            ('"participants_institution"' in query['sql'] or '"tournaments_round"' in query['sql'])]
        self.assertEqual(len(reference_queries), 2, reference_queries)

    def test_all_templates_download_and_map_required_columns(self):
        for kind in CSV_TYPES.values():
            for template, label, columns in kind.templates:
                with self.subTest(template=template):
                    response = self.client.get(reverse_tournament('importer-csv-template', self.tournament,
                        kwargs={'template_key': template}))
                    self.assertEqual(response.status_code, 200)
                    self.assertTrue(set(kind.required_targets).issubset({kind.guess_column(column) for column in columns}))

    def test_adjudicator_cannot_conflict_with_their_own_uploaded_row(self):
        rows = [{'kind': 'adjudicator', 'file': 'adjudicators.csv', 'file_index': 0, 'line': 2,
            'values': {'name': 'Judge', 'adj_conflicts': 'Judge'}}]
        context = CSVImportContext(self.tournament, rows)
        initial = context.initial_rows()[0]
        form = CSV_TYPES['adjudicator'].form_class(self.tournament, references=context.references, initial=initial,
            data={'name': 'Judge', 'adj_conflicts': ['row:0']})
        self.assertFalse(form.is_valid())
        self.assertIn('adj_conflicts', form.errors)

    def test_file_changes_remap_references_without_changing_literal_text(self):
        sources = [{'id': name, 'rows': [{'line': 2}]} for name in ('removed', 'motion', 'round')]
        data = QueryDict(mutable=True)
        data.setlist('preview-1-rounds', ['row:0', 'row:2'])
        data['preview-1-reference'] = 'row:0'
        data['preview-1-text'] = 'Edited motion text'
        result = remap_step_data('preview', data, sources, sources[1:], {1: CSV_TYPES['motion']})
        self.assertEqual(result.getlist('preview-0-rounds'), ['removed', 'row:1'])
        self.assertEqual(result['preview-0-reference'], 'row:0')
        self.assertEqual(result['preview-0-text'], 'Edited motion text')
        self.assertEqual(result['preview-TOTAL_FORMS'], 2)

    def test_scalar_side_rejects_unknown_positions(self):
        team = Team.objects.create(tournament=self.tournament, reference='A')
        form = CSV_TYPES['side'].form_class(self.tournament, data={
            'team': team.pk, 'round': self.tournament.current_round.pk, 'side': 99})
        self.assertFalse(form.is_valid())
        self.assertIn('side', form.errors)

    def test_round_sequence_uses_data_row_order_after_header_and_blank_lines(self):
        rows = [{'kind': 'round', 'file': 'rounds.csv', 'file_index': 0, 'line': 9, 'row_index': 0,
            'values': {'name': 'First round', 'abbreviation': 'FIRST'}}]
        context = CSVImportContext(self.tournament, rows)
        initial = context.initial_rows()[0]
        self.assertEqual(initial['seq'], 1)
        self.assertEqual(initial['schedule_group'], 1)
