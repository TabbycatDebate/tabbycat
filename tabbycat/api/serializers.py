from collections import OrderedDict
from collections.abc import Mapping
from functools import partialmethod
from urllib import parse

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from django.db.models import QuerySet
from django.urls import get_script_prefix, resolve, Resolver404
from django.utils import timezone
from django.utils.encoding import uri_to_iri
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.fields import get_error_detail, SkipField
from rest_framework.relations import Hyperlink
from rest_framework.settings import api_settings

from adjallocation.models import DebateAdjudicator, PreformedPanel
from adjfeedback.models import AdjudicatorFeedback, AdjudicatorFeedbackQuestion
from breakqual.models import BreakCategory, BreakingTeam
from draw.models import Debate, DebateTeam
from motions.models import DebateTeamMotionPreference, Motion, RoundMotion
from participants.emoji import pick_unused_emoji
from participants.models import Adjudicator, Institution, Region, Speaker, SpeakerCategory, Team
from participants.utils import populate_code_names
from privateurls.utils import populate_url_keys
from results.mixins import TabroomSubmissionFieldsMixin
from results.models import BallotSubmission, SpeakerScore, TeamScore
from results.result import DebateResult
from standings.speakers import SpeakerStandingsGenerator
from standings.teams import TeamStandingsGenerator
from tournaments.models import Round, Tournament
from venues.models import Venue, VenueCategory, VenueConstraint

from . import fields


def _validate_field(self, field, value):
    if value is None:
        return None
    qs = self.Meta.model.objects.filter(
        tournament=self.context['tournament'], **{field: value}).exclude(id=getattr(self.instance, 'id', None))
    if qs.exists():
        raise serializers.ValidationError("Object with same value exists in the tournament")
    return value


def is_staff(context):
    # OpenAPI generation does not have a view (sometimes context is also None in that circumstance).
    # Avoid redacting fields.
    return context is None or 'view' not in context or context['request'].user.is_staff


class BaseSourceField(fields.TournamentHyperlinkedRelatedField):
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


class RootSerializer(serializers.Serializer):
    class RootLinksSerializer(serializers.Serializer):
        v1 = serializers.HyperlinkedIdentityField(view_name='api-v1-root')

    _links = RootLinksSerializer(source='*', read_only=True)
    timezone = serializers.CharField(allow_blank=False, read_only=True)
    version = serializers.CharField()


class V1RootSerializer(serializers.Serializer):
    class V1LinksSerializer(serializers.Serializer):
        tournaments = serializers.HyperlinkedIdentityField(view_name='api-tournament-list')
        institutions = serializers.HyperlinkedIdentityField(view_name='api-global-institution-list')

    _links = V1LinksSerializer(source='*', read_only=True)


class CheckinSerializer(serializers.Serializer):
    object = serializers.HyperlinkedIdentityField(view_name='api-root')
    barcode = serializers.IntegerField()
    checked = serializers.BooleanField()
    timestamp = serializers.DateTimeField()


class AvailabilitiesSerializer(serializers.ListSerializer):
    child = fields.ParticipantAvailabilityForeignKeyField(view_name='api-availability-list')


class VenueConstraintSerializer(serializers.ModelSerializer):
    category = fields.TournamentHyperlinkedRelatedField(view_name='api-venuecategory-detail', queryset=VenueCategory.objects.all())

    class Meta:
        model = VenueConstraint
        fields = ('category', 'priority')


class TournamentSerializer(serializers.ModelSerializer):

    url = serializers.HyperlinkedIdentityField(
        view_name='api-tournament-detail',
        lookup_field='slug', lookup_url_kwarg='tournament_slug')

    current_rounds = fields.TournamentHyperlinkedRelatedField(
        view_name='api-round-detail', read_only=True, many=True,
        lookup_field='seq', lookup_url_kwarg='round_seq',
    )

    class TournamentLinksSerializer(serializers.Serializer):
        rounds = serializers.HyperlinkedIdentityField(
            view_name='api-round-list',
            lookup_field='slug', lookup_url_kwarg='tournament_slug')
        break_categories = serializers.HyperlinkedIdentityField(
            view_name='api-breakcategory-list',
            lookup_field='slug', lookup_url_kwarg='tournament_slug')
        speaker_categories = serializers.HyperlinkedIdentityField(
            view_name='api-speakercategory-list',
            lookup_field='slug', lookup_url_kwarg='tournament_slug')
        institutions = serializers.HyperlinkedIdentityField(
            view_name='api-institution-list',
            lookup_field='slug', lookup_url_kwarg='tournament_slug')
        teams = serializers.HyperlinkedIdentityField(
            view_name='api-team-list',
            lookup_field='slug', lookup_url_kwarg='tournament_slug')
        adjudicators = serializers.HyperlinkedIdentityField(
            view_name='api-adjudicator-list',
            lookup_field='slug', lookup_url_kwarg='tournament_slug')
        speakers = serializers.HyperlinkedIdentityField(
            view_name='api-speaker-list',
            lookup_field='slug', lookup_url_kwarg='tournament_slug')
        venues = serializers.HyperlinkedIdentityField(
            view_name='api-venue-list',
            lookup_field='slug', lookup_url_kwarg='tournament_slug')
        venue_categories = serializers.HyperlinkedIdentityField(
            view_name='api-venuecategory-list',
            lookup_field='slug', lookup_url_kwarg='tournament_slug')
        motions = serializers.HyperlinkedIdentityField(
            view_name='api-motion-list',
            lookup_field='slug', lookup_url_kwarg='tournament_slug')
        feedback = serializers.HyperlinkedIdentityField(
            view_name='api-feedback-list',
            lookup_field='slug', lookup_url_kwarg='tournament_slug')
        feedback_questions = serializers.HyperlinkedIdentityField(
            view_name='api-feedbackquestion-list',
            lookup_field='slug', lookup_url_kwarg='tournament_slug')
        preferences = serializers.HyperlinkedIdentityField(
            view_name='tournamentpreferencemodel-list',
            lookup_field='slug', lookup_url_kwarg='tournament_slug')

    _links = TournamentLinksSerializer(source='*', read_only=True)

    class Meta:
        model = Tournament
        fields = '__all__'


class RoundSerializer(serializers.ModelSerializer):
    class RoundMotionSerializer(serializers.ModelSerializer):
        id = serializers.IntegerField(source='motion.pk', read_only=True)
        url = fields.TournamentHyperlinkedRelatedField(required=False,
            view_name='api-motion-detail', queryset=Motion.objects.all(), source='motion')
        text = serializers.CharField(source='motion.text', max_length=500, required=False)
        reference = serializers.CharField(source='motion.reference', max_length=100, required=False)
        info_slide = serializers.CharField(source='motion.info_slide', required=False)

        class Meta:
            model = RoundMotion
            exclude = ('round', 'motion')

        def validate_seq(self, value):
            qs = RoundMotion.objects.filter(
                round=self.context['round'], seq=value).exclude(id=getattr(self.instance, 'id', None))
            if qs.exists():
                raise serializers.ValidationError("Object with same value exists in the round")
            return value

        def create(self, validated_data):
            motion_data = validated_data.pop('motion')
            if '' in motion_data:
                validated_data['motion'] = motion_data['']
            else:
                validated_data['motion'] = Motion()

            validated_data['motion'].text = motion_data['text']
            validated_data['motion'].reference = motion_data['reference']
            validated_data['motion'].info_slide = motion_data.get('info_slide', '')
            validated_data['motion'].save()

            return super().create(validated_data)

    class RoundLinksSerializer(serializers.Serializer):
        pairing = fields.TournamentHyperlinkedIdentityField(
            view_name='api-pairing-list',
            lookup_field='seq', lookup_url_kwarg='round_seq')

    url = fields.TournamentHyperlinkedIdentityField(
        view_name='api-round-detail',
        lookup_field='seq', lookup_url_kwarg='round_seq')
    break_category = fields.TournamentHyperlinkedRelatedField(
        view_name='api-breakcategory-detail',
        queryset=BreakCategory.objects.all(),
        allow_null=True, required=False)
    motions = RoundMotionSerializer(many=True, source='roundmotion_set')

    _links = RoundLinksSerializer(source='*', read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not is_staff(kwargs.get('context')):
            self.fields.pop('feedback_weight')

            # Can't show in a ListSerializer
            if isinstance(self.instance, QuerySet) or not self.instance.motions_released:
                self.fields.pop('motions')

    class Meta:
        model = Round
        exclude = ('tournament',)

    validate_seq = partialmethod(_validate_field, 'seq')

    def validate(self, data):
        bc = data.get('break_category', getattr(self.instance, 'break_category', None))
        stage = data.get('stage', getattr(self.instance, 'stage', Round.STAGE_ELIMINATION))
        if (bc is None) == (stage == Round.STAGE_ELIMINATION):
            # break category is None _XNOR_ stage is elimination
            raise serializers.ValidationError("Rounds are elimination iff they have a break category.")
        return super().validate(data)

    def create(self, validated_data):
        motions_data = validated_data.pop('roundmotion_set', [])
        round = super().create(validated_data)

        if len(motions_data) > 0:
            motions = self.RoundMotionSerializer(many=True, context=self.context)
            motions._validated_data = motions_data  # Data was already validated
            motions.save(round=round)

        return round

    def update(self, instance, validated_data):
        motions_data = validated_data.pop('motion_set', [])
        for roundmotion in motions_data:
            motion = roundmotion['motion'].get('pk')
            if motion is None:
                motion = Motion(
                    text=roundmotion['motion']['text'],
                    reference=roundmotion['motion']['reference'],
                    info_slide=roundmotion['motion'].get('info_slide'),
                )
            else:
                motion.text = roundmotion['motion']['text']
                motion.reference = roundmotion['motion']['reference']
                motion.info_slide = roundmotion['motion'].get('info_slide')
            motion.save()
            RoundMotion.objects.update_or_create(round=instance, motion=motion, defaults={'seq': roundmotion['seq']})
        return super().update(instance, validated_data)

    """Remove once DRF supports the serializer's structure"""
    def set_value(self, dictionary, keys, value):
        """
        Similar to Python's built in `dictionary[key] = value`,
        but takes a list of nested keys instead of a single key.
        set_value({'a': 1}, [], {'b': 2}) -> {'a': 1, 'b': 2}
        set_value({'a': 1}, ['x'], 2) -> {'a': 1, 'x': 2}
        set_value({'a': 1}, ['x', 'y'], 2) -> {'a': 1, 'x': {'y': 2}}
        """
        if not keys:
            dictionary.update(value)
            return
        for key in keys[:-1]:
            if key not in dictionary:
                dictionary[key] = {}
            elif type(dictionary[key]) is not dict:
                dictionary[key] = {'': dictionary[key]}
            dictionary = dictionary[key]

        if keys[-1] in dictionary and type(dictionary[keys[-1]]) is dict:
            dictionary[keys[-1]][''] = value
        else:
            dictionary[keys[-1]] = value

    def to_internal_value(self, data):
        """
        Dict of native values <- Dict of primitive datatypes.

        Copied from DRF while waiting for #8001/#7671 as the format is nested
        differently from the stock "set_value"
        """
        if not isinstance(data, Mapping):
            message = self.error_messages['invalid'].format(datatype=type(data).__name__)
            raise serializers.ValidationError({
                api_settings.NON_FIELD_ERRORS_KEY: [message],
            }, code='invalid')
        ret = OrderedDict()
        errors = OrderedDict()
        fields = self._writable_fields
        for field in fields:
            validate_method = getattr(self, 'validate_' + field.field_name, None)
            primitive_value = field.get_value(data)
            try:
                validated_value = field.run_validation(primitive_value)
                if validate_method is not None:
                    validated_value = validate_method(validated_value)
            except serializers.ValidationError as exc:
                errors[field.field_name] = exc.detail
            except DjangoValidationError as exc:
                errors[field.field_name] = get_error_detail(exc)
            except SkipField:
                pass
            else:
                self.set_value(ret, field.source_attrs, validated_value)

        if errors:
            raise serializers.ValidationError(errors)
        return ret


class MotionSerializer(serializers.ModelSerializer):
    class RoundsSerializer(serializers.ModelSerializer):
        # Should these be filtered if unreleased?
        round = fields.TournamentHyperlinkedRelatedField(view_name='api-round-detail',
            lookup_field='seq', lookup_url_kwarg='round_seq',
            queryset=Round.objects.all())

        class Meta:
            model = RoundMotion
            fields = ('round', 'seq')

    url = fields.TournamentHyperlinkedIdentityField(view_name='api-motion-detail')
    rounds = RoundsSerializer(many=True, source='roundmotion_set')

    class Meta:
        model = Motion
        exclude = ('tournament',)

    def create(self, validated_data):
        rounds_data = validated_data.pop('roundmotion_set')
        motion = super().create(validated_data)

        if len(rounds_data) > 0:
            rounds = self.RoundsSerializer(many=True, context=self.context)
            rounds._validated_data = rounds_data  # Data was already validated
            rounds.save(motion=motion)

        return motion


class BreakCategorySerializer(serializers.ModelSerializer):

    class BreakCategoryLinksSerializer(serializers.Serializer):
        eligibility = fields.TournamentHyperlinkedIdentityField(
            view_name='api-breakcategory-eligibility')
        breaking_teams = fields.TournamentHyperlinkedIdentityField(
            view_name='api-breakcategory-break')

    url = fields.TournamentHyperlinkedIdentityField(
        view_name='api-breakcategory-detail')

    _links = BreakCategoryLinksSerializer(source='*', read_only=True)

    class Meta:
        model = BreakCategory
        exclude = ('tournament', 'breaking_teams')

    validate_slug = partialmethod(_validate_field, 'slug')
    validate_seq = partialmethod(_validate_field, 'seq')


class SpeakerCategorySerializer(serializers.ModelSerializer):

    class SpeakerCategoryLinksSerializer(serializers.Serializer):
        eligibility = fields.TournamentHyperlinkedIdentityField(
            view_name='api-speakercategory-eligibility', lookup_field='pk')

    url = fields.TournamentHyperlinkedIdentityField(
        view_name='api-speakercategory-detail', lookup_field='pk')
    _links = SpeakerCategoryLinksSerializer(source='*', read_only=True)

    class Meta:
        model = SpeakerCategory
        exclude = ('tournament',)

    validate_slug = partialmethod(_validate_field, 'slug')
    validate_seq = partialmethod(_validate_field, 'seq')


class BaseEligibilitySerializer(serializers.ModelSerializer):

    class Meta:
        read_only_fields = ('slug',)

    def update(self, instance, validated_data):
        participants = validated_data.get(self.Meta.participants_field, [])

        if self.partial:
            # Add teams to category, don't remove any
            getattr(self.instance, self.Meta.participants_field).add(*participants)
        else:
            getattr(self.instance, self.Meta.participants_field).set(participants)
        return self.instance


class BreakEligibilitySerializer(BaseEligibilitySerializer):

    team_set = fields.TournamentHyperlinkedRelatedField(
        many=True,
        queryset=Team.objects.all(),
        view_name='api-team-detail',
    )

    class Meta(BaseEligibilitySerializer.Meta):
        model = BreakCategory
        participants_field = 'team_set'
        fields = ('slug', participants_field)


class SpeakerEligibilitySerializer(BaseEligibilitySerializer):

    speaker_set = fields.TournamentHyperlinkedRelatedField(
        many=True,
        queryset=Speaker.objects.all(),
        view_name='api-speaker-detail',
        tournament_field='team__tournament',
    )

    class Meta(BaseEligibilitySerializer.Meta):
        model = SpeakerCategory
        participants_field = 'speaker_set'
        fields = ('slug', participants_field)


class BreakingTeamSerializer(serializers.ModelSerializer):
    team = fields.TournamentHyperlinkedRelatedField(view_name='api-team-detail', queryset=Team.objects.all())

    class Meta:
        model = BreakingTeam
        exclude = ('id', 'break_category')

    def validate_team(self, value):
        qs = BreakingTeam.objects.filter(
            break_category=self.context['break_category'], team=value).exclude(id=getattr(self.instance, 'id', None))
        if qs.exists():
            raise serializers.ValidationError("Object with same value already exists")
        return value


class PartialBreakingTeamSerializer(BreakingTeamSerializer):
    class Meta:
        model = BreakingTeam
        fields = ('team', 'remark')

    def save(self, **kwargs):
        bt = self.context['break_category'].breakingteam_set.get(team=self.validated_data['team'])
        bt.remark = self.validated_data.get('remark', '')
        bt.save()
        return bt


class SpeakerSerializer(serializers.ModelSerializer):

    class SpeakerLinksSerializer(serializers.Serializer):
        checkin = fields.TournamentHyperlinkedIdentityField(tournament_field='team__tournament', view_name='api-speaker-checkin')

    url = fields.TournamentHyperlinkedIdentityField(tournament_field='team__tournament', view_name='api-speaker-detail')
    team = fields.TournamentHyperlinkedRelatedField(view_name='api-team-detail', queryset=Team.objects.all())
    categories = fields.TournamentHyperlinkedRelatedField(
        many=True,
        view_name='api-speakercategory-detail',
        queryset=SpeakerCategory.objects.all(),
    )
    _links = SpeakerLinksSerializer(source='*', read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not is_staff(kwargs.get('context')):
            self.fields.pop('gender')
            self.fields.pop('email')
            self.fields.pop('phone')
            self.fields.pop('pronoun')
            self.fields.pop('anonymous')
            self.fields.pop('url_key')

            if kwargs['context']['tournament'].pref('participant_code_names') == 'everywhere':
                self.fields.pop('name')

    class Meta:
        model = Speaker
        fields = '__all__'

    def create(self, validated_data):
        url_key = validated_data.pop('url_key', None)
        if url_key is not None and len(url_key) != 0:  # Let an empty string be null for the uniqueness constraint
            validated_data['url_key'] = url_key

        speaker = super().create(validated_data)

        if url_key is None:
            populate_url_keys([speaker])

        if validated_data.get('code_name') is None:
            populate_code_names([speaker])

        return speaker


class AdjudicatorSerializer(serializers.ModelSerializer):

    class AdjudicatorLinksSerializer(serializers.Serializer):
        checkin = fields.TournamentHyperlinkedIdentityField(view_name='api-adjudicator-checkin')

    url = fields.TournamentHyperlinkedIdentityField(view_name='api-adjudicator-detail')
    institution = serializers.HyperlinkedRelatedField(
        allow_null=True,
        view_name='api-global-institution-detail',
        queryset=Institution.objects.all(),
    )

    institution_conflicts = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='api-global-institution-detail',
        queryset=Institution.objects.all(),
    )
    team_conflicts = fields.TournamentHyperlinkedRelatedField(
        many=True,
        view_name='api-team-detail',
        queryset=Team.objects.all(),
    )
    adjudicator_conflicts = fields.TournamentHyperlinkedRelatedField(
        many=True,
        view_name='api-adjudicator-detail',
        queryset=Adjudicator.objects.all(),
    )
    venue_constraints = VenueConstraintSerializer(many=True, required=False)
    _links = AdjudicatorLinksSerializer(source='*', read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Remove private fields in the public endpoint if needed
        if not is_staff(kwargs.get('context')):
            self.fields.pop('institution_conflicts')
            self.fields.pop('team_conflicts')
            self.fields.pop('adjudicator_conflicts')
            self.fields.pop('venue_constraints')

            t = kwargs['context']['tournament']
            if not t.pref('show_adjudicator_institutions'):
                self.fields.pop('institution')
            if not t.pref('public_breaking_adjs'):
                self.fields.pop('breaking')
            if t.pref('participant_code_names') == 'everywhere':
                self.fields.pop('name')

            self.fields.pop('base_score')
            self.fields.pop('trainee')
            self.fields.pop('gender')
            self.fields.pop('email')
            self.fields.pop('phone')
            self.fields.pop('pronoun')
            self.fields.pop('anonymous')
            self.fields.pop('url_key')

    class Meta:
        model = Adjudicator
        exclude = ('tournament',)

    def create(self, validated_data):
        venue_constraints = validated_data.pop('venue_constraints', [])
        url_key = validated_data.pop('url_key', None)
        if url_key is not None and len(url_key) != 0:  # Let an empty string be null for the uniqueness constraint
            validated_data['url_key'] = url_key

        adj = super().create(validated_data)

        if len(venue_constraints) > 0:
            vc = VenueConstraintSerializer(many=True, context=self.context)
            vc._validated_data = venue_constraints  # Data was already validated
            vc.save(adjudicator=adj)

        if url_key is None:  # If explicitly null (and not just an empty string)
            populate_url_keys([adj])

        if validated_data.get('code_name') is None:
            populate_code_names([adj])

        if adj.institution is not None:
            adj.adjudicatorinstitutionconflict_set.get_or_create(institution=adj.institution)

        return adj

    def update(self, instance, validated_data):
        venue_constraints = validated_data.pop('venue_constraints', [])
        if len(venue_constraints) > 0:
            vc = VenueConstraintSerializer(many=True, context=self.context)
            vc._validated_data = venue_constraints  # Data was already validated
            vc.save(adjudicator=instance)

        return super().update(instance, validated_data)


class TeamSerializer(serializers.ModelSerializer):
    class TeamSpeakerSerializer(SpeakerSerializer):
        team = None

        class Meta:
            model = Speaker
            exclude = ('team',)

    url = fields.TournamentHyperlinkedIdentityField(view_name='api-team-detail')
    institution = serializers.HyperlinkedRelatedField(
        allow_null=True,
        view_name='api-global-institution-detail',
        queryset=Institution.objects.all(),
    )
    break_categories = fields.TournamentHyperlinkedRelatedField(
        many=True,
        view_name='api-breakcategory-detail',
        queryset=BreakCategory.objects.all(),
    )

    institution_conflicts = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='api-global-institution-detail',
        queryset=Institution.objects.all(),
    )

    venue_constraints = VenueConstraintSerializer(many=True, required=False)

    class Meta:
        model = Team
        exclude = ('tournament', 'type')

    def __init__(self, *args, **kwargs):
        self.fields['speakers'] = self.TeamSpeakerSerializer(*args, many=True, required=False, **kwargs)

        super().__init__(*args, **kwargs)

        # Remove private fields in the public endpoint if needed
        if not is_staff(kwargs.get('context')):
            self.fields.pop('institution_conflicts')
            self.fields.pop('venue_constraints')

            t = kwargs['context']['tournament']
            if t.pref('team_code_names') in ('admin-tooltips-code', 'admin-tooltips-real', 'everywhere'):
                self.fields.pop('institution')
                self.fields.pop('use_institution_prefix')
                self.fields.pop('reference')
                self.fields.pop('short_reference')
                self.fields.pop('short_name')
                self.fields.pop('long_name')
            elif not t.pref('show_team_institutions'):
                self.fields.pop('institution')
                self.fields.pop('use_institution_prefix')
            if not t.pref('public_break_categories'):
                self.fields.pop('break_categories')

    validate_emoji = partialmethod(_validate_field, 'emoji')

    def validate(self, data):
        if data.get('institution') is None and data.get('use_institution_prefix', False):
            raise serializers.ValidationError("Cannot include institution prefix without institution.")

        uniqueness_qs = Team.objects.filter(
            tournament=self.context['tournament'],
            reference=data.get('reference'),
            institution=data.get('institution'),
        ).exclude(id=getattr(self.instance, 'id', None))
        if uniqueness_qs.exists() and not self.partial:
            raise serializers.ValidationError("Team with same reference and institution exists in the tournament")

        return super().validate(data)

    def create(self, validated_data):
        """Four things must be done, excluding saving the Team object:
        1. Create the short_reference based on 'reference',
        2. Create emoji/code name if not stated,
        3. Create the speakers.
        4. Add institution conflict"""

        if len(validated_data.get('short_reference', "")) == 0:
            validated_data['short_reference'] = validated_data['reference'][:34]

        speakers_data = validated_data.pop('speakers', [])
        break_categories = validated_data.pop('break_categories', [])
        venue_constraints = validated_data.pop('venue_constraints', [])

        emoji, code_name = pick_unused_emoji()
        if 'emoji' not in validated_data or validated_data.get('emoji') is None:
            validated_data['emoji'] = emoji
        if 'code_name' not in validated_data or validated_data.get('code_name') is None:
            validated_data['code_name'] = code_name

        if validated_data['emoji'] == '':
            validated_data['emoji'] = None  # Must convert to null to avoid uniqueness errors

        team = super().create(validated_data)

        # Add general break categories
        team.break_categories.set(list(BreakCategory.objects.filter(
            tournament=team.tournament, is_general=True,
        ).exclude(pk__in=[bc.pk for bc in break_categories])) + break_categories)

        # The data is passed to the sub-serializer so that it handles categories
        if len(speakers_data) > 0:
            speakers = SpeakerSerializer(many=True, context=self.context)
            speakers._validated_data = speakers_data  # Data was already validated
            speakers.save(team=team)

        if len(venue_constraints) > 0:
            vc = VenueConstraintSerializer(many=True, context=self.context)
            vc._validated_data = venue_constraints  # Data was already validated
            vc.save(team=team)

        if team.institution is not None:
            team.teaminstitutionconflict_set.get_or_create(institution=team.institution)

        return team

    def update(self, instance, validated_data):
        speakers_data = validated_data.pop('speakers', [])
        venue_constraints = validated_data.pop('venue_constraints', [])
        if len(speakers_data) > 0:
            speakers = SpeakerSerializer(many=True, context=self.context)
            speakers._validated_data = speakers_data  # Data was already validated
            speakers.save(team=instance)
        if len(venue_constraints) > 0:
            vc = VenueConstraintSerializer(many=True, context=self.context)
            vc._validated_data = venue_constraints  # Data was already validated
            vc.save(institution=instance)

        return super().update(instance, validated_data)


class InstitutionSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='api-global-institution-detail')
    region = fields.CreatableSlugRelatedField(slug_field='name', queryset=Region.objects.all(), required=False)
    venue_constraints = VenueConstraintSerializer(many=True, required=False)

    class Meta:
        model = Institution
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not is_staff(kwargs.get('context')):
            self.fields.pop('venue_constraints')

    def create(self, validated_data):
        venue_constraints = validated_data.pop('venue_constraints', [])

        institution = super().create(validated_data)

        if len(venue_constraints) > 0:
            vc = VenueConstraintSerializer(many=True, context=self.context)
            vc._validated_data = venue_constraints  # Data was already validated
            vc.save(institution=institution)

        return institution

    def update(self, instance, validated_data):
        venue_constraints = validated_data.pop('venue_constraints', [])
        if len(venue_constraints) > 0:
            vc = VenueConstraintSerializer(many=True, context=self.context)
            vc._validated_data = venue_constraints  # Data was already validated
            vc.save(institution=instance)

        return super().update(instance, validated_data)


class PerTournamentInstitutionSerializer(InstitutionSerializer):
    teams = fields.TournamentHyperlinkedRelatedField(
        source='team_set',
        many=True,
        view_name='api-team-detail',
        required=False,
    )
    adjudicators = fields.TournamentHyperlinkedRelatedField(
        source='adjudicator_set',
        many=True,
        view_name='api-adjudicator-detail',
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not is_staff(kwargs.get('context')):
            self.fields.pop('teams')
            self.fields.pop('adjudicators')


class VenueSerializer(serializers.ModelSerializer):

    class VenueLinksSerializer(serializers.Serializer):
        checkin = fields.TournamentHyperlinkedIdentityField(view_name='api-venue-checkin')

    url = fields.TournamentHyperlinkedIdentityField(view_name='api-venue-detail')
    categories = fields.TournamentHyperlinkedRelatedField(
        source='venuecategory_set', many=True,
        view_name='api-venuecategory-detail',
        queryset=VenueCategory.objects.all(),
    )
    display_name = serializers.ReadOnlyField()
    external_url = serializers.URLField(source='url', required=False, allow_blank=True)
    _links = VenueLinksSerializer(source='*', read_only=True)

    class Meta:
        model = Venue
        exclude = ('tournament',)


class VenueCategorySerializer(serializers.ModelSerializer):
    url = fields.TournamentHyperlinkedIdentityField(view_name='api-venuecategory-detail')
    venues = fields.TournamentHyperlinkedRelatedField(
        many=True,
        view_name='api-venue-detail',
        queryset=Venue.objects.all(),
    )

    class Meta:
        model = VenueCategory
        exclude = ('tournament',)


def get_metrics_field_type(generator):
    return {
        'type': 'array',
        'items': {
            'type': 'object',
            'properties': {
                'metric': {'type': 'string', 'enum': list(generator.metric_annotator_classes.keys())},
                'value': {'type': 'number'},
            },
        },
    }


class BaseStandingsSerializer(serializers.Serializer):
    rank = serializers.SerializerMethodField()
    tied = serializers.SerializerMethodField()
    metrics = serializers.SerializerMethodField()

    def get_rank(self, obj) -> int:
        return obj.rankings['rank'][0]

    def get_tied(self, obj) -> bool:
        return obj.rankings['rank'][1]

    def get_metrics(self, obj) -> list:
        return [{'metric': s, 'value': v} for s, v in obj.metrics.items()]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TeamStandingsSerializer(BaseStandingsSerializer):
    team = fields.TournamentHyperlinkedRelatedField(view_name='api-team-detail', queryset=Team.objects.all())

    @extend_schema_field(get_metrics_field_type(TeamStandingsGenerator))
    def get_metrics(self, obj) -> list:
        return super().get_metrics(obj)


class SpeakerStandingsSerializer(BaseStandingsSerializer):
    speaker = fields.AnonymisingHyperlinkedTournamentRelatedField(view_name='api-speaker-detail', anonymous_source='anonymous')

    @extend_schema_field(get_metrics_field_type(SpeakerStandingsGenerator))
    def get_metrics(self, obj) -> list:
        return super().get_metrics(obj)


class DebateAdjudicatorSerializer(serializers.Serializer):
    adjudicators = Adjudicator.objects.all()
    chair = fields.TournamentHyperlinkedRelatedField(view_name='api-adjudicator-detail', queryset=adjudicators)
    panellists = fields.TournamentHyperlinkedRelatedField(many=True, view_name='api-adjudicator-detail', queryset=adjudicators)
    trainees = fields.TournamentHyperlinkedRelatedField(many=True, view_name='api-adjudicator-detail', queryset=adjudicators)

    def save(self, **kwargs):
        aa = kwargs['debate'].adjudicators
        aa.chair = self.validated_data.get('chair')
        aa.panellists = self.validated_data.get('panellists')
        aa.trainees = self.validated_data.get('trainees')
        aa.save()
        return aa


class RoundPairingSerializer(serializers.ModelSerializer):
    class DebateTeamSerializer(serializers.ModelSerializer):
        team = fields.TournamentHyperlinkedRelatedField(view_name='api-team-detail', queryset=Team.objects.all())

        class Meta:
            model = DebateTeam
            fields = ('team', 'side')

    url = fields.RoundHyperlinkedIdentityField(view_name='api-pairing-detail', lookup_url_kwarg='debate_pk')
    venue = fields.TournamentHyperlinkedRelatedField(view_name='api-venue-detail', queryset=Venue.objects.all(),
        required=False, allow_null=True)
    teams = DebateTeamSerializer(many=True, source='debateteam_set')
    adjudicators = DebateAdjudicatorSerializer(required=False, allow_null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not is_staff(kwargs.get('context')):
            self.fields.pop('bracket')
            self.fields.pop('room_rank')
            self.fields.pop('importance')
            self.fields.pop('result_status')

    class Meta:
        model = Debate
        exclude = ('round', 'flags')

    def create(self, validated_data):
        teams_data = validated_data.pop('debateteam_set')
        adjs_data = validated_data.pop('adjudicators', None)

        validated_data['round'] = self.context['round']
        debate = super().create(validated_data)

        teams = self.DebateTeamSerializer(many=True)
        teams._validated_data = teams_data  # Data was already validated
        teams.save(debate=debate)

        if adjs_data is not None:
            adjudicators = self.DebateAdjudicatorSerializer()
            adjudicators._validated_data = adjs_data
            adjudicators.save(debate=debate)

        return debate

    def update(self, instance, validated_data):
        for team in validated_data.pop('debateteam_set', []):
            try:
                DebateTeam.objects.update_or_create(debate=instance, side=team.get('side'), defaults={
                    'team': team.get('team'),
                })
            except (IntegrityError, TypeError) as e:
                raise serializers.ValidationError(e)

        if 'adjudicators' in validated_data and validated_data['adjudicators'] is not None:
            adjudicators = self.DebateAdjudicatorSerializer()
            adjudicators._validated_data = validated_data.pop('adjudicators')
            adjudicators.save(debate=instance)

        return super().update(instance, validated_data)


class FeedbackQuestionSerializer(serializers.ModelSerializer):
    url = fields.TournamentHyperlinkedIdentityField(view_name='api-feedbackquestion-detail')

    class Meta:
        model = AdjudicatorFeedbackQuestion
        exclude = ('tournament',)

    validate_reference = partialmethod(_validate_field, 'reference')
    validate_seq = partialmethod(_validate_field, 'seq')


class FeedbackSerializer(TabroomSubmissionFieldsMixin, serializers.ModelSerializer):

    class SubmitterSourceField(BaseSourceField):
        field_source_name = 'source'
        models = {
            'api-adjudicator-detail': (Adjudicator, 'source_adjudicator'),
            'api-team-detail': (Team, 'source_team'),
        }

        def get_url_options(self, value, format):
            for view_name, (model, field) in self.models.items():
                if getattr(value, field) is not None:
                    return self.get_url(
                        getattr(getattr(value, field), model.__name__.lower()),
                        view_name, self.context['request'], format)

    class DebateHyperlinkedRelatedField(fields.RoundHyperlinkedRelatedField):
        def lookup_kwargs(self):
            return {self.tournament_field: self.context['tournament']}

    class FeedbackAnswerSerializer(serializers.Serializer):
        question = fields.TournamentHyperlinkedRelatedField(
            view_name='api-feedbackquestion-detail',
            queryset=AdjudicatorFeedbackQuestion.objects.all(),
        )
        answer = serializers.CharField()

        def validate(self, data):
            # Convert answer to correct type
            model = AdjudicatorFeedbackQuestion.ANSWER_TYPE_CLASSES[data['question'].answer_type]
            data['answer'] = model.ANSWER_TYPE(data['answer'])
            return super().validate(data)

    url = fields.AdjudicatorFeedbackIdentityField(view_name='api-feedback-detail')
    adjudicator = fields.TournamentHyperlinkedRelatedField(view_name='api-adjudicator-detail', queryset=Adjudicator.objects.all())
    source = SubmitterSourceField(source='*')
    participant_submitter = ParticipantSourceField(allow_null=True)
    debate = DebateHyperlinkedRelatedField(view_name='api-pairing-detail', queryset=Debate.objects.all(), lookup_url_kwarg='debate_pk')
    answers = FeedbackAnswerSerializer(many=True, source='get_answers', required=False)

    class Meta:
        model = AdjudicatorFeedback
        exclude = ('source_adjudicator', 'source_team')
        read_only_fields = ('timestamp', 'version',
            'submitter_type', 'participant_submitter', 'submitter',
            'confirmer', 'confirm_timestamp', 'ip_address', 'private_url')

    def validate(self, data):
        source = data.pop('source')
        debate = data.pop('debate')

        # Test answers for correct source
        source_type = 'from_team' if isinstance(source, Team) else 'from_adj'
        for answer in data.get('get_answers'):
            if not getattr(answer['question'], source_type, False):
                raise serializers.ValidationError("Question is not permitted from source.")

        # Test participants in debate
        if not data['adjudicator'].debateadjudicator_set.filter(debate=debate).exists():
            raise serializers.ValidationError("Target is not in debate")

        # Also move the source field into participant_specific fields
        if isinstance(source, Team):
            try:
                data['source_team'] = source.debateteam_set.get(debate=debate)
            except DebateTeam.DoesNotExist:
                raise serializers.ValidationError("Source is not in debate")
        elif isinstance(source, Adjudicator):
            try:
                data['source_adjudicator'] = source.debateadjudicator_set.get(debate=debate)
            except DebateAdjudicator.DoesNotExist:
                raise serializers.ValidationError("Source is not in debate")

        return super().validate(data)

    def get_request(self):
        return self.context['request']

    def create(self, validated_data):
        answers = validated_data.pop('get_answers')

        validated_data.update(self.get_submitter_fields())
        if validated_data.get('confirmed', False):
            validated_data['confirmer'] = self.context['request'].user
            validated_data['confirm_timestamp'] = timezone.now()

        feedback = super().create(validated_data)

        # Create answers
        for answer in answers:
            question = answer['question']
            model = AdjudicatorFeedbackQuestion.ANSWER_TYPE_CLASSES[question.answer_type]
            obj = model(question=question, feedback=feedback, answer=answer['answer'])
            try:
                obj.save()
            except TypeError as e:
                raise serializers.ValidationError(e)

        return feedback

    def update(self, instance, validated_data):
        if validated_data.get('confirmed', False) and not instance.confirmed:
            validated_data['confirmer'] = self.context['request'].user
            validated_data['confirm_timestamp'] = timezone.now()

        instance.confirmed = validated_data['confirmed']
        instance.ignored = validated_data['ignored']
        return super().update(instance, validated_data)


class BallotSerializer(TabroomSubmissionFieldsMixin, serializers.ModelSerializer):

    class ResultSerializer(serializers.Serializer):
        class SheetSerializer(serializers.Serializer):

            class TeamResultSerializer(serializers.Serializer):
                side = serializers.ChoiceField(choices=DebateTeam.SIDE_CHOICES)
                points = serializers.IntegerField(required=False)
                win = serializers.BooleanField(required=False)
                score = serializers.FloatField(required=False, allow_null=True)

                team = fields.TournamentHyperlinkedRelatedField(
                    view_name='api-team-detail',
                    queryset=Team.objects.all(),
                )

                class SpeechSerializer(serializers.Serializer):
                    ghost = serializers.BooleanField(required=False, help_text=SpeakerScore._meta.get_field('ghost').help_text)
                    score = serializers.FloatField()

                    speaker = fields.TournamentHyperlinkedRelatedField(
                        view_name='api-speaker-detail',
                        queryset=Speaker.objects.all(),
                        tournament_field='team__tournament',
                    )

                    def save(self, **kwargs):
                        """Requires `result`, `side`, `seq`, and `adjudicator` as extra"""
                        result = kwargs['result']
                        speaker_args = [kwargs['side'], kwargs['seq']]

                        result.set_speaker(*speaker_args, self.validated_data['speaker'])
                        if self.validated_data.get('ghost', False):
                            result.set_ghost(*speaker_args)

                        if kwargs.get('adjudicator') is not None:
                            speaker_args.insert(0, kwargs['adjudicator'])
                        result.set_score(*speaker_args, self.validated_data['score'])

                        return result

                speeches = SpeechSerializer(many=True, required=False)

                def validate(self, data):
                    # Make sure the score is the sum of the speech scores
                    score = data.get('score', None)
                    speeches = data.get('speeches', [])
                    if len(speeches) == 0:
                        if score is not None:
                            raise serializers.ValidationError("Speeches are required to assign scores.")
                    elif score is not None and score != sum(speech['score'] for speech in speeches):
                        raise serializers.ValidationError("Score must be the sum of speech scores.")

                    # Speakers must be in correct team
                    team = data.get('team', None)
                    speakers_team = set(s['speaker'].team_id for s in speeches)
                    if team is None or len(speakers_team) > 1 or (len(speakers_team) == 1 and team.id not in speakers_team):
                        raise serializers.ValidationError("Speakers must be in their team.")
                    return data

                def save(self, **kwargs):
                    result = kwargs['result']

                    if result.get_scoresheet_class().uses_declared_winners and self.validated_data.get('win', False):
                        args = [self.validated_data['side']]
                        if self.validated_data.get('adjudicator') is not None:
                            args.insert(0, self.validated_data['adjudicator'])
                        result.add_winner(*args)

                    speech_serializer = self.SpeechSerializer(context=self.context)
                    for i, speech in enumerate(self.validated_data.get('speeches', []), 1):
                        speech_serializer._validated_data = speech
                        speech_serializer.save(
                            result=result,
                            side=self.validated_data['side'],
                            seq=i,
                            adjudicator=kwargs.get('adjudicator'),
                        )
                    return result

            teams = TeamResultSerializer(many=True)
            adjudicator = fields.TournamentHyperlinkedRelatedField(
                view_name='api-adjudicator-detail',
                queryset=Adjudicator.objects.all(),
                required=False, allow_null=True,
            )

            def validate_adjudicator(self, value):
                # Make sure adj is in debate
                if not self.context.get('debate').debateadjudicator_set.filter(adjudicator=value).exists():
                    raise serializers.ValidationError('Adjudicator must be in debate')
                return value

            def validate_teams(self, value):
                # Teams in their proper positions - this also checks having proper and consistent sides
                debate = self.context.get('debate')
                if len(value) != debate.debateteam_set.count():
                    raise serializers.ValidationError('Incorrect number of teams')
                for team in value:
                    if debate.get_team(team['side']) != team['team']:
                        raise serializers.ValidationError('Inconsistent team')
                return value

            def save(self, **kwargs):
                team_serializer = self.TeamResultSerializer(context=self.context)
                for team in self.validated_data.get('teams', []):
                    team_serializer._validated_data = team
                    team_serializer.save(result=kwargs['result'], adjudicator=self.validated_data.get('adjudicator'))
                return kwargs['result']

        sheets = SheetSerializer(many=True, required=True)

        def validate(self, data):
            # Make sure the speaker order is the same between adjs
            # There must be at least one sheet
            if len(data.get('sheets', [])) == 0:
                raise serializers.ValidationError('Must have at least one sheet')
            speaker_order = [s['speaker'] for t in data['sheets'][0]['teams'] for s in t.get('speeches', [])]
            for sheet in data['sheets']:
                speeches = [s['speaker'] for t in sheet.get('teams', []) for s in t.get('speeches', [])]
                for i, speech in enumerate(speeches):
                    if speech != speaker_order[i]:
                        raise serializers.ValidationError('Inconsistant speaker order')
            return data

        def create(self, validated_data):
            result = DebateResult(validated_data['ballot'], tournament=self.context.get('tournament'))

            sheets = self.SheetSerializer(context=self.context)
            for sheet in validated_data['sheets']:
                sheets._validated_data = sheet
                sheets.save(result=result)

            result.save()
            return result

    class VetoSerializer(serializers.ModelSerializer):
        team = fields.TournamentHyperlinkedRelatedField(
            source='debate_team.team', view_name='api-team-detail', queryset=Team.objects.all())
        motion = fields.TournamentHyperlinkedRelatedField(view_name='api-motion-detail', queryset=Motion.objects.all())

        class Meta:
            model = DebateTeamMotionPreference
            exclude = ('id', 'ballot_submission', 'preference', 'debate_team')

        def create(self, validated_data):
            try:
                validated_data['debate_team'] = DebateTeam.objects.get(debate=self.context['debate'], team=validated_data.pop('team'))
            except (DebateTeam.DoesNotExist, DebateTeam.MultipleObjectsReturned):
                raise serializers.ValidationError('Team is not in debate')
            return super().create(validated_data)

    result = ResultSerializer(source='result.get_result_info')
    motion = fields.TournamentHyperlinkedRelatedField(view_name='api-motion-detail', required=False, queryset=Motion.objects.all())
    url = fields.DebateHyperlinkedIdentityField(view_name='api-ballot-detail')
    participant_submitter = ParticipantSourceField(allow_null=True)
    vetos = VetoSerializer(many=True, source='debateteammotionpreference_set', required=False, allow_null=True)

    class Meta:
        model = BallotSubmission
        exclude = ('debate',)
        read_only_fields = ('timestamp', 'version',
            'submitter_type', 'submitter', 'participant_submitter',
            'confirmer', 'confirm_timestamp', 'ip_address', 'single_adj', 'private_url')

    def get_request(self):
        return self.context['request']

    def create(self, validated_data):
        result_data = validated_data.pop('result').pop('get_result_info')
        veto_data = validated_data.pop('vetos', None)

        validated_data.update(self.get_submitter_fields())
        if validated_data.get('confirmed', False):
            validated_data['confirmer'] = self.context['request'].user
            validated_data['confirm_timestamp'] = timezone.now()

        stage = 'elim' if self.context['round'].stage == Round.STAGE_ELIMINATION else 'prelim'
        if self.context['tournament'].pref('ballots_per_debate_' + stage) == 'per-adj':
            if self.context['debate'].debateadjudicator_set.all().count() > 1:
                if len(result_data['sheets']) == 1:
                    validated_data['participant_submitter'] = result_data['sheets'][0]['adjudicator']
                    validated_data['single_adj'] = True
                else:
                    raise serializers.ValidationError('Single-adjudicator ballots must have only one scoresheet')

        ballot = super().create(validated_data)

        result = self.ResultSerializer(context=self.context)
        result._validated_data = result_data
        result._errors = []
        result.save(ballot=ballot)

        if veto_data:
            vetos = self.VetoSerializer(context=self.context)
            vetos._validated_data = veto_data
            vetos.save(ballot_submission=ballot, preference=3)

        return ballot

    def update(self, instance, validated_data):
        if validated_data['confirmed'] and not instance.confirmed:
            validated_data['confirmer'] = self.context['request'].user
            validated_data['confirm_timestamp'] = timezone.now()

        instance.confirmed = validated_data['confirmed']
        instance.discarded = validated_data['discarded']
        instance.save()
        return instance


class UpdateBallotSerializer(serializers.ModelSerializer):
    """Unused, just for OpenAPI with BallotSerializer.update()"""
    class Meta:
        model = BallotSubmission
        fields = ('confirmed', 'discarded')


class PreformedPanelSerializer(serializers.ModelSerializer):
    url = fields.RoundHyperlinkedIdentityField(view_name='api-preformedpanel-detail', lookup_url_kwarg='debate_pk')
    adjudicators = DebateAdjudicatorSerializer(required=False, allow_null=True)

    class Meta:
        model = PreformedPanel
        exclude = ('round',)

    def create(self, validated_data):
        adjs_data = validated_data.pop('adjudicators', None)

        validated_data['round'] = self.context['round']
        debate = super().create(validated_data)

        if adjs_data is not None:
            adjudicators = self.DebateAdjudicatorSerializer()
            adjudicators._validated_data = adjs_data
            adjudicators.save(debate=debate)

        return debate

    def update(self, instance, validated_data):
        if validated_data.get('adjudicators', None) is not None:
            adjudicators = self.DebateAdjudicatorSerializer()
            adjudicators._validated_data = validated_data.pop('adjudicators')
            adjudicators.save(debate=instance)

        return super().update(instance, validated_data)


class SpeakerRoundScoresSerializer(serializers.ModelSerializer):
    class RoundScoresSerializer(serializers.ModelSerializer):
        class RoundSpeechSerializer(serializers.ModelSerializer):
            class Meta:
                model = SpeakerScore
                fields = ('score', 'position', 'ghost')

        round = fields.TournamentHyperlinkedRelatedField(view_name='api-round-detail', source='debate.round',
            lookup_field='seq', lookup_url_kwarg='round_seq',
            queryset=Round.objects.all())

        speeches = RoundSpeechSerializer(many=True, source="scores")

        class Meta:
            model = DebateTeam
            fields = ('round', 'speeches')

    speaker = fields.TournamentHyperlinkedIdentityField(tournament_field='team__tournament', view_name='api-speaker-detail')
    rounds = RoundScoresSerializer(many=True, source="debateteams")

    class Meta:
        model = Speaker
        fields = ('speaker', 'rounds')


class TeamRoundScoresSerializer(serializers.ModelSerializer):

    class ScoreSerializer(serializers.ModelSerializer):
        round = fields.TournamentHyperlinkedRelatedField(view_name='api-round-detail', source='debate.round',
            lookup_field='seq', lookup_url_kwarg='round_seq',
            queryset=Round.objects.all())

        points = serializers.IntegerField(source='ballot.points')
        score = serializers.FloatField(source='ballot.score')
        has_ghost = serializers.BooleanField(source='ballot.has_ghost')

        class Meta:
            model = TeamScore
            fields = ('round', 'points', 'score', 'has_ghost')

    team = fields.TournamentHyperlinkedIdentityField(view_name='api-team-detail')
    rounds = ScoreSerializer(many=True, source="debateteam_set")

    class Meta:
        model = Team
        fields = ('team', 'rounds')
