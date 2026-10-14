"""Hooks implemented by every registered CSV type."""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import Generic, TYPE_CHECKING, TypeVar

from django.db.models import Model
from django.forms import BaseForm

from .csv_typing import AdditionalObject, CSVResultRow, CSVRow, CSVSource, DisplayLabel, DuplicateKey, ExecutionDependencies, FormOptions, PreviewSummary, RowData, SerializedRowData


if TYPE_CHECKING:
    from django.contrib.auth.base_user import AbstractBaseUser
    from django.http import QueryDict

    from tournaments.models import Tournament

    from .csv_pipeline import CSVImportContext
    from .references import ImportReferences


FormT = TypeVar('FormT', bound=BaseForm)
SavedT = TypeVar('SavedT', bound=Model)


class DependencyPendingError(Exception):
    pass


class DependencyBlockedError(Exception):
    pass


def normalized_header(header: str) -> str:
    return re.sub(r'\W+', '_', header.strip().casefold()).strip('_')


class CSVObjectType(Generic[FormT, SavedT]):
    form_class: Callable[..., FormT]
    key: str = ''
    label: DisplayLabel = ''
    filename_words: tuple[str, ...] = ()
    templates: tuple[tuple[str, DisplayLabel, tuple[str, ...]], ...] = ()
    targets = ()
    aliases: dict[str, str] = {}
    required_targets = ()
    priority: int = 0
    identity_fields = ()
    name_field = 'name'
    reference_fields = ()
    deferred_fields = ()
    count_label: DisplayLabel | None = None

    def review_label(self, count: int) -> DisplayLabel:
        return self.count_label % {'count': count} if self.count_label is not None else self.label

    def mapping_choices(self, source: CSVSource) -> list[tuple[str, DisplayLabel]]:
        return list(self.targets)

    def guess_column(self, header: str) -> str:
        name = normalized_header(header)
        return self.aliases.get(name, name)

    def form_options(self, values: Iterable[str]) -> FormOptions:
        return {}

    def preview_field_count(self, targets: Iterable[str]) -> int:
        return len(self.targets) + 1

    def initial(self, row: CSVRow, context: CSVImportContext) -> RowData:
        return row['values'].copy()

    def serialize(self, data: RowData) -> SerializedRowData:
        return data.copy()

    def duplicate_key(self, data: RowData) -> DuplicateKey:
        return (self.key, *(data[field] for field in self.identity_fields))

    def duplicate_keys(self, data: RowData) -> tuple[DuplicateKey, ...]:
        return (self.duplicate_key(data),)

    def restore_preview(self, data: QueryDict, prefix: str, initial: RowData) -> None:
        pass

    def resolve_preview(self, form: FormT, forms: Sequence[BaseForm]) -> None:
        pass

    def preview_summary(self, form: FormT) -> PreviewSummary:
        return {'name': form[self.name_field].value() or '', 'related': ''}

    def object_counts(self, form: FormT) -> dict[str, int]:
        return {self.key: 1}

    def additional_objects(self, form: FormT) -> Iterable[AdditionalObject]:
        return ()

    def preview_dependencies(self, data: Mapping[str, object]) -> tuple[int, ...]:
        return reference_dependencies(data, self.reference_fields)

    def dependencies(self, tournament: Tournament, data: SerializedRowData, rows: Sequence[CSVResultRow], references: ImportReferences | None = None) -> ExecutionDependencies:
        return {}

    def finish_references(self, form: FormT, obj: SavedT) -> None:
        """Complete references deferred by a type after primary object creation."""
        raise NotImplementedError

    def save(self, form: FormT, user: AbstractBaseUser, **dependencies: Model | None) -> SavedT:
        raise NotImplementedError


def reference_dependencies(data: Mapping[str, object], fields: Iterable[str]) -> tuple[int, ...]:
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
