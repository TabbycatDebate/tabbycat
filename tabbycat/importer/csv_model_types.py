"""Model-backed CSV types shared across Anorak and Boots formats."""

from dataclasses import dataclass
from datetime import date, datetime
from functools import partial

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldDoesNotExist, ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _, ngettext_lazy

from actionlog.models import ActionLogEntry
from adjallocation.models import AdjudicatorAdjudicatorConflict, AdjudicatorInstitutionConflict, AdjudicatorTeamConflict
from adjfeedback.models import AdjudicatorBaseScoreHistory, AdjudicatorFeedback
from availability.models import RoundAvailability
from checkins.models import PersonIdentifier, VenueIdentifier
from draw.types import DebateSide
from motions.models import RoundMotion
from participants.utils import populate_code_names
from privateurls.utils import populate_url_keys

from .csv_base_types import CSVObjectType, reference_dependencies
from .csv_model_forms import boolean_field, CSVModelForm
from .csv_models import CSV_MODELS, IMPLICIT_REFERENCE_TYPES
from .csv_values import convert_bool
from .importers.anorak import AnorakTournamentDataImporter
from .references import reference_value


@dataclass(frozen=True)
class CSVReference:
    """A named reference, optionally accepting a delimited list of objects."""

    kind: str
    multiple: bool = False
    separator: str = ','


def convert_boolean(value):
    return convert_bool(str(value)) if value != '' else False


def reference_objects(data, name, reference):
    value = data.get(name)
    return (value or []) if reference.multiple else [value]


def validate_existing_identity(form, data):
    kind = form.csv_type
    for existing in form.references.objects(kind.key).values():
        if existing.pk == form.instance.pk:
            continue
        matches = all(
            reference_value(getattr(existing, name)) == reference_value(data.get(name)) if name in kind.references else
            getattr(existing, name) == data.get(name) for name in kind.identity_fields)
        if matches:
            form.add_error(kind.name_field, _('A record with this identity already exists. Skip or correct this row.'))
            break


def validate_distinct_adjudicators(form, first, second, field):
    if reference_value(first) == reference_value(second):
        form.add_error(field, _('An adjudicator cannot conflict with themselves.'))


def save_availability(form, obj):
    for name, value in form.cleaned_data.items():
        if name.startswith('available:') and value:
            RoundAvailability.objects.get_or_create(content_type=ContentType.objects.get_for_model(obj),
                object_id=obj.pk, round=form.cleaned_data['round_for_' + name])


class ModelCSVType(CSVObjectType):
    filename = None
    fields = None
    references = {}
    extra_fields = {}
    extra_labels = {}
    defaults = {}
    converters = {}
    dynamic_converters = {}
    dynamic_fields = {}
    action = None
    name_field = None
    required_targets = None
    validation_exclusions = ()

    def __init__(self):
        self.model = CSV_MODELS[self.key]
        self.reference_fields = tuple(self.references)

        excluded = {
            'id', 'tournament', 'for_content_type', 'subject_content_type', 'subject_id',
            'person_ptr', 'question_ptr', 'url_key', 'code_name',
        }
        self.model_field_names = tuple(self.fields or (
            field.name for field in self.model._meta.fields if field.editable and field.name not in excluded))
        self.field_names = tuple(dict.fromkeys((*self.model_field_names, *self.references, *self.extra_fields)))

        if self.name_field is None:
            self.name_field = next((name for name in ('name', 'reference') if name in self.field_names), self.field_names[0])
        self.identity_fields = self.identity_fields or (self.name_field,)
        if self.required_targets is None:
            self.required_targets = tuple(
                name for name in self.model_field_names if name not in self.defaults and
                not self.model._meta.get_field(name).blank and not self.model._meta.get_field(name).has_default())

        self.templates = ((self.filename, self.label, self.field_names),)
        self.filename_words = (self.filename,)
        self.targets = [(name, self.field_label(name)) for name in self.field_names]
        self.form_class = type(f'{type(self).__name__}Form', (CSVModelForm,), {'csv_type': self})

    def field_label(self, name):
        if name in self.extra_labels:
            return self.extra_labels[name]
        try:
            return self.model._meta.get_field(name).verbose_name
        except FieldDoesNotExist:
            return name.replace('_', ' ')

    def guess_column(self, header):
        prefix, separator, suffix = header.partition(':')
        if separator and prefix.casefold() in self.dynamic_converters:
            return prefix.casefold() + ':' + suffix
        return super().guess_column(header)

    def mapping_choices(self, source):
        dynamic = [self.guess_column(header) for header in source['headers']]
        return [*self.targets, *((name, self.field_label(name)) for name in dynamic
            if ':' in name and name.partition(':')[0] in self.dynamic_converters)]

    def form_options(self, values):
        return {'extra_columns': tuple(name for name in values if ':' in name and name.partition(':')[0] in self.dynamic_converters)}

    def preview_field_count(self, targets):
        return len(self.field_names) + 2 * len(self.form_options(targets)['extra_columns']) + 1

    def initial(self, row, context):
        values = {**self.defaults, **row['values']}
        for name, convert in self.converters.items():
            if name in values and values[name] != '':
                try:
                    values[name] = convert(values[name])
                except ValueError:
                    pass

        for name in self.field_names:
            if name in self.references:
                reference = self.references[name]
                raw = values.get(name, '')
                if reference.multiple:
                    values[name] = [context.references.match(reference.kind, item.strip())
                        for item in raw.split(reference.separator) if item.strip()]
                else:
                    values[name] = context.references.match(reference.kind, raw, create=reference.kind in IMPLICIT_REFERENCE_TYPES)
            elif name in self.model_field_names:
                field = self.model._meta.get_field(name)
                if field.has_default() and values.get(name, '') == '':
                    values[name] = field.get_default()

        for name in self.form_options(values)['extra_columns']:
            prefix, suffix = name.split(':', 1)
            values['round_for_' + name] = context.references.match('round', suffix)
            try:
                values[name] = self.dynamic_converters[prefix](values[name])
            except ValueError:
                pass
        return values

    def prepare_instance(self, instance, data):
        pass

    def validate_row(self, form, data):
        pass

    def create_object(self, form):
        form.instance.save()
        return form.instance

    def after_save(self, form, obj):
        pass

    def serialize(self, data):
        result = {}
        for name, value in data.items():
            if isinstance(value, (list, tuple)):
                value = [reference_value(item) for item in value]
            elif hasattr(value, '_meta'):
                value = reference_value(value)
            elif isinstance(value, (date, datetime)):
                value = value.isoformat()
            result[name] = value
        return result

    def additional_objects(self, form):
        objects = set()
        for name, reference in self.references.items():
            values = reference_objects(form.cleaned_data, name, reference)
            for obj in values or []:
                token = getattr(obj, '_csv_token', '') or ''
                if token.startswith('new:'):
                    objects.add((reference.kind, token))
        return objects

    def preview_dependencies(self, data):
        fields = (*self.reference_fields, *(name for name in data if name.startswith('round_for_')))
        return reference_dependencies(data, fields)

    def preview_summary(self, form):
        value = form[self.name_field].value()
        field = form.fields[self.name_field]
        if self.name_field in self.references:
            value = {str(key): label for key, label in field.widget.choices}.get(str(value), value)
        related = []
        for name in self.references:
            if name == self.name_field:
                continue
            values = form[name].value() or []
            if not isinstance(values, (list, tuple)):
                values = [values]
            choices = {str(key): label for key, label in form.fields[name].widget.choices}
            related.extend(str(choices.get(str(item), item)) for item in values)
        return {'name': value or '', 'related': ' · '.join(related) or str(self.label)}

    def duplicate_key(self, data):
        return (self.key, *(reference_value(data[name]) if hasattr(data.get(name), '_meta') else data.get(name)
            for name in self.identity_fields))

    @transaction.atomic
    def save(self, form, user, **dependencies):
        data = form.cleaned_data
        for name, reference in self.references.items():
            for obj in reference_objects(data, name, reference):
                if obj is None or not (getattr(obj, '_csv_token', None) or '').startswith('new:'):
                    continue
                attributes = {'name': obj.name}
                if hasattr(obj, 'tournament_id'):
                    attributes['tournament'] = form.tournament
                actual, unused = CSV_MODELS[reference.kind].objects.get_or_create(**attributes)
                if reference.multiple:
                    data[name] = [actual if item is obj else item for item in data[name]]
                else:
                    data[name] = actual
                    if name in self.model_field_names:
                        setattr(form.instance, name, actual)

        obj = self.create_object(form)
        self.after_save(form, obj)
        if self.action:
            ActionLogEntry.objects.log(type=self.action, tournament=form.tournament, content_object=obj, user=user)
        return obj


class AvailabilityCSVType(ModelCSVType):
    dynamic_converters = {'available': convert_boolean}
    dynamic_fields = {'available': partial(boolean_field, empty_value=False)}

    def field_label(self, name):
        if name.startswith('available:'):
            return _('Available in %(round)s') % {'round': name.split(':', 1)[1]}
        return super().field_label(name)

    def after_save(self, form, obj):
        save_availability(form, obj)


class ConflictCSVType(ModelCSVType):
    def create_object(self, form):
        obj, unused = self.model.objects.get_or_create(**{name: form.cleaned_data[name] for name in self.model_field_names})
        return obj


class VenueConstraintCSVType(ModelCSVType):
    fields = ('category', 'priority')
    subject_field = None

    def prepare_instance(self, instance, data):
        subject = data.get(self.subject_field)
        if subject:
            instance.subject_content_type = ContentType.objects.get_for_model(subject)
            instance.subject_id = subject.pk or 1

    def create_object(self, form):
        form.instance.subject_id = form.cleaned_data[self.subject_field].pk
        return super().create_object(form)


class RegionCSVType(ModelCSVType):
    key = 'region'
    label = _('Regions')
    count_label = ngettext_lazy('Region', 'Regions', 'count')
    filename = 'regions'
    priority = -50


class InstitutionCSVType(ModelCSVType):
    key = 'institution'
    label = _('Institutions')
    count_label = ngettext_lazy('Institution', 'Institutions', 'count')
    filename = 'institutions'
    priority = -40
    references = {
        'region': CSVReference('region'),
    }
    identity_fields = ('name', 'code')
    action = ActionLogEntry.ActionType.INSTITUTION_CREATE


class VenueCategoryCSVType(ModelCSVType):
    key = 'venue_category'
    label = _('Room categories')
    count_label = ngettext_lazy('Room category', 'Room categories', 'count')
    filename = 'venue_categories'
    priority = -30
    converters = {
        'display_in_venue_name': AnorakTournamentDataImporter.lookup_venue_category_display,
    }
    action = ActionLogEntry.ActionType.VENUE_CATEGORY_CREATE

    def validate_row(self, form, data):
        validate_existing_identity(form, data)


class BreakCategoryCSVType(ModelCSVType):
    key = 'break_category'
    label = _('Break categories')
    count_label = ngettext_lazy('Break category', 'Break categories', 'count')
    filename = 'break_categories'
    priority = -30
    converters = {'is_general': convert_boolean}
    action = ActionLogEntry.ActionType.BREAK_CATEGORIES_EDIT


class SpeakerCategoryCSVType(ModelCSVType):
    key = 'speaker_category'
    label = _('Speaker categories')
    count_label = ngettext_lazy('Speaker category', 'Speaker categories', 'count')
    filename = 'speaker_categories'
    priority = -30
    converters = {'public': convert_boolean}
    action = ActionLogEntry.ActionType.SPEAKER_CATEGORIES_EDIT


class RoundCSVType(ModelCSVType):
    key = 'round'
    label = _('Rounds')
    count_label = ngettext_lazy('Round', 'Rounds', 'count')
    filename = 'rounds'
    priority = -20
    references = {
        'break_category': CSVReference('break_category'),
    }
    defaults = {'seq': None, 'schedule_group': None}
    identity_fields = ('seq',)
    converters = {
        'stage': AnorakTournamentDataImporter.lookup_round_stage,
        'draw_type': AnorakTournamentDataImporter.lookup_draw_type,
        'silent': convert_boolean,
        'completed': convert_boolean,
    }
    action = ActionLogEntry.ActionType.ROUND_CREATE

    def initial(self, row, context):
        values = row['values'].copy()
        values['seq'] = values.get('seq') or row.get('row_index', row['line'] - 2) + 1
        values['schedule_group'] = values.get('schedule_group') or values['seq']
        return super().initial({**row, 'values': values}, context)


class VenueCSVType(AvailabilityCSVType):
    key = 'venue'
    label = _('Rooms')
    count_label = ngettext_lazy('Room', 'Rooms', 'count')
    filename = 'venues'
    priority = 10
    references = {
        'category': CSVReference('venue_category'),
    }
    action = ActionLogEntry.ActionType.VENUE_CREATE
    extra_labels = {'category': _('Room category')}

    def validate_row(self, form, data):
        validate_existing_identity(form, data)

    def after_save(self, form, obj):
        super().after_save(form, obj)
        VenueIdentifier.objects.create(venue=obj)
        if form.cleaned_data.get('category'):
            form.cleaned_data['category'].venues.add(obj)


class AdjudicatorCSVType(AvailabilityCSVType):
    key = 'adjudicator'
    label = _('Adjudicators')
    count_label = ngettext_lazy('Adjudicator', 'Adjudicators', 'count')
    filename = 'adjudicators'
    priority = 10
    references = {
        'institution': CSVReference('institution'),
        'institution_conflicts': CSVReference('institution', multiple=True),
        'team_conflicts': CSVReference('team', multiple=True),
        'adj_conflicts': CSVReference('adjudicator', multiple=True),
    }
    deferred_fields = ('adj_conflicts',)
    converters = {
        'gender': AnorakTournamentDataImporter.lookup_gender,
        'anonymous': convert_boolean,
        'trainee': convert_boolean,
        'breaking': convert_boolean,
        'independent': convert_boolean,
        'adj_core': convert_boolean,
    }
    aliases = {
        'adjudicator': 'name',
        'adj_conflicts': 'adj_conflicts',
        'adjudicator_conflicts': 'adj_conflicts',
        'category': '',
    }
    identity_fields = ('institution', 'name')
    action = ActionLogEntry.ActionType.ADJUDICATOR_CREATE
    extra_labels = {
        'team_conflicts': _('Team conflicts'),
        'institution_conflicts': _('Institution conflicts'),
        'adj_conflicts': _('Adjudicator conflicts'),
    }

    def validate_row(self, form, data):
        validate_existing_identity(form, data)
        if form.instance._csv_token:
            for other in data.get('adj_conflicts', []):
                validate_distinct_adjudicators(form, form.instance, other, 'adj_conflicts')

    def after_save(self, form, obj):
        super().after_save(form, obj)
        data = form.cleaned_data
        PersonIdentifier.objects.create(person=obj)
        populate_url_keys([obj])
        populate_code_names([obj])
        if obj.institution_id:
            AdjudicatorInstitutionConflict.objects.get_or_create(adjudicator=obj, institution=obj.institution)
        AdjudicatorBaseScoreHistory.objects.create(adjudicator=obj, score=obj.base_score, round=None)
        for institution in data.get('institution_conflicts', []):
            AdjudicatorInstitutionConflict.objects.get_or_create(adjudicator=obj, institution=institution)
        for team in data.get('team_conflicts', []):
            AdjudicatorTeamConflict.objects.get_or_create(adjudicator=obj, team=team)

    @transaction.atomic
    def finish_references(self, form, obj):
        for other in form.cleaned_data.get('adj_conflicts', []):
            if obj.pk == other.pk:
                raise ValidationError(_('An adjudicator cannot conflict with themselves.'))
            AdjudicatorAdjudicatorConflict.objects.get_or_create(adjudicator1=obj, adjudicator2=other)


class MotionCSVType(ModelCSVType):
    key = 'motion'
    label = _('Motions')
    count_label = ngettext_lazy('Motion', 'Motions', 'count')
    filename = 'motions'
    priority = 20
    references = {
        'rounds': CSVReference('round', multiple=True, separator=';'),
    }
    extra_fields = {'seq': forms.CharField}
    action = ActionLogEntry.ActionType.MOTION_EDIT
    extra_labels = {'rounds': _('Rounds'), 'seq': _('Motion sequences')}

    def validate_row(self, form, data):
        validate_existing_identity(form, data)
        sequences = str(data.get('seq') or '').split(';') if data.get('seq') else []
        if sequences and len(sequences) != len(data.get('rounds', [])):
            raise ValidationError(_('Provide one motion sequence for each linked round.'))
        if any(not value.isdigit() or int(value) < 1 for value in sequences):
            raise ValidationError(_('Motion sequences must be positive integers.'))

    def after_save(self, form, obj):
        data = form.cleaned_data
        sequences = str(data.get('seq') or '').split(';')
        for index, round in enumerate(data.get('rounds', [])):
            RoundMotion.objects.create(motion=obj, round=round, seq=int(sequences[index]) if data.get('seq') else 1)


class ScoreCSVType(ModelCSVType):
    key = 'score'
    label = _('Adjudicator scores')
    count_label = ngettext_lazy('Adjudicator score', 'Adjudicator scores', 'count')
    filename = 'scores'
    priority = 20
    references = {
        'adjudicator': CSVReference('adjudicator'),
        'round': CSVReference('round'),
    }
    identity_fields = ('adjudicator', 'round')
    action = ActionLogEntry.ActionType.TEST_SCORE_EDIT

    def after_save(self, form, obj):
        adjudicator = form.cleaned_data['adjudicator']
        adjudicator.base_score = obj.score
        adjudicator.save(update_fields=['base_score'])


class TeamConflictCSVType(ConflictCSVType):
    key = 'team_conflict'
    label = _('Adjudicator–team conflicts')
    count_label = ngettext_lazy('Adjudicator–team conflict', 'Adjudicator–team conflicts', 'count')
    filename = 'team_conflicts'
    priority = 20
    references = {
        'adjudicator': CSVReference('adjudicator'),
        'team': CSVReference('team'),
    }
    identity_fields = ('adjudicator', 'team')
    action = ActionLogEntry.ActionType.CONFLICTS_ADJ_TEAM_EDIT


class InstitutionConflictCSVType(ConflictCSVType):
    key = 'institution_conflict'
    label = _('Adjudicator–institution conflicts')
    count_label = ngettext_lazy('Adjudicator–institution conflict', 'Adjudicator–institution conflicts', 'count')
    filename = 'institution_conflicts'
    priority = 20
    references = {
        'adjudicator': CSVReference('adjudicator'),
        'institution': CSVReference('institution'),
    }
    identity_fields = ('adjudicator', 'institution')
    action = ActionLogEntry.ActionType.CONFLICTS_ADJ_INST_EDIT


class AdjudicatorConflictCSVType(ConflictCSVType):
    key = 'adjudicator_conflict'
    label = _('Adjudicator conflicts')
    count_label = ngettext_lazy('Adjudicator conflict', 'Adjudicator conflicts', 'count')
    filename = 'adjudicator_conflicts'
    priority = 20
    references = {
        'adjudicator1': CSVReference('adjudicator'),
        'adjudicator2': CSVReference('adjudicator'),
    }
    identity_fields = ('adjudicator1', 'adjudicator2')
    action = ActionLogEntry.ActionType.CONFLICTS_ADJ_ADJ_EDIT

    def validate_row(self, form, data):
        validate_distinct_adjudicators(form, data.get('adjudicator1'), data.get('adjudicator2'), 'adjudicator2')


class TeamInstitutionConflictCSVType(ConflictCSVType):
    key = 'team_institution_conflict'
    label = _('Team–institution conflicts')
    count_label = ngettext_lazy('Team–institution conflict', 'Team–institution conflicts', 'count')
    filename = 'team_institution_conflicts'
    priority = 20
    references = {
        'team': CSVReference('team'),
        'institution': CSVReference('institution'),
    }
    identity_fields = ('team', 'institution')
    action = ActionLogEntry.ActionType.CONFLICTS_TEAM_INST_EDIT


class SideCSVType(ModelCSVType):
    key = 'side'
    label = _('Side allocations')
    count_label = ngettext_lazy('Side allocation', 'Side allocations', 'count')
    filename = 'sides'
    priority = 20
    references = {
        'team': CSVReference('team'),
        'round': CSVReference('round'),
    }
    aliases = {'team_name': 'team', 'position': 'side'}
    converters = {'side': AnorakTournamentDataImporter.lookup_team_position}
    identity_fields = ('team', 'round')
    action = ActionLogEntry.ActionType.SIDE_PREALLOCATIONS_SAVE
    name_field = 'team'
    required_targets = ('team',)
    validation_exclusions = ('round', 'side')
    dynamic_converters = {'side': AnorakTournamentDataImporter.lookup_team_position}
    side_choices = [(DebateSide.AFF, _('Affirmative')), (DebateSide.NEG, _('Negative'))]
    extra_fields = {'side': partial(forms.TypedChoiceField, choices=side_choices, coerce=int, empty_value=None)}
    dynamic_fields = {'side': extra_fields['side']}

    def field_label(self, name):
        if name.startswith('side:'):
            return _('Side in %(round)s') % {'round': name.split(':', 1)[1]}
        return super().field_label(name)

    def guess_column(self, header):
        name = super().guess_column(header)
        return name if name in dict(self.targets) or name.startswith('side:') else 'side:' + header

    @staticmethod
    def allocations(data):
        allocations = [(data['round'], data['side'])] if data.get('round') and data.get('side') is not None else []
        allocations.extend((data['round_for_' + name], value) for name, value in data.items()
            if name.startswith('side:') and value is not None)
        return allocations

    def duplicate_keys(self, data):
        return tuple((self.key, reference_value(data['team']), reference_value(round)) for round, side in self.allocations(data))

    def object_counts(self, form):
        return {self.key: len(self.allocations(form.cleaned_data))}

    def validate_row(self, form, data):
        if not self.allocations(data):
            raise ValidationError(_('Choose a round and side, or map at least one round column.'))

    def create_object(self, form):
        data = form.cleaned_data
        objects = [self.model.objects.create(team=data['team'], round=round, side=side) for round, side in self.allocations(data)]
        return objects[0]


class AdjFeedbackQuestionCSVType(ModelCSVType):
    key = 'adj_feedback_question'
    label = _('Adjudicator feedback questions')
    count_label = ngettext_lazy('Adjudicator feedback question', 'Adjudicator feedback questions', 'count')
    filename = 'adj_feedback_questions'
    priority = 20
    converters = {
        'answer_type': AnorakTournamentDataImporter.lookup_feedback_answer_type,
        'required': convert_boolean,
        'from_adj': convert_boolean,
        'from_team': convert_boolean,
    }
    action = ActionLogEntry.ActionType.FEEDBACK_QUESTION_CREATE

    def prepare_instance(self, instance, data):
        instance.for_content_type = ContentType.objects.get_for_model(AdjudicatorFeedback)


class AdjVenueConstraintCSVType(VenueConstraintCSVType):
    key = 'adj_venue_constraint'
    label = _('Adjudicator room constraints')
    count_label = ngettext_lazy('Adjudicator room constraint', 'Adjudicator room constraints', 'count')
    filename = 'adj_venue_constraints'
    priority = 20
    fields = ('category', 'priority')
    references = {
        'category': CSVReference('venue_category'),
        'adjudicator': CSVReference('adjudicator'),
    }
    identity_fields = ('category', 'adjudicator')
    action = ActionLogEntry.ActionType.VENUE_CONSTRAINTS_EDIT
    subject_field = 'adjudicator'
    name_field = 'adjudicator'
    required_targets = ('category', 'priority', 'adjudicator')
    extra_labels = {'adjudicator': _('Adjudicator')}


class TeamVenueConstraintCSVType(VenueConstraintCSVType):
    key = 'team_venue_constraint'
    label = _('Team room constraints')
    count_label = ngettext_lazy('Team room constraint', 'Team room constraints', 'count')
    filename = 'team_venue_constraints'
    priority = 20
    fields = ('category', 'priority')
    references = {
        'category': CSVReference('venue_category'),
        'team': CSVReference('team'),
    }
    identity_fields = ('category', 'team')
    action = ActionLogEntry.ActionType.VENUE_CONSTRAINTS_EDIT
    subject_field = 'team'
    name_field = 'team'
    required_targets = ('category', 'priority', 'team')
    extra_labels = {'team': _('Team')}


def model_csv_types():
    return [
        RegionCSVType(),
        InstitutionCSVType(),
        VenueCategoryCSVType(),
        BreakCategoryCSVType(),
        SpeakerCategoryCSVType(),
        RoundCSVType(),
        VenueCSVType(),
        AdjudicatorCSVType(),
        MotionCSVType(),
        ScoreCSVType(),
        TeamConflictCSVType(),
        InstitutionConflictCSVType(),
        AdjudicatorConflictCSVType(),
        TeamInstitutionConflictCSVType(),
        SideCSVType(),
        AdjFeedbackQuestionCSVType(),
        AdjVenueConstraintCSVType(),
        TeamVenueConstraintCSVType(),
    ]
