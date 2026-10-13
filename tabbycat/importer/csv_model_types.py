"""Model-backed CSV types shared across Anorak and Boots formats."""

from datetime import date, datetime

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldDoesNotExist, ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _

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
from .csv_model_forms import CSVModelForm
from .csv_models import CSV_MODELS, IMPLICIT_REFERENCE_TYPES
from .csv_values import convert_bool
from .importers.anorak import AnorakTournamentDataImporter
from .references import reference_value


EXTRA_FIELD_LABELS = {
    'adjudicator': _('Adjudicator'), 'team': _('Team'), 'category': _('Room category'),
    'rounds': _('Rounds'), 'seq': _('Motion sequences'),
    'team_conflicts': _('Team conflicts'), 'institution_conflicts': _('Institution conflicts'),
    'adj_conflicts': _('Adjudicator conflicts'),
}


class ModelCSVType(CSVObjectType):
    side_choices = [(DebateSide.AFF, _('Affirmative')), (DebateSide.NEG, _('Negative'))]
    validation_exclusions = ()

    def __init__(self, key, label, filename, priority, *, fields=None, references=None, extras=None,
                 identity=None, defaults=None, aliases=None, converters=None, action=None, deferred=()):
        self.key, self.label, self.priority = key, label, priority
        self.model = CSV_MODELS[key]
        self.references = references or {}
        self.extra_fields = extras or {}
        excluded = {'id', 'tournament', 'for_content_type', 'subject_content_type', 'subject_id',
            'person_ptr', 'question_ptr', 'url_key', 'code_name'}
        self.model_field_names = tuple(fields or (field.name for field in self.model._meta.fields if field.editable and field.name not in excluded))
        self.field_names = tuple(dict.fromkeys((*self.model_field_names, *self.references, *self.extra_fields)))
        self.defaults = defaults or {}
        self.aliases = aliases or {}
        self.converters = converters or {}
        self.action = action
        self.deferred_fields = deferred
        self.reference_fields = tuple(self.references)
        self.name_field = 'name' if 'name' in self.field_names else 'reference' if 'reference' in self.field_names else self.field_names[0]
        if key == 'side' or key.endswith('venue_constraint'):
            self.name_field = 'adjudicator' if key.startswith('adj') else 'team'
        self.identity_fields = identity or (self.name_field,)
        self.required_targets = tuple(name for name in self.model_field_names
            if name not in self.defaults and not self.model._meta.get_field(name).blank and not self.model._meta.get_field(name).has_default())
        if key == 'side':
            self.required_targets = ('team',)
            self.validation_exclusions = ('round', 'side')
        if key.endswith('venue_constraint'):
            self.required_targets = ('category', 'priority', 'adjudicator' if key.startswith('adj') else 'team')
        self.templates = ((filename, label, self.field_names),)
        self.filename_words = (filename,)
        self.targets = [(name, self.field_label(name)) for name in self.field_names]
        self.form_class = type(f'{self.model.__name__}{key.title().replace("_", "")}CSVForm', (CSVModelForm,), {'csv_type': self})

    def field_label(self, name):
        if name.startswith('available:'):
            return _('Available in %(round)s') % {'round': name.split(':', 1)[1]}
        if name.startswith('side:'):
            return _('Side in %(round)s') % {'round': name.split(':', 1)[1]}
        if name in EXTRA_FIELD_LABELS and name not in self.model_field_names:
            return EXTRA_FIELD_LABELS[name]
        try:
            return getattr(self.model._meta.get_field(name), 'verbose_name', EXTRA_FIELD_LABELS.get(name, name.replace('_', ' ')))
        except FieldDoesNotExist:
            return name.replace('_', ' ')

    def guess_column(self, header):
        if header.casefold().startswith('available:'):
            return 'available:' + header.split(':', 1)[1]
        name = super().guess_column(header)
        if self.key == 'side' and name not in dict(self.targets):
            return 'side:' + header
        return name

    def mapping_choices(self, source):
        dynamic = [self.guess_column(header) for header in source['headers']]
        return [*self.targets, *((name, self.field_label(name)) for name in dynamic
            if name.startswith(('available:', 'side:')))]

    def form_options(self, values):
        return {'extra_columns': tuple(name for name in values if name.startswith(('available:', 'side:')))}

    def preview_field_count(self, targets):
        return len(self.field_names) + 2 * len(self.form_options(targets)['extra_columns']) + 1

    def initial(self, row, context):
        values = {**self.defaults, **row['values']}
        if self.key == 'round':
            values['seq'] = values.get('seq') or row.get('row_index', row['line'] - 2) + 1
            values['schedule_group'] = values.get('schedule_group') or values['seq']
        for name, convert in self.converters.items():
            if values.get(name) != '' and name in values:
                try:
                    values[name] = convert(values[name])
                except ValueError:
                    pass
        for name in self.field_names:
            if name in self.references:
                target, multiple = self.references[name]
                raw = values.get(name, '')
                if multiple:
                    separator = ';' if name == 'rounds' else ','
                    values[name] = [context.references.match(target, item.strip()) for item in raw.split(separator) if item.strip()]
                else:
                    values[name] = context.references.match(target, raw, create=target in IMPLICIT_REFERENCE_TYPES)
            elif name in self.model_field_names:
                field = self.model._meta.get_field(name)
                if field.has_default() and values.get(name, '') == '':
                    values[name] = field.get_default()
        for name in self.form_options(values)['extra_columns']:
            values['round_for_' + name] = context.references.match('round', name.split(':', 1)[1])
            try:
                if name.startswith('side:') and values[name]:
                    values[name] = AnorakTournamentDataImporter.lookup_team_position(values[name])
                elif name.startswith('available:'):
                    values[name] = self.convert_boolean(values[name])
            except ValueError:
                pass
        return values

    @staticmethod
    def convert_boolean(value):
        return convert_bool(str(value)) if value != '' else False

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

    def duplicate_key(self, data):
        if self.key == 'side' and data.get('round') is None:
            rounds = tuple(sorted(reference_value(value) for name, value in data.items() if name.startswith('round_for_side:')))
            return self.key, reference_value(data.get('team')), rounds
        return (self.key, *(reference_value(data[name]) if hasattr(data.get(name), '_meta') else data.get(name)
            for name in self.identity_fields))

    def duplicate_keys(self, data):
        if self.key != 'side':
            return super().duplicate_keys(data)
        team = reference_value(data.get('team'))
        rounds = [data['round']] if data.get('round') else []
        rounds.extend(data['round_for_' + name] for name, value in data.items() if name.startswith('side:') and value is not None)
        return tuple((self.key, team, reference_value(round)) for round in rounds)

    def additional_objects(self, form):
        objects = set()
        for name, (target, multiple) in self.references.items():
            values = form.cleaned_data.get(name) if multiple else [form.cleaned_data.get(name)]
            for obj in values or []:
                token = getattr(obj, '_csv_token', '') or ''
                if token.startswith('new:'):
                    objects.add((target, token))
        return objects

    def object_counts(self, form):
        if self.key == 'side':
            return {self.key: len(self.duplicate_keys(form.cleaned_data))}
        return super().object_counts(form)

    def preview_dependencies(self, data):
        fields = (*self.reference_fields, *(name for name in data if name.startswith('round_for_')))
        return reference_dependencies(data, fields)

    def prepare_instance(self, instance, data):
        if self.key == 'adj_feedback_question':
            instance.for_content_type = ContentType.objects.get_for_model(AdjudicatorFeedback)
        elif self.key.endswith('venue_constraint'):
            subject = data.get('adjudicator' if self.key.startswith('adj') else 'team')
            if subject:
                instance.subject_content_type = ContentType.objects.get_for_model(subject)
                instance.subject_id = subject.pk or 1

    def validate_row(self, form, data):
        if self.key in ('venue', 'adjudicator', 'motion', 'venue_category'):
            for existing in form.references.objects(self.key).values():
                if existing.pk != form.instance.pk and all(
                        reference_value(getattr(existing, name)) == reference_value(data.get(name)) if name in self.references else
                        getattr(existing, name) == data.get(name) for name in self.identity_fields):
                    form.add_error(self.name_field, _('A record with this identity already exists. Skip or correct this row.'))
                    break
        if self.key == 'side' and not (data.get('round') is not None and data.get('side') is not None) and not any(
                value is not None for name, value in data.items() if name.startswith('side:')):
            raise ValidationError(_('Choose a round and side, or map at least one round column.'))
        if self.key == 'motion':
            sequences = str(data.get('seq') or '').split(';') if data.get('seq') else []
            if sequences and len(sequences) != len(data.get('rounds', [])):
                raise ValidationError(_('Provide one motion sequence for each linked round.'))
            if any(not value.isdigit() or int(value) < 1 for value in sequences):
                raise ValidationError(_('Motion sequences must be positive integers.'))
        if self.key == 'adjudicator' and form.instance._csv_token and any(
                reference_value(other) == form.instance._csv_token for other in data.get('adj_conflicts', [])):
            form.add_error('adj_conflicts', _('An adjudicator cannot conflict with themselves.'))
        if self.key == 'adjudicator_conflict' and data.get('adjudicator1') == data.get('adjudicator2'):
            form.add_error('adjudicator2', _('An adjudicator cannot conflict with themselves.'))

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

    @transaction.atomic
    def save(self, form, user, **dependencies):
        kind = self.key
        data = form.cleaned_data
        for name, (target, multiple) in self.references.items():
            values = data.get(name) if multiple else [data.get(name)]
            for obj in values or []:
                if obj is not None and (getattr(obj, '_csv_token', None) or '').startswith('new:'):
                    attributes = {'name': obj.name}
                    if hasattr(obj, 'tournament_id'):
                        attributes['tournament'] = form.tournament
                    actual, unused = CSV_MODELS[target].objects.get_or_create(**attributes)
                    if multiple:
                        data[name] = [actual if item is obj else item for item in data[name]]
                    else:
                        data[name] = actual
                        if name in self.model_field_names:
                            setattr(form.instance, name, actual)
        obj = form.instance
        if kind == 'side':
            allocations = []
            if data.get('round') and data.get('side') is not None:
                allocations.append((data['round'], data['side']))
            allocations.extend((data['round_for_' + name], value) for name, value in data.items()
                if name.startswith('side:') and value is not None)
            objects = [self.model.objects.create(team=data['team'], round=round, side=side) for round, side in allocations]
            return objects[0]
        if kind.endswith('venue_constraint'):
            subject = data['adjudicator' if kind.startswith('adj') else 'team']
            obj.subject_id = subject.pk
        if kind.endswith('conflict'):
            obj, unused = self.model.objects.get_or_create(**{name: data[name] for name in self.model_field_names})
        else:
            obj.save()
        if kind == 'venue':
            VenueIdentifier.objects.create(venue=obj)
            if data.get('category'):
                data['category'].venues.add(obj)
        if kind == 'adjudicator':
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
        if kind == 'motion':
            sequences = str(data.get('seq') or '').split(';')
            for index, round in enumerate(data.get('rounds', [])):
                RoundMotion.objects.create(motion=obj, round=round, seq=int(sequences[index]) if data.get('seq') else 1)
        if kind == 'score':
            data['adjudicator'].base_score = obj.score
            data['adjudicator'].save(update_fields=['base_score'])
        for name, value in data.items():
            if name.startswith('available:') and value:
                RoundAvailability.objects.get_or_create(content_type=ContentType.objects.get_for_model(obj),
                    object_id=obj.pk, round=data['round_for_' + name])
        if self.action:
            ActionLogEntry.objects.log(type=self.action, tournament=form.tournament, content_object=obj, user=user)
        return obj

    @transaction.atomic
    def finish_references(self, form, obj):
        for other in form.cleaned_data.get('adj_conflicts', []):
            if obj.pk == other.pk:
                raise ValidationError(_('An adjudicator cannot conflict with themselves.'))
            AdjudicatorAdjudicatorConflict.objects.get_or_create(adjudicator1=obj, adjudicator2=other)


def model_csv_types():
    lookup = AnorakTournamentDataImporter
    boolean = ModelCSVType.convert_boolean
    actions = ActionLogEntry.ActionType
    return [
        ModelCSVType('region', _('Regions'), 'regions', -50),
        ModelCSVType('institution', _('Institutions'), 'institutions', -40, references={'region': ('region', False)},
            identity=('name', 'code'), action=actions.INSTITUTION_CREATE),
        ModelCSVType('venue_category', _('Room categories'), 'venue_categories', -30,
            converters={'display_in_venue_name': lookup.lookup_venue_category_display}, action=actions.VENUE_CATEGORY_CREATE),
        ModelCSVType('break_category', _('Break categories'), 'break_categories', -30,
            converters={'is_general': boolean}, action=actions.BREAK_CATEGORIES_EDIT),
        ModelCSVType('speaker_category', _('Speaker categories'), 'speaker_categories', -30,
            converters={'public': boolean}, action=actions.SPEAKER_CATEGORIES_EDIT),
        ModelCSVType('round', _('Rounds'), 'rounds', -20, references={'break_category': ('break_category', False)},
            defaults={'seq': None, 'schedule_group': None}, identity=('seq',),
            converters={'stage': lookup.lookup_round_stage, 'draw_type': lookup.lookup_draw_type, 'silent': boolean, 'completed': boolean},
            action=actions.ROUND_CREATE),
        ModelCSVType('venue', _('Rooms'), 'venues', 10, references={'category': ('venue_category', False)}, action=actions.VENUE_CREATE),
        ModelCSVType('adjudicator', _('Adjudicators'), 'adjudicators', 10,
            references={'institution': ('institution', False), 'institution_conflicts': ('institution', True),
                'team_conflicts': ('team', True), 'adj_conflicts': ('adjudicator', True)}, deferred=('adj_conflicts',),
            converters={'gender': lookup.lookup_gender, **{name: boolean for name in ('anonymous', 'trainee', 'breaking', 'independent', 'adj_core')}},
            aliases={'adjudicator': 'name', 'adj_conflicts': 'adj_conflicts', 'adjudicator_conflicts': 'adj_conflicts', 'category': ''},
            identity=('institution', 'name'), action=actions.ADJUDICATOR_CREATE),
        ModelCSVType('motion', _('Motions'), 'motions', 20, references={'rounds': ('round', True)},
            extras={'seq': forms.CharField}, action=actions.MOTION_EDIT),
        ModelCSVType('score', _('Adjudicator scores'), 'scores', 20, references={'adjudicator': ('adjudicator', False), 'round': ('round', False)},
            identity=('adjudicator', 'round'), action=actions.TEST_SCORE_EDIT),
        ModelCSVType('team_conflict', _('Adjudicator–team conflicts'), 'team_conflicts', 20,
            references={'adjudicator': ('adjudicator', False), 'team': ('team', False)}, identity=('adjudicator', 'team'), action=actions.CONFLICTS_ADJ_TEAM_EDIT),
        ModelCSVType('institution_conflict', _('Adjudicator–institution conflicts'), 'institution_conflicts', 20,
            references={'adjudicator': ('adjudicator', False), 'institution': ('institution', False)},
            identity=('adjudicator', 'institution'), action=actions.CONFLICTS_ADJ_INST_EDIT),
        ModelCSVType('adjudicator_conflict', _('Adjudicator conflicts'), 'adjudicator_conflicts', 20,
            references={'adjudicator1': ('adjudicator', False), 'adjudicator2': ('adjudicator', False)},
            identity=('adjudicator1', 'adjudicator2'), action=actions.CONFLICTS_ADJ_ADJ_EDIT),
        ModelCSVType('team_institution_conflict', _('Team–institution conflicts'), 'team_institution_conflicts', 20,
            references={'team': ('team', False), 'institution': ('institution', False)}, identity=('team', 'institution'), action=actions.CONFLICTS_TEAM_INST_EDIT),
        ModelCSVType('side', _('Side allocations'), 'sides', 20, references={'team': ('team', False), 'round': ('round', False)},
            aliases={'team_name': 'team', 'position': 'side'}, converters={'side': lookup.lookup_team_position},
            identity=('team', 'round'), action=actions.SIDE_PREALLOCATIONS_SAVE),
        ModelCSVType('adj_feedback_question', _('Adjudicator feedback questions'), 'adj_feedback_questions', 20,
            converters={'answer_type': lookup.lookup_feedback_answer_type, 'required': boolean, 'from_adj': boolean, 'from_team': boolean},
            action=actions.FEEDBACK_QUESTION_CREATE),
        ModelCSVType('adj_venue_constraint', _('Adjudicator room constraints'), 'adj_venue_constraints', 20,
            fields=('category', 'priority'), references={'category': ('venue_category', False), 'adjudicator': ('adjudicator', False)},
            identity=('category', 'adjudicator'), action=actions.VENUE_CONSTRAINTS_EDIT),
        ModelCSVType('team_venue_constraint', _('Team room constraints'), 'team_venue_constraints', 20,
            fields=('category', 'priority'), references={'category': ('venue_category', False), 'team': ('team', False)},
            identity=('category', 'team'), action=actions.VENUE_CONSTRAINTS_EDIT),
    ]
