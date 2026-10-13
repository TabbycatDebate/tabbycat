"""Forms for the session-backed team CSV importer."""

import csv
import io

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from participants.models import Institution, Speaker, Team

from .csv_types import CSV_TYPES, guess_file_type
from .forms import BaseTournamentObjectDetailsForm
from .importers.base import convert_bool


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        clean = super().clean
        if not data:
            return clean(None, initial)
        return [clean(item, initial) for item in (data if isinstance(data, (list, tuple)) else [data])]


class CSVUploadForm(forms.Form):
    files = MultipleFileField(label=_("CSV files"), widget=MultipleFileInput(attrs={'accept': '.csv,text/csv'}))
    encoding = forms.ChoiceField(choices=[('utf-8-sig', 'UTF-8'), ('cp1252', 'Windows-1252')])
    delimiter = forms.ChoiceField(required=False, choices=[('', _('Detect automatically')), (',', _('Comma')),
        (';', _('Semicolon')), ('\t', _('Tab'))])
    header_row = forms.IntegerField(min_value=1, max_value=100, initial=1, label=_("Header row"))

    def clean(self):
        data = super().clean()
        if self.errors:
            return data
        files = data['files']
        if len(files) > 20:
            raise ValidationError(_("Upload at most 20 CSV files at a time."))
        parsed = []
        total = 0
        for upload in files:
            if upload.size > 2 * 1024 * 1024:
                raise ValidationError(_("Each CSV must be smaller than 2 MiB."))
            try:
                text = upload.read().decode(data['encoding'])
                delimiter = data['delimiter']
                if not delimiter:
                    try:
                        delimiter = csv.Sniffer().sniff(text[:8192], delimiters=',;\t').delimiter
                    except csv.Error:
                        delimiter = ','
                reader = csv.reader(io.StringIO(text, newline=''), delimiter=delimiter, strict=True)
                for unused in range(data['header_row'] - 1):
                    next(reader)
                headers = next(reader)
                if not headers or len(headers) > 100:
                    raise ValidationError(_("Choose a header row containing between 1 and 100 columns."))
                rows = []
                for values in reader:
                    if not any(value.strip() for value in values):
                        continue
                    if len(values) != len(headers):
                        raise ValidationError(_("%(file)s, line %(line)s: the number of cells does not match the headers.") % {
                            'file': upload.name, 'line': reader.line_num})
                    rows.append({'line': reader.line_num, 'values': [value.strip() for value in values]})
                    total += 1
                    if total > 1000:
                        raise ValidationError(_("Upload at most 1,000 rows in total."))
                if not rows:
                    raise ValidationError(_("%(file)s contains no data rows.") % {'file': upload.name})
                parsed.append({'name': upload.name, 'headers': headers, 'rows': rows})
            except UnicodeDecodeError:
                raise ValidationError(_("Unable to decode %(file)s. Try another encoding.") % {'file': upload.name})
            except (csv.Error, StopIteration):
                raise ValidationError(_("Unable to read %(file)s. Check the delimiter and header row.") % {'file': upload.name})
        data['parsed'] = parsed
        return data


class CSVTypesForm(forms.Form):
    def __init__(self, *args, sources, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [('', _('Choose a file type'))] + [(kind.key, kind.label) for kind in CSV_TYPES.values()]
        for index, source in enumerate(sources):
            self.fields[f'file_{index}'] = forms.ChoiceField(initial=guess_file_type(source['name']),
                label=source['name'], choices=choices)


class CSVMappingForm(forms.Form):
    def __init__(self, *args, sources, types, **kwargs):
        super().__init__(*args, **kwargs)
        self.sources = sources
        self.types = types
        self.file_groups = []
        for index, source in enumerate(sources):
            kind = CSV_TYPES[types[f'file_{index}']]
            choices = [('', _('Ignore this column'))] + kind.mapping_choices(source)
            used = set()
            field_names = []
            for column, header in enumerate(source['headers']):
                guess = kind.guess_column(header)
                if guess not in dict(choices) or guess in used:
                    guess = ''
                used.add(guess)
                name = f'column_{index}_{column}'
                self.fields[name] = forms.ChoiceField(required=False, choices=choices, initial=guess,
                    label=_('Column %(number)d: %(header)s') % {'number': column + 1, 'header': header},
                    help_text=_('Example: %(value)s') % {'value': source['rows'][0]['values'][column]})
                field_names.append(name)
            self.file_groups.append({'name': source['name'], 'type_label': kind.label,
                'fields': [self[name] for name in field_names]})

    def clean(self):
        data = super().clean()
        field_count = 10
        for index, source in enumerate(self.sources):
            kind = CSV_TYPES[self.types[f'file_{index}']]
            targets = [data.get(f'column_{index}_{column}') for column in range(len(source['headers']))]
            selected = [target for target in targets if target]
            missing = set(kind.required_targets) - set(selected)
            if missing:
                labels = dict(kind.mapping_choices(source))
                raise ValidationError(_('Map the required columns in %(file)s: %(fields)s.') % {
                    'file': source['name'], 'fields': ', '.join(str(labels[field]) for field in sorted(missing))})
            if len(selected) != len(set(selected)):
                raise ValidationError(_('Map each target field only once in %(file)s.') % {'file': source['name']})
            field_count += len(source['rows']) * kind.preview_field_count(selected)
        limit = settings.DATA_UPLOAD_MAX_NUMBER_FIELDS
        if limit is not None and field_count > limit:
            raise ValidationError(_('This preview has too many fields. Split the CSV into smaller files and import separately.'))
        return data


def mapped_rows(files, mapping, types=None):
    rows = []
    for index, source in enumerate(files):
        for row in source['rows']:
            values = {mapping[f'column_{index}_{column}']: value for column, value in enumerate(row['values'])
                if mapping.get(f'column_{index}_{column}')}
            kind = (types or {}).get(f'file_{index}', 'team')
            rows.append({'file': source['name'], 'file_index': index, 'line': row['line'], 'values': values, 'kind': kind})
    return rows


def configure_institution_field(field, initial):
    field.label_from_instance = lambda inst: f'{inst.name} ({inst.code})'
    field.empty_label = _('Unaffiliated')
    if isinstance(initial, str) and initial.startswith('unresolved:'):
        field.choices = [*field.choices, (initial, _('Unmatched: %(value)s') % {'value': initial.split(':', 1)[1]})]
        field.error_messages['invalid_choice'] = _('Choose an existing institution, select Unaffiliated, or skip this row.')


class CSVSpeakerForm(forms.Form):
    name = forms.CharField(max_length=Speaker._meta.get_field('name').max_length, label=_('Speaker name'))
    email = forms.EmailField(required=False, max_length=Speaker._meta.get_field('email').max_length, label=_('Email'))
    team = forms.ChoiceField(label=_('Team'))
    institution = forms.ModelChoiceField(queryset=Institution.objects.all(), required=False, label=_('Institution for new team'))
    team_name = forms.CharField(required=False, max_length=150, label=_('New team name / suffix'))
    use_institution_prefix = forms.TypedChoiceField(required=False, empty_value=False,
        coerce=lambda value: convert_bool(str(value)), choices=[('False', _('No')), ('True', _('Yes'))],
        initial='False', label=_('Prefix new team name with institution'))

    def __init__(self, tournament, *args, slots=0, team_choices=(), **kwargs):
        super().__init__(*args, **kwargs)
        self.tournament = tournament
        self.fields['team'].choices = [('', _('Choose a team')), ('new', _('Create or use team from the name and institution below'))] + list(team_choices)
        configure_institution_field(self.fields['institution'], self.initial.get('institution'))

    def clean(self):
        data = super().clean()
        token = data.get('team', '')
        if token == 'new':
            if not data.get('team_name'):
                self.add_error('team_name', _('Enter the name of the team to create.'))
            if data.get('use_institution_prefix') and not data.get('institution'):
                self.add_error('institution', _('Select an institution to use an institutional prefix.'))
        if token.startswith('existing:') and data.get('name'):
            if Speaker.objects.filter(team_id=token.split(':')[1], team__tournament=self.tournament, name=data['name']).exists():
                self.add_error('name', _('A speaker with this name already belongs to this team. Skip or correct this row.'))
        return data


class CSVTeamForm(BaseTournamentObjectDetailsForm):
    use_institution_prefix = forms.TypedChoiceField(coerce=lambda value: convert_bool(str(value)), choices=[('False', _('No')), ('True', _('Yes'))],
        initial='False', label=_('Prefix team name with institution'))

    class Meta:
        model = Team
        fields = ('reference', 'institution', 'use_institution_prefix', 'seed')

    def __init__(self, tournament, *args, slots=0, team_choices=(), **kwargs):
        super().__init__(tournament, *args, **kwargs)
        self.slots = slots
        configure_institution_field(self.fields['institution'], self.initial.get('institution'))
        for n in range(1, slots + 1):
            self.fields[f'speaker_{n}_name'] = forms.CharField(required=False,
                max_length=Speaker._meta.get_field('name').max_length, label=_('Speaker %(number)d name') % {'number': n})
            self.fields[f'speaker_{n}_email'] = forms.EmailField(required=False,
                max_length=Speaker._meta.get_field('email').max_length, label=_('Speaker %(number)d email') % {'number': n})

    def clean(self):
        data = super().clean()
        self.instance.short_reference = data.get('reference', '')[:35]
        for n in range(1, self.slots + 1):
            name, email = data.get(f'speaker_{n}_name'), data.get(f'speaker_{n}_email')
            if email and not name:
                self.add_error(f'speaker_{n}_name', _('Enter a name for this speaker or clear the email.'))
        if 'reference' in data and 'institution' in data and Team.objects.all_with_unconfirmed.filter(
                tournament=self.tournament, reference=data['reference'], institution=data['institution']).exists():
            self.add_error('reference', _('A team with this name and institution already exists. Skip this row or change its name.'))
        return data


class CSVPreviewFormSet(forms.BaseFormSet):
    deletion_widget = forms.CheckboxInput

    def _construct_form(self, i, **kwargs):
        original = self.form
        if i < len(self.initial):
            self.form = CSV_TYPES[self.initial[i].get('_kind', 'team')].form_class
        try:
            return super()._construct_form(i, **kwargs)
        finally:
            self.form = original

    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        if index is not None and index < len(self.initial):
            row = self.initial[index]
            kwargs.update(CSV_TYPES[row.get('_kind', 'team')].form_options(row))
        return kwargs

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.forms:
            form.fields['DELETE'].label = _('Skip')
            form.fields['DELETE'].widget.attrs['aria-label'] = _('Skip this row')

    def clean(self):
        super().clean()
        if self.total_form_count() != len(self.initial) or self.initial_form_count() != len(self.initial):
            raise ValidationError(_('The number of preview rows changed. Reload the preview.'))
        seen = set()
        for index, form in enumerate(self.forms):
            if self._should_delete_form(form) or form.errors:
                continue
            kind = CSV_TYPES[self.initial[index].get('_kind', 'team')]
            kind.resolve_preview(form, self.forms)
            if form.errors:
                continue
            for dependency in kind.preview_dependencies(form.cleaned_data):
                parent = self.forms[dependency]
                if parent.cleaned_data.get('DELETE') or parent.errors:
                    form.add_error(None, _('The linked row is skipped or has errors. Select another reference, correct the linked row, or skip this row.'))
            if form.errors:
                continue
            key = kind.duplicate_key(form.cleaned_data)
            if key in seen:
                form.add_error(kind.name_field, _('This participant appears more than once in the uploaded files. Skip or correct this row.'))
            seen.add(key)


CSVPreviewFormSet = forms.formset_factory(CSVTeamForm, formset=CSVPreviewFormSet, extra=0, can_delete=True)


class CSVConfirmForm(forms.Form):
    confirm = forms.BooleanField(label=_("Import the reviewed rows, excluding rows marked Skip."))
