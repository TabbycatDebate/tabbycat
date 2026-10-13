from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings, TestCase

from participants.models import Institution, Speaker, Team
from tournaments.models import Round, Tournament
from utils.misc import reverse_tournament

from ..csv_forms import CSVMappingForm, CSVPreviewFormSet, CSVTeamForm, CSVTypesForm, CSVUploadForm
from ..csv_types import CSV_TYPES, guess_file_type, register_csv_type, SpeakerCSVType


@override_settings(SESSION_ENGINE='django.contrib.sessions.backends.cache',
    STORAGES={'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'}})
class CSVWizardTests(TestCase):
    def setUp(self):
        cache.clear()
        self.tournament = Tournament.objects.create(slug='csv-test')
        self.tournament.current_round = Round.objects.create(tournament=self.tournament, seq=1, name='Round 1', abbreviation='R1')
        self.tournament.save()
        self.institution = Institution.objects.create(name='Example University', code='EU')
        self.user = get_user_model().objects.create_superuser('csv-admin', 'admin@example.com', 'password')
        self.client.force_login(self.user)

    def upload(self, text='Team,Institution,Speaker 1 name,Speaker 1 email\nA,EU,Alice,alice@example.com\n'):
        response = self.client.post(reverse_tournament('importer-csv-upload', self.tournament), {
            'files': SimpleUploadedFile('teams.csv', text.encode()), 'encoding': 'utf-8-sig', 'delimiter': '', 'header_row': 1,
        })
        self.assertEqual(response.status_code, 302)
        self.url = response.url
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.prefix = response.context['wizard']['management_form'].prefix
        return response

    def step(self, step, values):
        response = self.client.post(self.url, {f'{self.prefix}-current_step': step, **values})
        self.assertIn(response.status_code, (200, 302))
        return response

    def preview(self, text=None, speakers=1):
        self.upload(**({'text': text} if text is not None else {}))
        self.step('types', {'types-file_0': 'team'})
        response = self.step('mapping', {'mapping-column_0_0': 'reference', 'mapping-column_0_1': 'institution',
            'mapping-column_0_2': 'speaker_1_name' if speakers else '',
            'mapping-column_0_3': 'speaker_1_email' if speakers else ''})
        self.assertEqual(response.context['wizard']['steps'].current, 'preview')
        return response

    def preview_data(self, rows):
        data = {'preview-TOTAL_FORMS': len(rows), 'preview-INITIAL_FORMS': len(rows),
            'preview-MIN_NUM_FORMS': 0, 'preview-MAX_NUM_FORMS': 1000}
        for i, row in enumerate(rows):
            data.update({f'preview-{i}-{key}': value for key, value in row.items()})
        return data

    def row(self, **changes):
        return {'reference': 'A', 'institution': self.institution.pk, 'use_institution_prefix': 'True', 'seed': '',
            'speaker_1_name': 'Alice', 'speaker_1_email': 'alice@example.com', **changes}

    def finish(self, rows):
        response = self.step('preview', self.preview_data(rows))
        self.assertEqual(response.context['wizard']['steps'].current, 'confirm', response.context['wizard']['form'].errors)
        self.assertFalse(Team.objects.exists())
        response = self.step('confirm', {'confirm-confirm': 'on'})
        self.assertEqual(response.status_code, 302)
        return response.url

    def test_wizard_creates_team_with_speaker_and_does_not_repeat(self):
        self.preview()
        url = self.finish([self.row()])
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertFalse(Team.objects.exists())
        result = self.client.post(url, {'row': 0})
        self.assertEqual(result.json()['status'], 'imported', result.content)
        team = Team.objects.get()
        self.assertEqual(team.short_name, 'EU A')
        speaker = Speaker.objects.get()
        self.assertEqual(speaker.name, 'Alice')
        self.assertEqual(speaker.email, 'alice@example.com')
        self.assertTrue(speaker.url_key)
        self.assertTrue(speaker.code_name)
        self.assertTrue(team.teaminstitutionconflict_set.filter(institution=self.institution).exists())
        self.client.post(url, {'row': 0})
        self.assertEqual(Team.objects.count(), 1)
        self.assertEqual(Speaker.objects.count(), 1)
        self.assertEqual(self.client.get(url.replace('results/', 'errors/')).status_code, 200)

    def test_teams_without_speakers(self):
        self.preview(speakers=0)
        url = self.finish([self.row(speaker_1_name='', speaker_1_email='')])
        self.assertEqual(self.client.post(url, {'row': 0}).json()['status'], 'imported')
        self.assertEqual(Team.objects.count(), 1)
        self.assertFalse(Speaker.objects.exists())

    def test_skip_invalid_row_preserves_other_registration(self):
        self.preview(text='Team,Institution,Speaker 1 name,Speaker 1 email\nA,EU,Alice,alice@example.com\nB,EU,,bad\n')
        url = self.finish([self.row(), self.row(reference='B', speaker_1_name='', speaker_1_email='bad', DELETE='on')])
        self.assertEqual(self.client.post(url, {'row': 1}).json()['status'], 'skipped')
        self.assertEqual(self.client.post(url, {'row': 0}).json()['status'], 'imported')
        self.assertEqual(Team.objects.count(), 1)

    def test_duplicate_rows_and_missing_speaker_name_block_preview(self):
        data = self.preview_data([self.row(), self.row()])
        forms = CSVPreviewFormSet(data=data, prefix='preview', initial=[{}, {}],
            form_kwargs={'tournament': self.tournament, 'slots': 1})
        self.assertFalse(forms.is_valid())
        self.assertIn('reference', forms.forms[1].errors)
        form = CSVTeamForm(self.tournament, data=self.row(speaker_1_name=''), slots=1)
        self.assertFalse(form.is_valid())
        self.assertIn('speaker_1_name', form.errors)

    def test_invalid_prefix_is_not_silently_true(self):
        form = CSVTeamForm(self.tournament, data=self.row(use_institution_prefix='perhaps'), slots=1)
        self.assertFalse(form.is_valid())
        self.assertIn('use_institution_prefix', form.errors)

    def test_registration_rolls_back_if_speaker_setup_fails(self):
        form = CSVTeamForm(self.tournament, data=self.row(), slots=1)
        self.assertTrue(form.is_valid(), form.errors)
        with patch('importer.csv_types.populate_url_keys', side_effect=ValidationError('failure')):
            with self.assertRaises(ValidationError):
                CSV_TYPES['team'].save(form, self.user)
        self.assertFalse(Team.objects.exists())
        self.assertFalse(Speaker.objects.exists())

    def test_changed_database_is_checked_before_import(self):
        self.preview()
        url = self.finish([self.row()])
        Team.objects.create(tournament=self.tournament, institution=self.institution, reference='A')
        self.assertEqual(self.client.post(url, {'row': 0}).json()['status'], 'failed')
        self.assertEqual(Team.objects.count(), 1)

    def test_other_user_and_tournament_cannot_use_draft(self):
        self.upload()
        other = Tournament.objects.create(slug='other')
        other.current_round = Round.objects.create(tournament=other, seq=1, name='Round 1', abbreviation='R1')
        other.save()
        self.assertEqual(self.client.get(self.url.replace(self.tournament.slug, other.slug)).status_code, 404)
        self.client.force_login(get_user_model().objects.create_superuser('other', 'other@example.com', 'password'))
        self.assertEqual(self.client.get(self.url).status_code, 404)

    def test_non_admin_cannot_upload(self):
        self.client.force_login(get_user_model().objects.create_user('ordinary', password='password'))
        self.assertEqual(self.client.get(reverse_tournament('importer-csv-upload', self.tournament)).status_code, 403)

    def test_upload_parses_bom_semicolon_multiline_and_rejects_ragged_rows(self):
        form = CSVUploadForm(data={'encoding': 'utf-8-sig', 'delimiter': ';', 'header_row': 1}, files={
            'files': SimpleUploadedFile('teams.csv', '\ufeffTeam;Notes\nA;"hello\nworld"\n'.encode()),
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['parsed'][0]['rows'][0]['values'], ['A', 'hello\nworld'])
        form = CSVUploadForm(data={'encoding': 'utf-8-sig', 'delimiter': ',', 'header_row': 1}, files={
            'files': SimpleUploadedFile('teams.csv', b'Team,Notes\nA,B,C\n'),
        })
        self.assertFalse(form.is_valid())

    def separate_speaker_preview(self, existing=False):
        files = [SimpleUploadedFile('speakers.csv', b'Name,Email,Team,Institution\nBob,bob@example.com,A,EU\n')]
        if not existing:
            # Deliberately upload speakers first: execution must still create teams first.
            files.append(SimpleUploadedFile('teams.csv', b'Team,Institution\nA,EU\n'))
        response = self.client.post(reverse_tournament('importer-csv-upload', self.tournament), {
            'files': files, 'encoding': 'utf-8-sig', 'delimiter': '', 'header_row': 1})
        self.url = response.url
        response = self.client.get(self.url)
        self.prefix = response.context['wizard']['management_form'].prefix
        self.step('types', {'types-file_0': 'speaker', **({} if existing else {'types-file_1': 'team'})})
        mapping = {'mapping-column_0_0': 'name', 'mapping-column_0_1': 'email', 'mapping-column_0_2': 'team',
            'mapping-column_0_3': 'institution'}
        if not existing:
            mapping.update({'mapping-column_1_0': 'reference', 'mapping-column_1_1': 'institution'})
        response = self.step('mapping', mapping)
        self.assertEqual(response.context['wizard']['steps'].current, 'preview')
        token = response.context['wizard']['form'].forms[0]['team'].value()
        self.speaker_token = token

    def test_separate_speaker_links_to_uploaded_team_and_waits_for_it(self):
        self.separate_speaker_preview()
        url = self.finish([{'name': 'Bob', 'email': 'bob@example.com', 'team': self.speaker_token}, self.row()])
        self.assertEqual(self.client.post(url, {'row': 0}).status_code, 409)
        self.assertEqual(self.client.post(url, {'row': 1}).json()['status'], 'imported')
        self.assertEqual(self.client.post(url, {'row': 0}).json()['status'], 'imported')
        self.assertEqual(Speaker.objects.get().team, Team.objects.get())

    def test_separate_speaker_links_to_existing_team(self):
        team = Team.objects.create(tournament=self.tournament, institution=self.institution, reference='A')
        self.separate_speaker_preview(existing=True)
        response = self.step('preview', self.preview_data([{'name': 'Bob', 'email': '', 'team': self.speaker_token}]))
        self.assertEqual(response.context['wizard']['steps'].current, 'confirm')
        url = self.step('confirm', {'confirm-confirm': 'on'}).url
        self.assertEqual(self.client.post(url, {'row': 0}).json()['status'], 'imported')
        self.assertEqual(Speaker.objects.get().team, team)

    def test_skipped_team_is_flagged_before_confirming(self):
        self.separate_speaker_preview()
        rows = [{'name': 'Bob', 'email': '', 'team': self.speaker_token}, self.row(DELETE='on')]
        response = self.step('preview', self.preview_data(rows))
        self.assertEqual(response.context['wizard']['steps'].current, 'preview')
        self.assertIn('linked row is skipped', str(response.context['wizard']['form'].forms[0].errors))
        self.assertEqual(response.context['file_groups'][0]['attention_count'], 1)
        self.assertFalse(Team.objects.exists())
        rows[0]['DELETE'] = 'on'
        url = self.finish(rows)
        self.assertEqual(self.client.post(url, {'row': 0}).json()['status'], 'skipped')
        self.assertFalse(Speaker.objects.exists())

    def test_failed_team_still_blocks_speaker_during_execution(self):
        from ..csv_pipeline import process_csv_row
        row = {'kind': 'speaker', 'status': 'pending', 'data': {'name': 'Bob', 'team': 'row:1'}}
        process_csv_row(self.tournament, self.user,
            {'rows': [row, {'status': 'failed'}], 'team_choices': [('row:1', 'Uploaded team')]}, row)
        self.assertEqual(row['status'], 'blocked')
        self.assertFalse(Speaker.objects.exists())

    def test_separate_speaker_cannot_select_other_tournament_team(self):
        self.separate_speaker_preview()
        response = self.step('preview', self.preview_data([{'name': 'Bob', 'team': 'existing:999999'}, self.row()]))
        self.assertEqual(response.context['wizard']['steps'].current, 'preview')
        self.assertTrue(response.context['wizard']['form'].errors)

    def test_preview_shows_mapped_errors_before_submission(self):
        response = self.preview(text='Team,Institution,Speaker 1 name,Speaker 1 email\nA,EU,,bad-email\n')
        form = response.context['wizard']['form'].forms[0]
        self.assertIn('speaker_1_email', form.errors)

    def test_back_navigation_keeps_preview_edits(self):
        self.preview()
        data = self.preview_data([self.row(reference='Edited')])
        self.step('preview', {**data, 'wizard_goto_step': 'mapping'})
        response = self.step('mapping', {'mapping-column_0_0': 'reference', 'mapping-column_0_1': 'institution',
            'mapping-column_0_2': 'speaker_1_name', 'mapping-column_0_3': 'speaker_1_email'})
        self.assertEqual(response.context['wizard']['form'].forms[0]['reference'].value(), 'Edited')

    def test_refresh_retains_draft_and_unskipping_revalidates(self):
        self.preview(text='Team,Institution,Speaker 1 name,Speaker 1 email\nA,EU,Alice,bad\n')
        self.assertEqual(self.client.get(self.url).context['wizard']['steps'].current, 'preview')
        self.step('preview', self.preview_data([self.row(speaker_1_email='bad', DELETE='on')]))
        response = self.step('confirm', {'wizard_goto_step': 'preview'})
        self.assertTrue(response.context['wizard']['form'].forms[0]['DELETE'].value())
        response = self.step('preview', self.preview_data([self.row(speaker_1_email='bad')]))
        self.assertEqual(response.context['wizard']['steps'].current, 'preview')
        self.assertIn('speaker_1_email', response.context['wizard']['form'].forms[0].errors)

    def test_filename_detection_is_case_insensitive_and_editable(self):
        self.assertEqual(guess_file_type('TEAMS.csv'), 'team')
        self.assertEqual(guess_file_type('Registration_SpEaKeRs_2026.csv'), 'speaker')
        self.assertEqual(guess_file_type('responses.csv'), '')
        self.assertEqual(guess_file_type('teams-and-speakers.csv'), '')
        form = CSVTypesForm(data={'file_0': 'team'}, sources=[{'name': 'speakers.csv'}])
        self.assertEqual(form['file_0'].initial, 'speaker')
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['file_0'], 'team')
        self.assertEqual(len(form.fields), 1)

    def test_mapping_has_a_card_for_each_file(self):
        self.separate_speaker_preview()
        response = self.step('preview', {'wizard_goto_step': 'mapping'})
        groups = response.context['wizard']['form'].file_groups
        self.assertEqual([(group['name'], str(group['type_label'])) for group in groups],
            [('speakers.csv', 'Speakers'), ('teams.csv', 'Teams')])
        self.assertContains(response, 'data-csv-mapping-file', count=2)
        self.assertEqual(str(response.context['csv_vue_data']['files'][0]['type_label']), 'Speakers')
        self.assertEqual(response.context['page_emoji'], '📄')
        self.assertIn('Map CSV columns', str(response.context['page_title']))

    def test_inline_speaker_fields_are_inferred_per_file(self):
        self.upload('Team,First person,Second person\nA,Alice,Bob\n')
        self.step('types', {'types-file_0': 'team'})
        response = self.step('mapping', {'mapping-column_0_0': 'reference',
            'mapping-column_0_1': 'speaker_1_name', 'mapping-column_0_2': 'speaker_2_name'})
        form = response.context['wizard']['form'].forms[0]
        self.assertEqual(form.slots, 2)
        self.assertEqual(form['speaker_2_name'].value(), 'Bob')
        self.assertNotIn('speaker_3_name', form.fields)
        url = self.finish([self.row(institution='', speaker_1_name='Alice', speaker_1_email='',
            speaker_2_name='Bob', speaker_2_email='', use_institution_prefix='False')])
        self.assertEqual(self.client.post(url, {'row': 0}).json()['status'], 'imported')
        self.assertEqual(set(Speaker.objects.values_list('name', flat=True)), {'Alice', 'Bob'})

    def test_anorak_speaker_headers_are_mapped(self):
        form = CSVMappingForm(sources=[{'name': 'speakers.csv', 'headers': ['name', 'team_name', 'institution', 'email'],
            'rows': [{'values': ['Alice', 'A', 'EU', 'alice@example.com']}]}], types={'file_0': 'speaker'})
        self.assertEqual([field.value() for field in form], ['name', 'team', 'institution', 'email'])

    def test_registered_type_uses_wizard_and_execution_without_view_changes(self):
        class GuestCSVType(SpeakerCSVType):
            key = 'guest'
            label = 'Guest speakers'
            filename_words = ('guests',)

        team = Team.objects.create(tournament=self.tournament, institution=self.institution, reference='A')
        with patch.dict(CSV_TYPES):
            register_csv_type(GuestCSVType())
            self.assertEqual(guess_file_type('guests.csv'), 'guest')
            self.upload('Name,Team\nGuest,A\n')
            self.step('types', {'types-file_0': 'guest'})
            self.step('mapping', {'mapping-column_0_0': 'name', 'mapping-column_0_1': 'team'})
            response = self.step('preview', self.preview_data([{'name': 'Guest', 'email': '', 'team': f'existing:{team.pk}'}]))
            self.assertEqual(response.context['wizard']['steps'].current, 'confirm')
            url = self.step('confirm', {'confirm-confirm': 'on'}).url
            self.assertEqual(self.client.post(url, {'row': 0}).json()['status'], 'imported')
            self.assertEqual(Speaker.objects.get().team, team)

    def test_upload_requires_files_and_uses_title_mixin(self):
        url = reverse_tournament('importer-csv-upload', self.tournament)
        response = self.client.get(url)
        self.assertEqual(str(response.context['page_title']), 'CSV Importer')
        self.assertEqual(response.context['page_emoji'], '📄')
        response = self.client.post(url, {'encoding': 'utf-8-sig', 'delimiter': '', 'header_row': 1})
        self.assertEqual(response.status_code, 200)
        self.assertIn('files', response.context['form'].errors)

    def test_speaker_only_csv_creates_one_shared_team(self):
        self.upload('name,team_name,institution,prefix\nAlice,A,EU,yes\nBob,A,EU,yes\n')
        self.step('types', {'types-file_0': 'speaker'})
        response = self.step('mapping', {'mapping-column_0_0': 'name', 'mapping-column_0_1': 'team',
            'mapping-column_0_2': 'institution', 'mapping-column_0_3': 'use_institution_prefix'})
        self.assertEqual(response.context['wizard']['steps'].current, 'preview')
        forms = response.context['wizard']['form']
        self.assertTrue(forms.is_valid(), forms.errors)
        self.assertEqual(forms.forms[0]['team'].value(), 'new')
        rows = [CSV_TYPES['speaker'].serialize(form.cleaned_data) for form in forms.forms]
        url = self.finish(rows)
        for index in range(2):
            self.assertEqual(self.client.post(url, {'row': index}).json()['status'], 'imported')
        self.assertEqual(Team.objects.count(), 1)
        self.assertEqual(Team.objects.get().short_name, 'EU A')
        self.assertEqual(Speaker.objects.count(), 2)

    def test_new_team_and_first_speaker_roll_back_together(self):
        self.separate_speaker_preview(existing=True)
        url = self.finish([{'name': 'Bob', 'team': 'new', 'team_name': 'A',
            'institution': self.institution.pk, 'use_institution_prefix': 'False'}])
        with patch('importer.csv_types.populate_url_keys', side_effect=[None, ValidationError('failure')]):
            self.assertEqual(self.client.post(url, {'row': 0}).json()['status'], 'failed')
        self.assertFalse(Team.objects.exists())
        self.assertFalse(Speaker.objects.exists())

    def test_unmatched_institution_is_a_preview_error_and_can_be_skipped(self):
        response = self.preview(text='Team,Institution\nA,Unknown university\n', speakers=0)
        form = response.context['wizard']['form'].forms[0]
        self.assertIn('institution', form.errors)
        self.assertEqual(form['institution'].value(), 'unresolved:Unknown university')
        url = self.finish([self.row(institution='unresolved:Unknown university', DELETE='on')])
        self.assertEqual(self.client.post(url, {'row': 0}).json()['status'], 'skipped')

    def test_ambiguous_team_requires_preview_selection(self):
        for reference in ('A', 'EU A'):
            Team.objects.create(tournament=self.tournament, institution=self.institution,
                reference=reference, use_institution_prefix=True)
        self.upload('name,team_name,institution\nAlice,EU A,EU\n')
        self.step('types', {'types-file_0': 'speaker'})
        response = self.step('mapping', {'mapping-column_0_0': 'name', 'mapping-column_0_1': 'team',
            'mapping-column_0_2': 'institution'})
        self.assertIn('team', response.context['wizard']['form'].forms[0].errors)

    def test_edited_new_team_reference_links_to_edited_uploaded_team(self):
        self.separate_speaker_preview()
        url = self.finish([{'name': 'Bob', 'team': 'new', 'team_name': 'Edited',
            'institution': self.institution.pk, 'use_institution_prefix': 'False'}, self.row(reference='Edited')])
        self.assertEqual(self.client.post(url, {'row': 0}).status_code, 409)
        self.assertEqual(self.client.post(url, {'row': 1}).json()['status'], 'imported')
        self.assertEqual(self.client.post(url, {'row': 0}).json()['status'], 'imported')
        self.assertEqual(Team.objects.count(), 1)
        self.assertEqual(Speaker.objects.get().team.reference, 'Edited')

    def test_speaker_team_identity_includes_institution(self):
        from ..csv_pipeline import process_csv_row
        rows = [{'kind': 'speaker', 'status': 'pending', 'data': {'name': name, 'team': 'new',
            'team_name': 'A', 'institution': institution, 'use_institution_prefix': 'False'}}
            for name, institution in [('Alice', ''), ('Bob', ''), ('Alice', self.institution.pk)]]
        draft = {'rows': rows, 'team_choices': []}
        for row in rows:
            process_csv_row(self.tournament, self.user, draft, row)
            self.assertEqual(row['status'], 'imported', row)
        self.assertEqual(Team.objects.count(), 2)
        self.assertEqual(Speaker.objects.filter(team__institution=None).count(), 2)

    def test_file_previews_group_rows_and_keep_all_edit_controls(self):
        self.separate_speaker_preview()
        response = self.client.get(self.url)
        groups = response.context['file_groups']
        self.assertEqual([group['name'] for group in groups], ['speakers.csv', 'teams.csv'])
        self.assertEqual(groups[0]['rows'][0]['name'], 'Bob')
        self.assertEqual(groups[0]['rows'][0]['source']['file'], 'speakers.csv')
        self.assertIn('teams.csv', str(groups[0]['rows'][0]['related']))
        self.assertContains(response, 'data-csv-panel=', count=2)
        self.assertContains(response, 'name="preview-0-name"')
        self.assertContains(response, 'name="preview-1-reference"')
        self.assertFalse(Team.objects.exists())

    def test_confirmation_counts_inline_speakers_and_source_rows_separately(self):
        self.preview()
        response = self.step('preview', self.preview_data([self.row()]))
        self.assertEqual(response.context['import_count'], 1)
        self.assertEqual({str(item['label']): item['count'] for item in response.context['object_counts']},
            {'Teams': 1, 'Speakers': 1})
        self.assertFalse(Team.objects.exists())

    def test_multiple_files_of_the_same_type_are_supported(self):
        form = CSVUploadForm(data={'encoding': 'utf-8-sig', 'delimiter': ',', 'header_row': 1}, files={
            'files': [SimpleUploadedFile(f'teams-{index}.csv', b'Team\nExample\n') for index in range(14)]})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(len(form.cleaned_data['parsed']), 14)

    def test_download_templates_have_mappable_headers(self):
        import csv
        import io
        for template, kind in [('teams', 'team'), ('teams-with-speakers', 'team'), ('speakers', 'speaker')]:
            with self.subTest(template=template):
                response = self.client.get(reverse_tournament('importer-csv-template', self.tournament,
                    kwargs={'template_key': template}))
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')
                self.assertEqual(guess_file_type(template + '.csv'), kind)
                headers = next(csv.reader(io.StringIO(response.content.decode('utf-8-sig'))))
                source = {'name': template + '.csv', 'headers': headers, 'rows': [{'values': [''] * len(headers)}]}
                form = CSVMappingForm(sources=[source], types={'file_0': kind})
                targets = [field.value() for field in form]
                self.assertTrue(all(targets))
                self.assertTrue(set(CSV_TYPES[kind].required_targets).issubset(targets))
                if template == 'teams-with-speakers':
                    self.assertIn('speaker_2_email', targets)
        self.assertEqual(self.client.get(reverse_tournament('importer-csv-template', self.tournament,
            kwargs={'template_key': 'unknown'})).status_code, 404)

    def test_template_download_requires_admin(self):
        self.client.force_login(get_user_model().objects.create_user('template-reader', password='password'))
        response = self.client.get(reverse_tournament('importer-csv-template', self.tournament,
            kwargs={'template_key': 'teams'}))
        self.assertEqual(response.status_code, 403)
