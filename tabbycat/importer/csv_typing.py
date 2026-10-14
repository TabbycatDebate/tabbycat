"""CSV row and draft contracts: mapped fields stay dynamic, session values must be JSON-compatible."""

from __future__ import annotations

from collections.abc import Hashable
from typing import Any, Literal, NotRequired, TypeAlias, TypedDict

from django.db.models import Model
from django.utils.functional import Promise


DisplayLabel: TypeAlias = str | Promise
ReferenceToken: TypeAlias = int | str
CSVChoice: TypeAlias = tuple[ReferenceToken, DisplayLabel]
RowData: TypeAlias = dict[str, Any]
JSONValue: TypeAlias = str | int | float | bool | None | list['JSONValue'] | dict[str, 'JSONValue']
SerializedRowData: TypeAlias = dict[str, JSONValue]
RowStatus: TypeAlias = Literal['pending', 'created', 'imported', 'skipped', 'failed', 'blocked']
DuplicateKey: TypeAlias = tuple[Hashable, ...]
AdditionalObject: TypeAlias = tuple[str, Hashable]
ExecutionDependencies: TypeAlias = dict[str, Model | None]
TeamCandidate: TypeAlias = tuple[str, list[str], ReferenceToken | None]


class CSVParsedRow(TypedDict):
    line: int
    values: list[str]


class CSVSource(TypedDict):
    name: str
    headers: list[str]
    rows: list[CSVParsedRow]
    id: NotRequired[str]


class CSVRow(TypedDict):
    file: str
    file_index: int
    line: int
    kind: str
    values: dict[str, str]
    row_index: NotRequired[int]


class PreviewSummary(TypedDict):
    name: str
    related: DisplayLabel


class FormOptions(TypedDict, total=False):
    slots: int
    participant_fields: tuple[str, ...]
    extra_columns: tuple[str, ...]
    instance: Model | None


class CSVResultRow(TypedDict):
    file: str
    line: int
    kind: str
    status: RowStatus
    data: SerializedRowData
    errors: str
    display_name: NotRequired[str]
    object_id: NotRequired[int]
    team_id: NotRequired[int]


class CSVImportDraft(TypedDict):
    tournament: int
    user: int


class CSVUploadDraft(CSVImportDraft):
    started: Literal[False]
    files: list[CSVSource]
    format_options: SerializedRowData


class CSVExecutionDraft(CSVImportDraft):
    started: Literal[True]
    rows: list[CSVResultRow]
    team_choices: list[CSVChoice]
