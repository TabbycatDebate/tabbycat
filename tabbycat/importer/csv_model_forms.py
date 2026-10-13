"""Editable model rows with cached, existing or uploaded references."""

from django import forms
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from .csv_values import convert_bool
from .references import ImportReferences, reference_value


class CSVReferenceField(forms.Field):
    widget = forms.Select

    def __init__(self, kind, references, *args, multiple=False, **kwargs):
        self.kind = kind
        self.references = references
        self.multiple = multiple
        if multiple:
            kwargs['widget'] = forms.SelectMultiple
        super().__init__(*args, **kwargs)
        self.widget.choices = [('', _('None')), *references.choices(kind)]
        initial = kwargs.get('initial') or []
        if not isinstance(initial, (list, tuple)):
            initial = [initial]
        for token in initial:
            if isinstance(token, str) and token.startswith(('new:', 'unresolved:')):
                self.widget.choices.append((token, token.split(':', 1)[1]))

    def to_python(self, value):
        if value in self.empty_values:
            return [] if self.multiple else None
        values = value if self.multiple and isinstance(value, (list, tuple)) else [value]
        try:
            objects = [self.references.get_object(self.kind, token) for token in values if token != '']
        except ValidationError as error:
            raise ValidationError(error.messages, code='invalid_reference')
        except (ObjectDoesNotExist, TypeError):
            raise ValidationError(_('Choose an existing or uploaded reference, or skip this row.'), code='invalid_reference')
        return objects if self.multiple else objects[0] if objects else None

    def prepare_value(self, value):
        if isinstance(value, (list, tuple)):
            return [self.prepare_value(item) for item in value]
        if isinstance(value, models.Model):
            return reference_value(value)
        return value


def boolean_field(**kwargs):
    return forms.TypedChoiceField(coerce=lambda value: convert_bool(str(value)),
        choices=[('False', _('No')), ('True', _('Yes'))], **kwargs)


class CSVModelForm(forms.Form):
    csv_type = None

    def __init__(self, tournament, *args, references=None, team_choices=(), slots=0, extra_columns=(), instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tournament = tournament
        self.references = references or ImportReferences(tournament)
        self.instance = instance or self.csv_type.model()
        self.instance._csv_token = self.initial.get('_row_token')
        kind = self.csv_type
        for name in (*kind.field_names, *extra_columns):
            label = kind.field_label(name)
            options = {'label': label, 'initial': self.initial.get(name), 'required': name in kind.required_targets}
            if name in kind.references:
                target, multiple = kind.references[name]
                self.fields[name] = CSVReferenceField(target, self.references, multiple=multiple, **options)
            elif name == 'side' or name.startswith('side:'):
                self.fields[name] = forms.TypedChoiceField(choices=kind.side_choices, coerce=int, empty_value=None, **options)
            elif name.startswith('available:'):
                self.fields[name] = boolean_field(empty_value=False, **options)
            elif name in kind.extra_fields:
                self.fields[name] = kind.extra_fields[name](**options)
            else:
                field = kind.model._meta.get_field(name)
                if isinstance(field, models.BooleanField):
                    self.fields[name] = boolean_field(empty_value=field.get_default() if field.has_default() else False, **options)
                elif field.get_internal_type() == 'ArrayField':
                    self.fields[name] = forms.CharField(**options)
                else:
                    self.fields[name] = field.formfield()
                    self.fields[name].label = label
                    self.fields[name].required = options['required']
        for name in extra_columns:
            if name.startswith(('available:', 'side:')):
                token = self.references.match('round', name.split(':', 1)[1])
                self.fields['round_for_' + name] = CSVReferenceField('round', self.references, required=True,
                    label=_('Round for %(column)s') % {'column': name}, initial=self.initial.get('round_for_' + name, token))

    def clean(self):
        data = super().clean()
        if self.errors:
            return data
        kind = self.csv_type
        instance = self.instance
        for name in kind.model_field_names:
            if name not in data:
                continue
            value = data[name]
            field = kind.model._meta.get_field(name)
            if value in (None, '') and field.has_default():
                value = field.get_default()
            if field.get_internal_type() == 'ArrayField':
                value = value.split('//') if value else []
            setattr(instance, name, value)
        if 'tournament' in {field.name for field in kind.model._meta.fields}:
            instance.tournament = self.tournament
        kind.prepare_instance(instance, data)
        exclude = {'tournament', *kind.references, *kind.validation_exclusions}
        exclude.update(field.name for field in kind.model._meta.fields if field.is_relation and field.name not in kind.model_field_names)
        try:
            instance.full_clean(exclude=exclude)
            kind.validate_row(self, data)
        except ValidationError as error:
            if hasattr(error, 'message_dict'):
                for name, messages in error.message_dict.items():
                    self.add_error(name if name in self.fields else None, messages)
            else:
                self.add_error(None, error)
        return data
