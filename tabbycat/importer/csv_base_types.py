"""Hooks implemented by every registered CSV type."""

import re


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
    reference_fields = ()
    deferred_fields = ()

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

    def duplicate_keys(self, data):
        return (self.duplicate_key(data),)

    def restore_preview(self, data, prefix, initial):
        pass

    def resolve_preview(self, form, forms):
        pass

    def preview_summary(self, form):
        return {'name': form[self.name_field].value() or '', 'related': ''}

    def object_counts(self, form):
        return {self.key: 1}

    def additional_objects(self, form):
        return ()

    def preview_dependencies(self, data):
        return reference_dependencies(data, self.reference_fields)

    def dependencies(self, tournament, data, rows, references=None):
        return {}

    def save(self, form, user, **dependencies):
        raise NotImplementedError


def reference_dependencies(data, fields):
    dependencies = set()
    for field in fields:
        values = data.get(field) or []
        if not isinstance(values, (list, tuple)):
            values = [values]
        for value in values:
            token = getattr(value, '_csv_token', value)
            if isinstance(token, str) and token.startswith('row:'):
                dependencies.add(int(token.split(':')[1]))
    return tuple(sorted(dependencies))
