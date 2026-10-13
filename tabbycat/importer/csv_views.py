"""Small, session-backed team CSV wizard. No uploaded files are retained."""

import csv
import uuid

from django.core.cache import cache
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.utils.functional import cached_property
from django.utils.translation import gettext as _, gettext_lazy
from django.views.generic import FormView, TemplateView, View
from formtools.wizard.views import SessionWizardView

from tournaments.mixins import TournamentMixin
from users.permissions import Permission
from utils.misc import reverse_tournament
from utils.mixins import AdministratorMixin, TabbycatPageTitlesMixin

from .csv_forms import (CSV_MAX_FILE_SIZE_MIB, CSV_MAX_FILES, CSV_MAX_ROWS,
                        CSVConfirmForm, CSVMappingForm, CSVPreviewFormSet,
                        CSVTypesForm, CSVUploadForm, mapped_rows)
from .csv_pipeline import CSVImportContext, process_csv_row
from .csv_types import CSV_TYPES, DependencyPendingError


CSV_STEP_TITLES = {
    'upload': gettext_lazy('Upload files'),
    'types': gettext_lazy('Choose file types'),
    'mapping': gettext_lazy('Map CSV columns'),
    'preview': gettext_lazy('Preview and edit rows'),
    'confirm': gettext_lazy('Review and import'),
}


class CSVAccessMixin(AdministratorMixin, TournamentMixin, TabbycatPageTitlesMixin):
    page_title = gettext_lazy('CSV Importer')
    page_emoji = '📄'
    edit_permission = Permission.ADD_TEAMS

    @property
    def draft_key(self):
        return 'csv_import_' + str(self.kwargs['import_id'])

    @property
    def draft(self):
        draft = self.request.session.get(self.draft_key)
        if not draft or draft['tournament'] != self.tournament.pk or draft['user'] != self.request.user.pk:
            raise Http404(_('This import has expired. Upload the CSV files again.'))
        return draft

    def draft_url(self, name):
        return reverse_tournament(name, self.tournament, kwargs={'import_id': self.kwargs['import_id']})


class CSVUploadView(CSVAccessMixin, FormView):
    template_name = 'csv_upload.html'
    form_class = CSVUploadForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['csv_limits'] = {'files': CSV_MAX_FILES, 'size': CSV_MAX_FILE_SIZE_MIB, 'rows': CSV_MAX_ROWS}
        context['csv_templates'] = [{'key': key, 'label': label}
            for kind in CSV_TYPES.values() for key, label, columns in kind.templates]
        context['csv_vue_data'] = {'steps': [{'key': key, 'label': label,
            'state': 'current' if key == 'upload' else 'upcoming'} for key, label in CSV_STEP_TITLES.items()]}
        return context

    def form_valid(self, form):
        import_id = uuid.uuid4()
        self.request.session['csv_import_' + str(import_id)] = {
            'tournament': self.tournament.pk, 'user': self.request.user.pk,
            'files': form.cleaned_data['parsed'], 'started': False,
        }
        return redirect(reverse_tournament('importer-csv-wizard', self.tournament, kwargs={'import_id': import_id}))


class CSVTemplateView(CSVAccessMixin, View):
    def get(self, request, *args, **kwargs):
        key = kwargs['template_key']
        columns = next((columns for kind in CSV_TYPES.values() for name, label, columns in kind.templates if name == key), None)
        if columns is None:
            raise Http404
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{key}.csv"'
        # Excel recognizes UTF-8 CSV files with a byte-order mark.
        response.write('\ufeff')
        csv.writer(response).writerow(columns)
        return response


class CSVWizardView(CSVAccessMixin, SessionWizardView):
    template_name = 'csv_wizard.html'
    form_list = [('types', CSVTypesForm), ('mapping', CSVMappingForm),
        ('preview', CSVPreviewFormSet), ('confirm', CSVConfirmForm)]
    step_titles = {key: label for key, label in CSV_STEP_TITLES.items() if key != 'upload'}

    def get_page_title(self):
        return _('%(title)s — %(step)s') % {'title': self.page_title, 'step': self.step_titles[self.steps.current]}

    def get_prefix(self, request, *args, **kwargs):
        return 'csv_' + str(self.kwargs['import_id'])

    def get(self, request, *args, **kwargs):
        if self.draft['started']:
            return redirect(self.draft_url('importer-csv-results'))
        if self.storage.current_step not in self.get_form_list():
            self.storage.current_step = self.steps.first
        return self.render(self.get_form(data=self.storage.get_step_data(self.steps.current)))

    def post(self, *args, **kwargs):
        if self.draft['started']:
            return redirect(self.draft_url('importer-csv-results'))
        return super().post(*args, **kwargs)

    def get_form_kwargs(self, step=None):
        files = self.draft['files']
        if step == 'types':
            return {'sources': files}
        if step == 'mapping':
            return {'sources': files, 'types': self.get_cleaned_data_for_step('types') or {f'file_{i}': 'team' for i in range(len(files))}}
        if step == 'preview':
            return {'form_kwargs': {'tournament': self.tournament, 'team_choices': self.import_context().team_options[0], 'references': self.import_context().references}}
        return {}

    def get_form(self, step=None, data=None, files=None):
        step = step or self.steps.current
        if step == 'preview' and data is not None:
            # Preserve edits in drafts opened before team creation fields existed,
            # while filling the newly introduced fields from their CSV values.
            data = data.copy()
            for index, initial in enumerate(self.get_form_initial(step)):
                prefix = f'preview-{index}-'
                CSV_TYPES[initial['_kind']].restore_preview(data, prefix, initial)
        form = super().get_form(step=step, data=data, files=files)
        if step == 'preview' and data is None:
            # Validate the mapped values on arrival, without waiting for a POST.
            values = {f'{form.prefix}-TOTAL_FORMS': len(form.forms),
                f'{form.prefix}-INITIAL_FORMS': len(form.forms)}
            for row in form.forms:
                for name in row.fields:
                    value = row[name].value()
                    if name != 'DELETE' and value is not None:
                        values[row.add_prefix(name)] = str(value)
            form = super().get_form(step=step, data=values, files=files)
            form.is_valid()
        return form

    def source_rows(self):
        return mapped_rows(self.draft['files'], self.get_cleaned_data_for_step('mapping') or {},
            self.get_cleaned_data_for_step('types') or {})

    @cached_property
    def csv_context(self):
        return CSVImportContext(self.tournament, self.source_rows())

    def import_context(self):
        return self.csv_context

    def get_form_initial(self, step):
        if step == 'preview':
            return self.import_context().initial_rows()
        return super().get_form_initial(step)

    def render_goto_step(self, goto_step, **kwargs):
        steps = list(self.get_form_list())
        if goto_step not in steps or steps.index(goto_step) >= self.steps.step0:
            return self.render(self.get_form(data=self.storage.get_step_data(self.steps.current)))
        # Preserve edits even when navigating back through a currently invalid form.
        if self.steps.current:
            self.storage.set_step_data(self.steps.current, self.request.POST)
        return super().render_goto_step(goto_step, **kwargs)

    def process_step(self, form):
        data = super().process_step(form)
        old = self.storage.get_step_data(self.steps.current)

        def comparable(values):
            return {key: values.getlist(key) for key in values if key.startswith(self.steps.current + '-')}

        if old is not None and comparable(old) != comparable(data):
            steps = list(self.get_form_list())
            for step in steps[steps.index(self.steps.current) + 1:]:
                self.storage.set_step_data(step, None)
        return data

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        files = self.draft['files']
        context['files'] = files
        context['row_count'] = sum(len(source['rows']) for source in files)
        types = self.get_cleaned_data_for_step('types') or {}
        groups = [{'index': index, 'name': source['name'], 'row_count': len(source['rows']),
            'type_label': CSV_TYPES[types[f'file_{index}']].label if f'file_{index}' in types else '',
            'attention_count': 0, 'skip_count': 0, 'rows': []} for index, source in enumerate(files)]
        if self.steps.current == 'types':
            for group in groups:
                group['type_field'] = form[f"file_{group['index']}"]
        if self.steps.current == 'mapping':
            for group, mapping in zip(groups, form.file_groups):
                group['fields'] = mapping['fields']
                group['attention_count'] = sum(bool(field.errors) for field in group['fields'])
                group['mapped_count'] = sum(bool(field.value()) for field in group['fields'])
        if self.steps.current in ('preview', 'confirm'):
            preview = form if self.steps.current == 'preview' else self.get_form(
                step='preview', data=self.storage.get_step_data('preview'))
            preview.is_valid()
            context['preview_rows'] = list(zip(self.source_rows(), preview.forms))
            object_counts = {}
            additional_objects = set()
            for index, (source, row_form) in enumerate(context['preview_rows']):
                kind = CSV_TYPES[source['kind']]
                skipped = bool(row_form['DELETE'].value())
                invalid = bool(row_form.errors) and not skipped
                summary = kind.preview_summary(row_form)
                groups[source['file_index']]['rows'].append({'index': index, 'source': source, 'form': row_form,
                    **summary, 'status': 'skipped' if skipped else 'attention' if invalid else 'ready'})
                groups[source['file_index']]['attention_count'] += int(invalid)
                groups[source['file_index']]['skip_count'] += int(skipped)
                if not skipped and not invalid:
                    for key, count in kind.object_counts(row_form).items():
                        object_counts[key] = object_counts.get(key, 0) + count
                    additional_objects.update(kind.additional_objects(row_form))
            for key, identity in additional_objects:
                object_counts[key] = object_counts.get(key, 0) + 1
            context['object_counts'] = [{'label': CSV_TYPES[key].label, 'count': count} for key, count in object_counts.items() if count]
            context['skip_count'] = sum(group['skip_count'] for group in groups)
            context['attention_count'] = sum(group['attention_count'] for group in groups)
            context['import_count'] = context['row_count'] - context['skip_count']
        context['csv_vue_data'] = {'files': [self.vue_file_data(group) for group in groups]}
        context['file_groups'] = groups
        context['step_list'] = [{'key': 'upload', 'label': _('Upload files'), 'state': 'complete',
            'href': reverse_tournament('importer-csv-upload', self.tournament)}] + [
            {'key': key, 'label': label, 'value': key if index < self.steps.step0 else None, 'state': 'current' if key == self.steps.current else
                'complete' if index < self.steps.step0 else 'upcoming'}
            for index, (key, label) in enumerate(self.step_titles.items())]
        context['csv_vue_data']['steps'] = context['step_list']
        return context

    @staticmethod
    def vue_file_data(group):
        data = {key: group[key] for key in ('index', 'name', 'row_count', 'type_label', 'attention_count')}
        data['mapped_count'] = group.get('mapped_count', 0)
        data['rows'] = []
        for row in group['rows']:
            data['rows'].append({
                'index': row['index'],
                'name': row['name'],
                'related': row['related'],
                'file': row['source']['file'],
                'line': row['source']['line'],
                'skip_name': row['form']['DELETE'].html_name,
                'skipped': bool(row['form']['DELETE'].value()),
                'invalid': bool(row['form'].errors),
            })
        return data

    def done(self, form_list, form_dict, **kwargs):
        draft = self.draft
        results = []
        for source, form in zip(self.source_rows(), form_dict['preview'].forms):
            data = form.cleaned_data.copy()
            skipped = data.pop('DELETE', False)
            kind = CSV_TYPES[source['kind']]
            if not skipped:
                data = kind.serialize(data)
            results.append({'file': source['file'], 'line': source['line'],
                'kind': source['kind'], 'status': 'skipped' if skipped else 'pending', 'data': {} if skipped else data, 'errors': ''})
        draft.update(started=True, rows=results, team_choices=self.import_context().team_options[0])
        draft.pop('files', None)
        self.request.session[self.draft_key] = draft
        return redirect(self.draft_url('importer-csv-results'))


class CSVResultsView(CSVAccessMixin, TemplateView):
    template_name = 'csv_results.html'
    page_title = gettext_lazy('CSV Importer — results')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.draft['started']:
            raise Http404
        context['rows'] = [{**row, 'priority': CSV_TYPES[row['kind']].priority,
            'display_name': row['data'].get(CSV_TYPES[row['kind']].name_field, '')} for row in self.draft['rows']]
        context['step_list'] = [{'label': label, 'state': 'complete'} for label in
            (_('Upload files'), _('Choose file types'), _('Map CSV columns'), _('Preview and edit rows'))] + [
            {'label': _('Import results'), 'state': 'current'}]
        context['csv_vue_data'] = {'rows': context['rows'], 'steps': context['step_list']}
        return context

    def post(self, request, *args, **kwargs):
        # A cache lock serializes tabs; refresh the session only after acquiring it.
        lock = self.draft_key + '_lock'
        if not cache.add(lock, True, timeout=120):
            return JsonResponse({'error': _('This import is already processing a row.')}, status=409)
        try:
            request.session._session_cache = request.session.load()
            draft = self.draft
            if not draft['started']:
                raise Http404
            try:
                index = int(request.POST['row'])
                if index < 0:
                    raise ValueError
                row = draft['rows'][index]
            except (KeyError, ValueError, IndexError):
                return JsonResponse({'error': _('Invalid import row.')}, status=400)
            if row['status'] == 'pending':
                try:
                    process_csv_row(self.tournament, request.user, draft, row)
                except DependencyPendingError:
                    return JsonResponse({'error': _('Import the linked team first.')}, status=409)
                draft['rows'][index] = row
                request.session[self.draft_key] = draft
                request.session.save()
            labels = {'pending': _('Pending'), 'imported': _('Imported'), 'skipped': _('Skipped'),
                'failed': _('Failed'), 'blocked': _('Blocked')}
            return JsonResponse({'status': row['status'], 'label': labels[row['status']], 'errors': row['errors']})
        finally:
            cache.delete(lock)


class CSVErrorsView(CSVAccessMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="csv-import-results.csv"'
        writer = csv.writer(response)
        writer.writerow([_('File'), _('Row'), _('Status'), _('Errors')])
        for row in self.draft.get('rows', []):
            # Prevent spreadsheet formula evaluation in an exported report.
            values = [str(row[key]) for key in ('file', 'line', 'status', 'errors')]
            writer.writerow(["'" + value if value.startswith(('=', '+', '-', '@', '\t', '\r')) else value for value in values])
        return response
