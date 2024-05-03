from urllib import parse

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.urls import get_script_prefix, resolve, Resolver404
from django.utils.encoding import uri_to_iri
from drf_spectacular.utils import extend_schema_field
from rest_framework.relations import Hyperlink, HyperlinkedIdentityField, HyperlinkedRelatedField, SlugRelatedField
from rest_framework.reverse import reverse
from rest_framework.serializers import CharField, Field, IntegerField

from draw.types import DebateSide
from participants.models import Adjudicator, Speaker, Team
from venues.models import Venue

from .utils import is_staff


class TournamentHyperlinkedRelatedField(HyperlinkedRelatedField):
    default_tournament_field = 'tournament'

    def __init__(self, *args, **kwargs):
        self.tournament_field = kwargs.pop('tournament_field', self.default_tournament_field)
        super().__init__(*args, **kwargs)

    def use_pk_only_optimization(self):
        return False

    def get_tournament(self, obj):
        return obj.tournament

    def get_url_kwargs(self, obj):
        lookup_value = getattr(obj, self.lookup_field)
        kwargs = {
            'tournament_slug': self.get_tournament(obj).slug,
            self.lookup_url_kwarg: lookup_value,
        }
        return kwargs

    def get_url(self, obj, view_name, request, format):
        return reverse(view_name, kwargs=self.get_url_kwargs(obj), request=request, format=format)

    def get_object(self, view_name, view_args, view_kwargs):
        lookup_value = view_kwargs[self.lookup_url_kwarg]
        lookup_kwargs = {
            self.lookup_field: lookup_value,
        }
        return self.get_queryset().get(**lookup_kwargs)

    def lookup_kwargs(self):
        return {self.tournament_field: self.context['tournament']}

    def get_queryset(self):
        return super().get_queryset().filter(**self.lookup_kwargs()).select_related(self.tournament_field)


class TournamentHyperlinkedIdentityField(TournamentHyperlinkedRelatedField, HyperlinkedIdentityField):
    pass


class RoundHyperlinkedRelatedField(TournamentHyperlinkedRelatedField):
    default_tournament_field = 'round__tournament'
    round_field = 'round'

    def get_tournament(self, obj):
        return self.get_round(obj).tournament

    def get_round(self, obj):
        return obj.round

    def get_url_kwargs(self, obj):
        kwargs = super().get_url_kwargs(obj)
        kwargs['round_seq'] = self.get_round(obj).seq
        return kwargs

    def lookup_kwargs(self):
        return {self.round_field: self.context['round']}

    def get_queryset(self):
        return super().get_queryset().select_related(self.round_field)


class RoundHyperlinkedIdentityField(RoundHyperlinkedRelatedField, HyperlinkedIdentityField):
    pass


class DebateHyperlinkedIdentityField(RoundHyperlinkedIdentityField):
    default_tournament_field = 'debate__round__tournament'
    round_field = 'debate__round'

    def get_round(self, obj):
        return obj.debate.round

    def get_url_kwargs(self, obj):
        kwargs = super().get_url_kwargs(obj)
        kwargs['debate_pk'] = obj.debate.pk
        return kwargs

    def lookup_kwargs(self):
        return {'debate': self.context['debate']}

    def get_queryset(self):
        return super().get_queryset().select_related('debate')


class AnonymisingParticipantNameField(CharField):

    def get_attribute(self, instance):
        # Pass entire instance to use other fields (not just .name)
        return instance

    def to_representation(self, instance):
        if not is_staff(self.context):
            if instance.anonymous:
                return None
            return instance.get_public_name(self.context['tournament'])
        return super().to_representation(instance.name)


class AnonymisingHyperlinkedTournamentRelatedField(TournamentHyperlinkedRelatedField):
    default_tournament_field = 'team__tournament'

    def __init__(self, view_name=None, queryset=Speaker.objects.all(), **kwargs):
        self.null_when = kwargs.pop('anonymous_source')
        super().__init__(view_name=view_name, queryset=queryset, **kwargs)

    def to_representation(self, value):
        if getattr(value, self.null_when, True):
            return None
        return super().to_representation(value)


class AdjudicatorFeedbackIdentityField(RoundHyperlinkedIdentityField):
    default_tournament_field = None
    round_field = None

    def get_url_kwargs(self, obj):
        kwargs = super().get_url_kwargs(obj)
        kwargs.pop('round_seq')
        return kwargs

    def lookup_kwargs(self):
        return {}  # More complicated lookup than with kwargs

    def get_queryset(self):
        return super().get_queryset().filter(
            Q(source_adjudicator__debate__round=self.context['round']) | Q(source_team__debate__round=self.context['round']))


class CreatableSlugRelatedField(SlugRelatedField):
    def to_internal_value(self, data):
        if data is None:
            return None
        try:
            # get_or_create returns (obj, created?) - only want the object
            return self.get_queryset().get_or_create(**{self.slug_field: data})[0]
        except (TypeError, ValueError):
            self.fail('invalid')


class ParticipantAvailabilityForeignKeyField(TournamentHyperlinkedRelatedField):
    default_tournament_field = 'round__tournament'

    def get_tournament(self, obj):
        return obj.round.tournament

    def get_url_kwargs(self, obj):
        return {
            'tournament_slug': self.get_tournament(obj).slug,
            'pk': obj.object_id,
        }

    def get_url(self, obj, view_name, request, format):
        view_name = 'api-%s-detail' % obj.content_type.model
        return super().get_url(obj, view_name, request, format)

    def get_object(self, view_name, view_args, view_kwargs):
        return {
            'api-adjudicator-detail': Adjudicator,
            'api-team-detail': Team,
            'api-venue-detail': Venue,
        }[view_name].objects.get(tournament__slug=view_kwargs['tournament_slug'], pk=view_kwargs['pk'])

    def to_internal_value(self, data):
        try:
            http_prefix = data.startswith(('http:', 'https:'))
        except AttributeError:
            self.fail('incorrect_type', data_type=type(data).__name__)

        if http_prefix:
            # If needed, convert absolute URLs to relative path
            data = parse.urlparse(data).path
            prefix = get_script_prefix()
            if data.startswith(prefix):
                data = '/' + data[len(prefix):]

        data = uri_to_iri(parse.unquote(data))

        try:
            match = resolve(data)
        except Resolver404:
            self.fail('no_match')

        if match.view_name.split("-")[1] not in ['team', 'adjudicator', 'venue']:
            self.fail('incorrect_match')

        try:
            return self.get_object(match.view_name, match.args, match.kwargs)
        except (ObjectDoesNotExist, ValueError, TypeError):
            self.fail('does_not_exist')


class BaseSourceField(TournamentHyperlinkedRelatedField):
    """Taken from REST_Framework: rest_framework.relations.HyperlinkedRelatedField

    This subclass adapts the framework in order to have a hyperlinked field which
    is dynamic on the model of object given or taken; merging into one field, as
    well as using an attribute from it, which would not be possible for fear of
    nulls."""

    view_name = ''  # View and model/queryset is dynamic on the object

    def get_queryset(self):
        return self.model.objects.all()

    def get_attribute(self, obj):
        return obj

    def to_representation(self, value):
        format = self.context.get('format', None)
        if format and self.format and self.format != format:
            format = self.format

        # Return the hyperlink, or error if incorrectly configured.
        url = self.get_url_options(value, format)

        if url is None:
            return None

        return Hyperlink(url, value)

    def to_internal_value(self, data):
        self.source_attrs = [self.field_source_name]  # Must set

        # Was the value already entered?
        if isinstance(data, tuple(model for model, field in self.models.values())):
            return data

        try:
            http_prefix = data.startswith(('http:', 'https:'))
        except AttributeError:
            self.fail('incorrect_type', data_type=type(data).__name__)

        if http_prefix:
            # If needed, convert absolute URLs to relative path
            data = parse.urlparse(data).path
            prefix = get_script_prefix()
            if data.startswith(prefix):
                data = '/' + data[len(prefix):]

        data = uri_to_iri(data)
        try:
            match = resolve(data)
        except Resolver404:
            self.fail('no_match')

        self.model = {view: model for view, (model, field) in self.models.items()}[match.view_name]

        try:
            return self.get_object(match.view_name, match.args, match.kwargs)
        except self.model.DoesNotExist:
            self.fail('does_not_exist')


class ParticipantSourceField(BaseSourceField):
    field_source_name = 'participant_submitter'
    models = {
        'api-speaker-detail': (Speaker, 'participant_submitter'),
        'api-adjudicator-detail': (Adjudicator, 'participant_submitter'),
    }

    def get_url_options(self, value, format):
        for view_name, (model, field) in self.models.items():
            obj = getattr(value.participant_submitter, model.__name__.lower(), None)
            if obj is not None:
                return self.get_url(obj, view_name, self.context['request'], format)


@extend_schema_field({'anyOf': [{"type": "number"}, {"type": "boolean"}, {"type": "string"}, {"type": "array", "items": {"type": "string"}}]})
class AnyField(Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        return data


@extend_schema_field({'anyOf': [{"type": "number"}, {"type": "string", "enum": [ds.name.lower() for ds in DebateSide]}]})
class SideChoiceField(IntegerField):

    def to_internal_value(self, data):
        if isinstance(data, str):
            if len(data) > self.MAX_STRING_LENGTH:
                self.fail('max_string_length')
            try:
                return DebateSide[data.upper()].value
            except KeyError:
                self.fail('invalid')

        try:
            data = int(self.re_decimal.sub('', str(data)))
        except (ValueError, TypeError):
            self.fail('invalid')
        return data

    def to_representation(self, value):
        t = self.context['tournament']
        if t.pref('side_names') != '1-2':
            if value == -1:
                return 'bye'
            if t.pref('teams_in_debate') == 2:
                return ['aff', 'neg'][value]
            if t.pref('teams_in_debate') == 4:
                return ['og', 'oo', 'cg', 'co'][value]
        return int(value)
