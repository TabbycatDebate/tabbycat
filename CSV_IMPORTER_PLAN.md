# CSV Importer Implementation Plan

## First-phase implementation

The proof of concept implements the Django/session wizard for team CSVs, optional
numbered speaker name/email columns, and separate one-speaker-per-row CSVs.
Separate speakers can link to existing teams or teams in the same upload, using
team names and institution names/codes for matching. Teams are processed first;
speakers whose linked uploaded team is skipped or invalid are flagged in preview,
and a linked team that fails during execution blocks its speakers.
A speaker-only CSV can also create missing teams, following Anorak's institution
and team-name identity. The preview proposes each missing team explicitly;
speakers sharing that identity reuse one team. A new team and its first speaker
are saved in the same transaction.

This phase includes upload, format selection, mapping, reference resolution within
editable previews with Skip checkboxes, confirmation, and per-row results.
CSV types are registered handlers for mapping, preview validation, reference
normalization, duplicate checks, dependencies, and saving. Filenames suggest the
type case-insensitively, each file has its own mapping card, and mapped speaker
columns determine team speaker groups without asking for a maximum count. The
upload drop zone also opens the file picker. Python views supply page titles and
an emoji through the existing title mixin, and nested URLs use ``include``.
Institution creation, custom questions, shared API/command service extraction,
and additional object types remain later phases of the plan below.

## Design implementation

Use the Figma Make CSV Upload Wizard concept within Tabbycat's existing page
layout. The CSV wizard remains a link on the Simple Importer Index, with a
compact progress indicator. Navigation uses the existing import-screen components:
an outlined Previous Step button above the form and a full-width green Next Step
button below it. Info cards use the shared outlined component with an info icon.
There is no additional global navigation.

The Simple Importer Index places the CSV importer in a separate group at the top.
The upload screen offers header-only CSV templates for teams, teams with numbered
speakers and separate speakers, declared by the registered type handlers.

Mapping and preview use a vertical, scrollable file list showing filename, type,
row count, attention status and skipped count. Selecting a file shows its own
panel; Previous/Next file controls also work. All edits remain in the same Django
form submission, including files hidden by the JavaScript enhancement. Without
JavaScript every file remains visible. Type handlers supply summaries, object
counts and dependency metadata, so additional import types can reuse the layout.

Preview rows are compact summaries with expandable editors. Invalid rows open
automatically; filters show all, attention or skipped rows within the selected
file. Each summary keeps its actual source file and line separate from its linked
team or institution. Changes are validated on submission before confirmation.
Uploaded team rows that are skipped or invalid flag dependent speakers in preview;
execution still blocks a speaker if its previously valid team fails to import.

The current implementation supports teams and speakers only and accepts up to
20 files, retaining the 2 MiB/file and 1,000-row/session limits. File panels are
presentation groups, not server pagination: all fields are still submitted and
Django's field limit still applies. Before substantially larger imports, add
session-backed per-file/page saves and cross-file validation over saved rows.

Confirmation reports source-row totals separately from object counts, including
inline speakers and distinct teams proposed by speaker rows. Results retain
per-row errors, a progress bar, status counts and a file filter.

## Goal and first-release scope

Add an administrator-only **CSV Importer** page under **Import Data**. It will accept one or more CSV files with flexible layouts, let administrators identify the kind of objects in each file, map columns, resolve references such as institution names, edit and skip individual rows, preview validation results, and see per-row import progress and errors.

The first release will support:

- institutions;
- teams;
- speakers;
- adjudicators;
- files where one row contains a team and repeated groups of speaker fields;
- answers to existing registration questions/custom fields; and
- CSV files downloaded from Google Sheets or Google Forms response sheets.

Later phases will extend the same file list and type handlers to all supported files from the importer app and importtournament command, including venues, regions, categories, rounds, motions, feedback questions, conflicts, scores and constraints. Administrators must be able to upload a complete supported file set together.

It will create new records and flag possible matches. It will not update existing participants, create custom questions automatically, connect directly to Google Sheets, or synchronize a saved external source.

## User flow

Implement the importer with the same Django `SessionWizardView`, forms, and formset conventions as the existing simple importers. Use small JavaScript enhancements for drag-and-drop file selection and incremental import progress; do not build a separate Vue application for the first release.

The wizard has five stages:

1. **Upload files**
   - Select or drag-and-drop multiple CSV files.
   - Parse files immediately and display the detected encoding, delimiter, header row, filename, and row count.
   - Support UTF-8 with or without BOM and a selectable Windows-1252 fallback.
   - Detect the delimiter and header row, with manual overrides.
   - Handle quoted delimiters, multiline cells, empty cells, blank rows, and repeated header labels.

2. **Choose row types**
   - Assign each file to institutions, teams, speakers, adjudicators, or combined teams and speakers.
   - Allow a file to be excluded without removing other uploaded files.

3. **Map files**
   - Suggest mappings from normalized header names, but require administrator confirmation.
   - Permit ignored columns, fixed values, joined name columns, explicit source-to-choice conversions, and repeated speaker groups.
   - Map custom-answer columns only to existing questions that apply to the tournament and target object type.
   - Suggest institution and team matches for review in the next step.

4. **Preview, resolve references and review**
   - Render an editable Django formset for each file.
   - Show original row number, normalized values, resolved references, warnings, possible duplicates, field errors, and a **Skip** checkbox.
   - Provide a **Skip all invalid rows** action and summary counts for rows to import, skip, or block.
   - Require all non-skipped rows to have mappings and resolvable dependencies before confirmation.

5. **Import and results**
   - Submit short sequential batches through CSRF-protected administrator endpoints.
   - Update each displayed row to pending, imported, skipped, failed, or dependency-blocked.
   - Show created objects and field-level errors and provide a downloadable error CSV.

Administrators can move backward without losing their uploaded data, mappings, edits, or skip choices. Changing source settings, mappings, references, or preview values invalidates the previous confirmation and re-runs preview validation.

## Wizard state and session storage

Use the user's Django session for the first release, matching the existing wizard approach. Give each wizard instance a random ID so multiple browser tabs do not overwrite each other.

Store only JSON-compatible data in a wizard-specific session namespace:

- filenames, parsing settings, headers, and parsed cell values;
- row-type and column mappings;
- reference-resolution selections;
- edited normalized values and skip flags;
- validation errors and warnings; and
- import statuses and created object IDs.

Do not retain raw uploaded files after parsing and do not add staging models, migrations, or a cleanup command. Explicitly discarding or completing the wizard removes its draft; otherwise the draft expires or may be evicted with the configured cache-backed session.

Start with limits of 20 files, 2 MiB per file, and 1,000 total source rows. Make these configurable as broader import types and per-file/page saves are added. Reject an upload before writing it to session if it would exceed these limits.

Session state cannot commit atomically with participant creation. Each source row will still be imported in its own database transaction, including all objects and answers created from a combined registration row. After a network interruption or uncertain response, stop the batch and do not retry it automatically. Identify the possibly completed batch and instruct the administrator to inspect those rows before starting it again. Durable exactly-once resumption is deferred unless staging records are introduced later.

## Reference resolution

CSV relationships use names and codes; administrators are not expected to supply database IDs or API hyperlinks.

Resolve relationships in the editable row preview, without separate institution or team matching steps. For institutions:

1. Trim surrounding whitespace.
2. Try the existing exact lookup against `Institution.code` and `Institution.name`.
3. If there is no exact match, offer case-insensitive matches as suggestions.
4. Require an explicit selection for unmatched or ambiguous values.
5. Keep each selection with its preview row so it can be edited or skipped.

Resolution choices include existing shared institutions and institution rows staged in the current wizard. Never silently create an institution because an unmatched name may be a spelling error.

Team references use the selected institution plus the team's reference/name to avoid collisions. They can resolve to an existing team in the current tournament or to a staged team row. If no team matches, propose creating one using the editable team name, institution and prefix setting. Reuse that team for subsequent speaker rows with the same institution and name; ambiguous matches require an explicit preview choice. Adjudicator institution conflicts and other supported institution references use the same resolution map.

Staged relationships are stored as source-file and source-row references. During execution, import institutions first, then teams, then dependent speakers and adjudicators. Replace staged references with the model instances or IDs returned by prior successful rows. If a referenced row is skipped or fails, mark its dependants as blocked until the administrator selects another reference or skips them.

Flag likely participant duplicates using email where present and name within the relevant team or institution. Present the candidates and require the administrator to skip the source row or explicitly create a distinct record where model constraints allow it. Do not overwrite or merge existing participants in this release.

## Preview formsets and skipping

Use Django formsets rather than keeping the whole workflow in Vue or creating records with client-side API calls.

Every preview form contains a stable source-row identifier and a **Skip** checkbox. A custom formset clean method must detect the skip flag before enforcing participant-field validation, while still validating that the row identifier belongs to the current wizard. Checking **Skip** preserves the row's values but removes its participant errors from the blocking error count. Unchecking it validates the row again.

A combined team-and-speakers source row is one import unit: skipping it skips the team, all speaker groups, and their answers. Completely empty repeated speaker groups are ignored; partially populated groups receive errors against their fields. Skipping a dependency does not silently skip its dependants—the dependent rows are shown as blocked so the administrator can make an explicit decision.

Rows become read-only once imported. A skip choice is not an undo operation and cannot delete an object already created.

## Shared validation and creation services

Do not make the wizard or `importtournament` manufacture API URLs or invoke the application over HTTP. Instead, extract request-independent validation and creation logic from the participant API serializers and their helpers into shared domain services.

The three entry points have different input adapters but converge after relationships have been resolved:

| Entry point | Relationship input | Shared layer receives |
| --- | --- | --- |
| API serializers | Hyperlinks resolved by DRF fields | Validated values and model instances |
| CSV wizard | Names/codes, explicit selections, and staged-row references | Normalized values and model instances |
| `importtournament` | Existing importer lookup rules | Normalized values and model instances |

`TournamentHyperlinkedRelatedField` already resolves a supplied URL locally through Django routing and a tournament-filtered queryset; it does not fetch the URL. Keep this API behavior in the serializer layer. The CSV wizard resolves names and staged references itself and passes resulting model instances directly into the shared services.

The shared services will cover institution/tournament-institution setup, team creation, speakers, adjudicators, applicable custom answers, generated code names/private identifiers, and current participant defaults. They must enforce tournament ownership and model compatibility themselves rather than relying only on DRF relationship fields.

API serializers remain responsible for HTTP representation, hyperlink fields, request permissions, public-field filtering, and translating service errors to DRF errors. The wizard remains responsible for CSV parsing, mapping, duplicate decisions, staged dependencies, skip behavior, and row-level presentation. The management command retains its directory formats, command-line policy, logging, and error presentation.

Adapt the participant portions of `importtournament`—institutions, teams, speakers, adjudicators, and custom answers—to call the same shared services. Preserve its existing file formats, tournament creation/setup, import order, `--keep-existing`, `--relaxed`, and duplicate semantics. Leave rounds, venues, motions, feedback questions, and other configuration imports on their current paths unless a participant extraction requires a narrowly related change.

Preview uses side-effect-free service validation after resolving existing objects. Staged dependencies that do not exist yet are validated structurally during preview and validated again with the actual instances immediately before creation.

## Custom questions

Expose only existing questions for the tournament and applicable target type. Include person-level questions for speaker, adjudicator, or coach-derived participants where the current data model supports them. Institution answers attach to the tournament's `TournamentInstitution`, not the globally shared `Institution`.

Provide a link to the existing question-management page and a way to refresh the available mapping choices without losing other mappings. Do not infer or create a question from an unknown CSV column.

Normalize and validate booleans, integers, floats, choice values, multiple choices, bounds, and ISO or administrator-selected date formats. Allow the administrator to configure the separator for multiple-choice cells. Correct the shared answer validator so multiple-choice answers are validated item-by-item rather than also being subjected to the scalar single-choice check. Preserve the API's current administrator behavior for omitted required questions, but show omissions as preview warnings.

## Import execution and logging

Import rows in dependency order and in short batches. Each source row runs inside `transaction.atomic()`. For a combined registration, the team, speakers, custom answers, and related generated values all succeed or roll back together.

Revalidate each row immediately before saving. Disable repeated submission while a request is active, and refuse to run rows whose session status is already imported. Return structured row statuses and field errors and update the session after each successful batch.

Use the existing action-log conventions to record the completed import, including counts by object type and skipped/failed rows. Do not log private source data or full CSV contents.

## Google Sheets

For the first release, document the workflow: download the relevant Google Sheets or Google Forms response tab as CSV, upload it, map it, preview it, and import it.

Keep parsing separate from normalized mapping data so a future source adapter can populate the same wizard state from a Google Sheets snapshot. Direct integration would require Google authorization, file and tab selection, deployment credentials, and permission review. Saved sources or repeated refreshes would additionally require record-matching and update policies, so both are deferred.

## Testing and acceptance criteria

- Parse supported encodings and delimiters, quoted multiline cells, repeated headers, empty rows, multiple files, limits, and combined registrations.
- Preserve wizard state across steps and isolate concurrent wizard IDs in the same session.
- Resolve exact institution names and codes, present case-insensitive suggestions, handle ambiguity, and resolve cross-file staged dependencies.
- Verify institution-scoped team resolution, adjudicator institutions and conflicts, skipped parents, and blocked dependants.
- Verify preview never writes participant data.
- Test row edits, the Skip checkbox, bulk skipping, unskipping and revalidation, and combined-row skip semantics.
- Test custom-answer types, choices, multiple selections, numeric bounds, dates, target compatibility, and tournament isolation.
- Verify each source row is atomic and that processing stops after an uncertain response without automatic retry.
- Verify API, wizard, and `importtournament` produce equivalent participant records and validation results from equivalent normalized input, apart from their documented duplicate/error policies.
- Run compatibility coverage for existing importer formats and command flags.
- Manually import a representative Google Forms CSV containing institutions, teams, speakers, adjudicators, and custom answers; correct mappings and errors; skip selected rows; and inspect the resulting records.
- Verify accessible keyboard operation, readable per-row errors and progress, translatable interface strings, and continued operation of all existing simple import wizards.
