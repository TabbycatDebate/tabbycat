"""Preserve wizard data when files or their interpretations change."""

import re

from django.http import QueryDict


PREVIEW_FIELD = re.compile(r'^preview-(\d+)-(.+)$')


def row_positions(files):
    return [(source['id'], row['line']) for source in files for row in source['rows']]


def remap_step_data(step, data, old_files, new_files):
    if data is None:
        return None
    result = QueryDict(mutable=True)
    file_indices = {source['id']: index for index, source in enumerate(new_files)}
    old_rows = row_positions(old_files)
    new_rows = {identity: index for index, identity in enumerate(row_positions(new_files))}
    for name, values in data.lists():
        if step == 'types' and (match := re.fullmatch(r'types-file_(\d+)', name)):
            old_index = int(match[1])
            if old_index >= len(old_files):
                continue
            index = file_indices.get(old_files[old_index]['id'])
            if index is not None:
                result.setlist(f'types-file_{index}', values)
        elif step == 'mapping' and (match := re.fullmatch(r'mapping-column_(\d+)_(\d+)', name)):
            old_index, column = int(match[1]), match[2]
            if old_index >= len(old_files):
                continue
            index = file_indices.get(old_files[int(old_index)]['id'])
            if index is not None:
                result.setlist(f'mapping-column_{index}_{column}', values)
        elif step == 'preview' and (match := PREVIEW_FIELD.match(name)):
            old_index, field = int(match[1]), match[2]
            if old_index >= len(old_rows):
                continue
            index = new_rows.get(old_rows[old_index])
            if index is None:
                continue
            if field == 'team' and values and values[0].startswith('row:'):
                parent = values[0].split(':')[1]
                target = new_rows.get(old_rows[int(parent)]) if parent.isdigit() and int(parent) < len(old_rows) else None
                # Keep an invalid choice when a referenced file was removed.
                # A blank value would be filled from CSV defaults as a new team.
                values = [f'row:{target}' if target is not None else 'removed']
            result.setlist(f'preview-{index}-{field}', values)
    if step == 'preview':
        result['preview-TOTAL_FORMS'] = len(new_rows)
        result['preview-INITIAL_FORMS'] = len(new_rows)
    return result


def update_wizard_files(storage, old_files, new_files):
    for step in ('types', 'mapping', 'preview'):
        storage.set_step_data(step, remap_step_data(step, storage.get_step_data(step), old_files, new_files))
    validated = storage.extra_data.get('validated_steps', {})
    for step in ('types', 'mapping'):
        if step in validated:
            data = QueryDict(mutable=True)
            for name, values in validated[step].items():
                data.setlist(name, values)
            validated[step] = dict(remap_step_data(step, data, old_files, new_files).lists())
    storage.extra_data = {**storage.extra_data, 'validated_steps': validated}
    storage.set_step_data('confirm', None)
    storage.current_step = 'types'


def invalidate_file_previews(storage, files, changed_indices, *, reset_mapping=False):
    if reset_mapping and (mapping := storage.get_step_data('mapping')) is not None:
        for name in list(mapping):
            if any(name.startswith(f'mapping-column_{index}_') for index in changed_indices):
                del mapping[name]
        storage.set_step_data('mapping', mapping)
    if (preview := storage.get_step_data('preview')) is not None:
        offset = 0
        changed_rows = set()
        for index, source in enumerate(files):
            if index in changed_indices:
                changed_rows.update(range(offset, offset + len(source['rows'])))
            offset += len(source['rows'])
        for name in list(preview):
            if (match := PREVIEW_FIELD.match(name)) and int(match[1]) in changed_rows:
                del preview[name]
        storage.set_step_data('preview', preview)
    storage.set_step_data('confirm', None)
