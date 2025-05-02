from collections import OrderedDict
from collections.abc import Mapping
from datetime import date, datetime, time
from functools import partial, partialmethod

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from django.db.models import QuerySet
from django.utils import timezone
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.fields import get_error_detail, SkipField
from rest_framework.settings import api_settings

from adjallocation.models import DebateAdjudicator, PreformedPanel
from adjfeedback.models import AdjudicatorBaseScoreHistory, AdjudicatorFeedback, AdjudicatorFeedbackQuestion
from breakqual.models import BreakCategory, BreakingTeam
from draw.manager import DrawManager
from draw.models import Debate, DebateTeam
from motions.models import DebateTeamMotionPreference, Motion, RoundMotion
from options.preferences import (BPAssignmentMethod, BPPositionCost, BPPullupDistribution, DrawAvoidConflicts,
    DrawOddBracket, DrawPairingMethod, DrawPullupRestriction, DrawSideAllocations)
from participants.emoji import pick_unused_emoji
from participants.models import Adjudicator, Institution, Person, Region, Speaker, SpeakerCategory, Team
from participants.utils import populate_code_names
from privateurls.utils import populate_url_keys
from results.models import BallotSubmission, ScoreCriterion, SpeakerScore, Submission, TeamScore
from results.result import DebateResult, ResultError
from standings.speakers import SpeakerStandingsGenerator
from standings.teams import TeamStandingsGenerator
from tournaments.models import Round, Tournament
from users.models import Group
from users.permissions import has_permission, Permission
from utils.misc import get_ip_address
from venues.models import Venue, VenueCategory, VenueConstraint

from . import fields
from .utils import is_staff


def _validate_field(self, field, value):
    if value is None:
        return None
    qs = self.Meta.model.objects.filter(
        tournament=self.context['tournament'], **{field: value}).exclude(id=getattr(self.instance, 'id', None))
    if qs.exists():
        raise serializers.ValidationError("Object with same value exists in the tournament")
    return value


def save_related(serializer, data, context, save_fields):
    s = serializer(many=isinstance(data, list), context=context)
    s._validated_data = data
    s._errors = []
    s.save(**save_fields)


def create_barcode(instance, barcode):
    checkin_model = type(instance).checkin_identifier.related.related_model
    checkin_model.objects.create(barcode=barcode, **{checkin_model.instance_attr: instance})


def handle_update_barcode(instance, validated_data):
    if barcode := validated_data.pop('checkin_identifier', {}).get('barcode', None):
        if ci := getattr(instance, 'checkin_identifier', None):
            ci.barcode = barcode
            ci.save()
        else:
            create_barcode(instance, barcode)


class RootSerializer(serializers.Serializer):
    class RootLinksSerializer(serializers.Serializer):
        v1 = serializers.HyperlinkedIdentityField(view_name='api-v1-root')

    _links = RootLinksSerializer(source='*', read_only=True)
    timezone = serializers.CharField(allow_blank=False, read_only=True)
    version = serializers.CharField()
    version_name = serializers.CharField()


class V1RootSerializer(serializers.Serializer):
    class V1LinksSerializer(serializers.Serializer):
        tournaments = serializers.HyperlinkedIdentityField(view_name='api-tournament-list')
        institutions = serializers.HyperlinkedIdentityField(view_name='api-global-institution-list')
        users = serializers.HyperlinkedIdentityField(view_name='api-user-list')

    _links = V1LinksSerializer(source='*', read_only=True)


class CheckinSerializer(serializers.Serializer):
    object = serializers.HyperlinkedIdentityField(view_name='api-root')
    barcode = serializers.CharField()
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
        info_slide_plain = serializers.CharField(source='motion.info_slide_plain', read_only=True)
        seq = serializers.IntegerField(read_only=True)

        class Meta:
            model = RoundMotion
            exclude = ('round', 'motion')

        def create(self, validated_data):
            motion_data = validated_data.pop('motion')
            if isinstance(motion_data, Motion):  # If passed in a URL - Becomes an object
                validated_data['motion'] = motion_data
            else:
                validated_data['motion'] = Motion(
                    text=motion_data['text'],
                    reference=motion_data['reference'],
                    info_slide=motion_data.get('info_slide', ''),
                    tournament=self.context['tournament'],
                )
                validated_data['motion'].save()

            return super().create(validated_data)

    class RoundLinksSerializer(serializers.Serializer):
        pairing = fields.TournamentHyperlinkedIdentityField(
            view_name='api-pairing-list',
            lookup_field='seq', lookup_url_kwarg='round_seq')
        availabilities = fields.TournamentHyperlinkedIdentityField(view_name='api-availability-list', lookup_field='seq', lookup_url_kwarg='round_seq')
        preformed_panels = fields.TournamentHyperlinkedIdentityField(view_name='api-preformedpanel-list', lookup_field='seq', lookup_url_kwarg='round_seq')

    class TimeOrDateTimeField(serializers.DateTimeField):
        def to_internal_value(self, value):
            try:
                value = time.fromisoformat(value)
            except ValueError:
                return super().to_internal_value(value)

            value = datetime.combine(date.today(), value)
            return super().to_internal_value(value)

    url = fields.TournamentHyperlinkedIdentityField(
        view_name='api-round-detail',
        lookup_field='seq', lookup_url_kwarg='round_seq')
    break_category = fields.TournamentHyperlinkedRelatedField(
        view_name='api-breakcategory-detail',
        queryset=BreakCategory.objects.all(),
        allow_null=True, required=False)
    motions = RoundMotionSerializer(many=True, source='roundmotion_set', required=False)
    starts_at = TimeOrDateTimeField(required=False, allow_null=True)

    _links = RoundLinksSerializer(source='*', read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not is_staff(kwargs.get('context')):
            with_permission = partial(has_permission, user=kwargs['context']['request'].user, tournament=kwargs['context']['tournament'])
            if not with_permission(permission=Permission.VIEW_FEEDBACK_OVERVIEW):
                self.fields.pop('feedback_weight')

            # Can't show in a ListSerializer
            if not with_permission(permission=Permission.VIEW_MOTION) and (isinstance(self.instance, QuerySet) or not self.instance.motions_released):
                self.fields.pop('motions')

    class Meta:
        model = Round
        exclude = ('tournament',)

    validate_seq = partialmethod(_validate_field, 'seq')

    def validate(self, data):
        bc = data.get('break_category', getattr(self.instance, 'break_category', None))
        stage = data.get('stage', getattr(self.instance, 'stage', Round.Stage.PRELIMINARY))
        if (bc is None) == (stage == Round.Stage.ELIMINATION):
            # break category is None _XNOR_ stage is elimination
            raise serializers.ValidationError("Rounds are elimination iff they have a break category.")
        return super().validate(data)

    def create(self, validated_data):
        motions_data = validated_data.pop('roundmotion_set', [])
        if len(motions_data) > 0 and not has_permission(self.context['request'].user, Permission.EDIT_MOTION, self.context['tournament']):
            raise serializers.PermissionDenied('Editing motions disallowed')

        round = super().create(validated_data)

        for i, motion in enumerate(motions_data, start=1):
            save_related(self.RoundMotionSerializer, motion, self.context, {'round': round, 'seq': i})

        return round

    def update(self, instance, validated_data):
        motions_data = validated_data.pop('roundmotion_set', [])
        if len(motions_data) > 0 and not has_permission(self.context['request'].user, Permission.EDIT_MOTION, self.context['tournament']):
            raise serializers.PermissionDenied('Editing motions disallowed')
        for i, roundmotion in enumerate(motions_data, start=1):
            roundmotion['seq'] = i

            motion = roundmotion['motion'].get('pk')
            if motion is None:
                motion = Motion(
                    text=roundmotion['motion']['text'],
                    reference=roundmotion['motion']['reference'],
                    info_slide=roundmotion['motion'].get('info_slide', ''),
                    tournament=instance.tournament,
                )
            else:
                motion.text = roundmotion['motion']['text']
                motion.reference = roundmotion['motion']['reference']
                motion.info_slide = roundmotion['motion'].get('info_slide', '')
            motion.save()
            RoundMotion.objects.update_or_create(round=instance, motion=motion, defaults={'seq': roundmotion['seq']})

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

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
    info_slide_plain = serializers.CharField(read_only=True)

    class Meta:
        model = Motion
        exclude = ('tournament',)

    def create(self, validated_data):
        rounds_data = validated_data.pop('roundmotion_set')
        motion = super().create(validated_data)

        save_related(self.RoundsSerializer, rounds_data, self.context, {'motion': motion})

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

    def validate_team(self, value):
        try:
            return self.context['break_category'].breakingteam_set.get(team=value)
        except BreakingTeam.DoesNotExist:
            raise serializers.ValidationError('Team is not included in break')

    def save(self, **kwargs):
        bt = self.validated_data['team']
        bt.remark = self.validated_data.get('remark', '')
        bt.save()
        return bt


class SpeakerSerializer(serializers.ModelSerializer):

    class SpeakerLinksSerializer(serializers.Serializer):
        checkin = fields.TournamentHyperlinkedIdentityField(tournament_field='team__tournament', view_name='api-speaker-checkin')

    url = fields.TournamentHyperlinkedIdentityField(tournament_field='team__tournament', view_name='api-speaker-detail')
    name = fields.AnonymisingParticipantNameField()
    team = fields.TournamentHyperlinkedRelatedField(view_name='api-team-detail', queryset=Team.objects.all())
    categories = fields.TournamentHyperlinkedRelatedField(
        many=True,
        view_name='api-speakercategory-detail',
        queryset=SpeakerCategory.objects.all(),
    )
    _links = SpeakerLinksSerializer(source='*', read_only=True)
    barcode = serializers.CharField(source='checkin_identifier.barcode', required=False, allow_null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not is_staff(kwargs.get('context')):
            t = kwargs['context']['tournament']
            with_permission = partial(has_permission, user=kwargs['context']['request'].user, tournament=t)
            if not with_permission(permission=Permission.VIEW_PARTICIPANT_CONTACT):
                self.fields.pop('email')
                self.fields.pop('phone')
            if not with_permission(permission=Permission.VIEW_PARTICIPANT_GENDER):
                self.fields.pop('gender')
                self.fields.pop('pronoun')
            if not with_permission(permission=Permission.VIEW_PRIVATE_URLS):
                self.fields.pop('url_key')
            if not with_permission(permission=Permission.VIEW_CHECKIN):
                self.fields.pop('barcode')

            if not with_permission(permission=Permission.VIEW_PARTICIPANT_DECODED) and t.pref('participant_code_names') == 'everywhere':
                self.fields.pop('name')

    class Meta:
        model = Speaker
        fields = '__all__'

    def create(self, validated_data):
        barcode = validated_data.pop('checkin_identifier', {}).get('barcode', None)
        url_key = validated_data.pop('url_key', None)
        if url_key is not None and len(url_key) != 0:  # Let an empty string be null for the uniqueness constraint
            validated_data['url_key'] = url_key

        speaker = super().create(validated_data)

        if barcode:
            create_barcode(speaker, barcode)

        if url_key is None:
            populate_url_keys([speaker])

        if validated_data.get('code_name') is None:
            populate_code_names([speaker])

        return speaker

    def update(self, instance, validated_data):
        handle_update_barcode(instance, validated_data)
        return super().update(instance, validated_data)


class AdjudicatorSerializer(serializers.ModelSerializer):

    class AdjudicatorLinksSerializer(serializers.Serializer):
        checkin = fields.TournamentHyperlinkedIdentityField(view_name='api-adjudicator-checkin')

    url = fields.TournamentHyperlinkedIdentityField(view_name='api-adjudicator-detail')
    name = fields.AnonymisingParticipantNameField()
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
    barcode = serializers.CharField(source='checkin_identifier.barcode', required=False, allow_null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Remove private fields in the public endpoint if needed
        if not is_staff(kwargs.get('context')):
            t = kwargs['context']['tournament']
            with_permission = partial(has_permission, user=kwargs['context']['request'].user, tournament=t)

            if not with_permission(permission=Permission.VIEW_ADJ_INST_CONFLICTS):
                self.fields.pop('institution_conflicts')
            if not with_permission(permission=Permission.VIEW_ADJ_TEAM_CONFLICTS):
                self.fields.pop('team_conflicts')
            if not with_permission(permission=Permission.VIEW_ADJ_ADJ_CONFLICTS):
                self.fields.pop('adjudicator_conflicts')
            if not with_permission(permission=Permission.VIEW_ROOMCONSTRAINTS):
                self.fields.pop('venue_constraints')

            if not with_permission(permission=Permission.VIEW_PARTICIPANT_INST) and not t.pref('show_adjudicator_institutions'):
                self.fields.pop('institution')
            if not with_permission(permission=Permission.VIEW_ADJ_BREAK) and not t.pref('public_breaking_adjs'):
                self.fields.pop('breaking')
            if not with_permission(permission=Permission.VIEW_PARTICIPANT_DECODED) and t.pref('participant_code_names') == 'everywhere':
                self.fields.pop('name')

            if not with_permission(permission=Permission.VIEW_FEEDBACK_OVERVIEW):
                self.fields.pop('base_score')
                self.fields.pop('trainee')

            if not with_permission(permission=Permission.VIEW_PARTICIPANT_CONTACT):
                self.fields.pop('email')
                self.fields.pop('phone')
            if not with_permission(permission=Permission.VIEW_PARTICIPANT_GENDER):
                self.fields.pop('gender')
                self.fields.pop('pronoun')
            if not with_permission(permission=Permission.VIEW_PRIVATE_URLS):
                self.fields.pop('url_key')
            if not with_permission(permission=Permission.VIEW_CHECKIN):
                self.fields.pop('barcode')

    class Meta:
        model = Adjudicator
        exclude = ('tournament',)

    def create(self, validated_data):
        venue_constraints = validated_data.pop('venue_constraints', [])
        barcode = validated_data.pop('checkin_identifier', {}).get('barcode', None)
        url_key = validated_data.pop('url_key', None)
        if url_key is not None and len(url_key) != 0:  # Let an empty string be null for the uniqueness constraint
            validated_data['url_key'] = url_key

        adj = super().create(validated_data)

        save_related(VenueConstraintSerializer, venue_constraints, self.context, {'subject': adj})

        if barcode:
            create_barcode(adj, barcode)

        if url_key is None:  # If explicitly null (and not just an empty string)
            populate_url_keys([adj])

        if validated_data.get('code_name') is None:
            populate_code_names([adj])

        if adj.institution is not None:
            adj.adjudicatorinstitutionconflict_set.get_or_create(institution=adj.institution)

        return adj

    def update(self, instance, validated_data):
        save_related(VenueConstraintSerializer, validated_data.pop('venue_constraints', []), self.context, {'subject': instance})
        handle_update_barcode(instance, validated_data)

        if 'base_score' in validated_data and validated_data['base_score'] != instance.base_score:
            AdjudicatorBaseScoreHistory.objects.create(
                adjudicator=instance, round=self.context['tournament'].current_round, score=validated_data['base_score'])

        if self.partial:
            # Avoid removing conflicts if merely PATCHing
            for field in ['institution_conflicts', 'adjudicator_conflicts', 'team_conflicts']:
                validated_data[field] = list(getattr(instance, field).all()) + validated_data.get(field, [])

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
        required=False,
    )
    break_categories = fields.TournamentHyperlinkedRelatedField(
        many=True,
        view_name='api-breakcategory-detail',
        queryset=BreakCategory.objects.all(),
        required=False,
    )

    institution_conflicts = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='api-global-institution-detail',
        queryset=Institution.objects.all(),
        required=False,
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
            t = kwargs['context']['tournament']
            with_permission = partial(has_permission, user=kwargs['context']['request'].user, tournament=t)

            if not with_permission(permission=Permission.VIEW_TEAM_INST_CONFLICTS):
                self.fields.pop('institution_conflicts')
            if not with_permission(permission=Permission.VIEW_ROOMCONSTRAINTS):
                self.fields.pop('venue_constraints')

            if not with_permission(permission=Permission.VIEW_DECODED_TEAMS) and t.pref('team_code_names') in ('admin-tooltips-code', 'admin-tooltips-real', 'everywhere'):
                self.fields.pop('institution')
                self.fields.pop('use_institution_prefix')
                self.fields.pop('reference')
                self.fields.pop('short_reference')
                self.fields.pop('short_name')
                self.fields.pop('long_name')
            elif not with_permission(permission=Permission.VIEW_PARTICIPANT_INST) and not t.pref('show_team_institutions'):
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

        if validated_data.get('short_reference') is None:
            validated_data['short_reference'] = validated_data.get('reference', '')[:34]

        speakers_data = validated_data.pop('speakers', [])
        break_categories = validated_data.pop('break_categories', [])
        venue_constraints = validated_data.pop('venue_constraints', [])

        emoji, code_name = pick_unused_emoji(validated_data['tournament'].id)
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
        save_related(SpeakerSerializer, speakers_data, self.context, {'team': team})
        save_related(VenueConstraintSerializer, venue_constraints, self.context, {'subject': team})

        if team.institution is not None:
            team.teaminstitutionconflict_set.get_or_create(institution=team.institution)

        return team

    def update(self, instance, validated_data):
        save_related(SpeakerSerializer, validated_data.pop('speakers', []), self.context, {'team': instance})
        save_related(VenueConstraintSerializer, validated_data.pop('venue_constraints', []), self.context, {'subject': instance})

        if self.partial:
            # Avoid removing conflicts if merely PATCHing
            validated_data['institution_conflicts'] = list(instance.institution_conflicts.all()) + validated_data.get('institution_conflicts', [])

        return super().update(instance, validated_data)


class InstitutionSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='api-global-institution-detail')
    region = fields.CreatableSlugRelatedField(slug_field='name', queryset=Region.objects.all(), required=False, allow_null=True)
    venue_constraints = VenueConstraintSerializer(many=True, required=False)

    class Meta:
        model = Institution
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not is_staff(kwargs.get('context')):
            with_permission = partial(has_permission, user=kwargs['context']['request'].user, tournament=kwargs['context']['tournament'])
            if not with_permission(permission=Permission.VIEW_ROOMCONSTRAINTS):
                self.fields.pop('venue_constraints')

    def create(self, validated_data):
        venue_constraints = validated_data.pop('venue_constraints', [])

        institution = super().create(validated_data)

        save_related(VenueConstraintSerializer, venue_constraints, self.context, {'subject': institution})

        return institution

    def update(self, instance, validated_data):
        save_related(VenueConstraintSerializer, validated_data.pop('venue_constraints', []), self.context, {'subject': instance})
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
            with_permission = partial(has_permission, user=kwargs['context']['request'].user, tournament=kwargs['context']['tournament'])
            if not with_permission(permission=Permission.VIEW_PARTICIPANT_INST):
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
    barcode = serializers.CharField(source='checkin_identifier.barcode', required=False, allow_null=True)
    _links = VenueLinksSerializer(source='*', read_only=True)

    class Meta:
        model = Venue
        exclude = ('tournament',)

    def create(self, validated_data):
        barcode = validated_data.pop('checkin_identifier', {}).get('barcode', None)
        venue = super().create(validated_data)

        if barcode:
            create_barcode(venue, barcode)

        return venue

    def update(self, instance, validated_data):
        handle_update_barcode(instance, validated_data)
        return super().update(instance, validated_data)


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
        side = fields.SideChoiceField(required=False)

        class Meta:
            model = DebateTeam
            fields = ('team', 'side')

        def save(self, **kwargs):
            seq = kwargs.pop('seq')
            if 'side' not in self.validated_data:
                self.validated_data['side'] = kwargs.get('side', seq)
            return super().save(**kwargs)

    class PairingLinksSerializer(serializers.Serializer):
        ballots = fields.RoundHyperlinkedIdentityField(
            view_name='api-ballot-list',
            lookup_field='pk', lookup_url_kwarg='debate_pk')

    url = fields.RoundHyperlinkedIdentityField(view_name='api-pairing-detail', lookup_url_kwarg='debate_pk')
    venue = fields.TournamentHyperlinkedRelatedField(view_name='api-venue-detail', queryset=Venue.objects.all(),
        required=False, allow_null=True)
    teams = DebateTeamSerializer(many=True, source='debateteam_set')
    adjudicators = DebateAdjudicatorSerializer(required=False, allow_null=True)

    barcode = serializers.CharField(source='checkin_identifier.barcode', required=False, allow_null=True)

    _links = PairingLinksSerializer(source='*', read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not is_staff(kwargs.get('context')):
            with_permission = partial(has_permission, user=kwargs['context']['request'].user, tournament=kwargs['context']['tournament'])
            if not with_permission(permission=Permission.VIEW_ADMIN_DRAW):
                self.fields.pop('bracket')
                self.fields.pop('room_rank')
                self.fields.pop('importance')
                self.fields.pop('result_status')

    class Meta:
        model = Debate
        exclude = ('round', 'flags')

    def create(self, validated_data):
        teams_data = validated_data.pop('debateteam_set', [])
        adjs_data = validated_data.pop('adjudicators', None)
        barcode = validated_data.pop('checkin_identifier', {}).get('barcode', None)

        validated_data['round'] = self.context['round']
        debate = super().create(validated_data)

        if barcode:
            create_barcode(debate, barcode)

        for i, team in enumerate(teams_data):
            save_related(self.DebateTeamSerializer, team, self.context, {'debate': debate, 'seq': i})

        if adjs_data is not None:
            save_related(DebateAdjudicatorSerializer, adjs_data, self.context, {'debate': debate})

        return debate

    def update(self, instance, validated_data):
        handle_update_barcode(instance, validated_data)
        for team in validated_data.pop('debateteam_set', []):
            try:
                DebateTeam.objects.update_or_create(debate=instance, side=team.get('side'), defaults={
                    'team': team.get('team'),
                })
            except (IntegrityError, TypeError) as e:
                raise serializers.ValidationError(e)

        if (adjs_data := validated_data.pop('adjudicators', None)) is not None:
            save_related(DebateAdjudicatorSerializer, adjs_data, self.context, {'debate': instance})

        return super().update(instance, validated_data)


class DrawGenerationSerializer(serializers.Serializer):
    class OptionsSerializer(serializers.Serializer):
        avoid_institution = serializers.BooleanField(required=False)
        avoid_history = serializers.BooleanField(required=False)
        history_penalty = serializers.IntegerField(required=False)
        institution_penalty = serializers.IntegerField(required=False)
        pullup_debates_penalty = serializers.IntegerField(required=False)
        side_penalty = serializers.IntegerField(required=False)
        pairing_penalty = serializers.IntegerField(required=False)
        side_allocations = serializers.ChoiceField(choices=DrawSideAllocations.choices, required=False, help_text=DrawSideAllocations.help_text)
        avoid_conflicts = serializers.ChoiceField(choices=DrawAvoidConflicts.choices, required=False, help_text=DrawAvoidConflicts.help_text)
        odd_bracket = serializers.ChoiceField(choices=DrawOddBracket.choices, required=False, help_text=DrawOddBracket.help_text)
        pairing_method = serializers.ChoiceField(choices=DrawPairingMethod.choices, required=False, help_text=DrawPairingMethod.help_text)
        pullup_restriction = serializers.ChoiceField(choices=DrawPullupRestriction.choices, required=False, help_text=DrawPullupRestriction.help_text)
        pullup = serializers.ChoiceField(choices=BPPullupDistribution.choices, required=False, help_text=BPPullupDistribution.help_text)
        position_cost = serializers.ChoiceField(choices=BPPositionCost.choices, required=False, help_text=BPPositionCost.help_text)
        assignment_method = serializers.ChoiceField(choices=BPAssignmentMethod.choices, required=False, help_text=BPAssignmentMethod.help_text)
        renyi_order = serializers.FloatField(required=False)
        exponent = serializers.FloatField(required=False)

    draw_type = serializers.ChoiceField(choices=Round.DrawType.choices, required=False, help_text=Round._meta.get_field('draw_type').help_text)
    options = OptionsSerializer(required=False, help_text="Options for draw generation; defaults to tournament preferences")

    def save(self, **kwargs):
        return DrawManager(self.context['round'], draw_type=self.validated_data.get('draw_type')).create(self.validated_data.get('options', {}))


class FeedbackQuestionSerializer(serializers.ModelSerializer):
    url = fields.TournamentHyperlinkedIdentityField(view_name='api-feedbackquestion-detail')

    class Meta:
        model = AdjudicatorFeedbackQuestion
        exclude = ('tournament',)

    validate_reference = partialmethod(_validate_field, 'reference')
    validate_seq = partialmethod(_validate_field, 'seq')


class FeedbackSerializer(serializers.ModelSerializer):

    class SubmitterSourceField(fields.BaseSourceField):
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
        answer = fields.AnyField()

        def validate(self, data):
            # Convert answer to correct type
            model = AdjudicatorFeedbackQuestion.ANSWER_TYPE_CLASSES[data['question'].answer_type]
            if type(data['answer']) != model.ANSWER_TYPE:
                raise serializers.ValidationError({'answer': 'The answer must be of type %s' % model.ANSWER_TYPE.__name__})

            data['answer'] = model.ANSWER_TYPE(data['answer'])

            option_error = serializers.ValidationError({'answer': 'Answer must be in set of options'})
            if len(data['question'].choices) > 0:
                if model.ANSWER_TYPE is list and len(set(data['answer']) - set(data['question'].choices)) > 0:
                    raise option_error
                if data['answer'] not in data['question'].choices:
                    raise option_error
            if (data['question'].min_value is not None and data['answer'] < data['question'].min_value) or (data['question'].max_value is not None and data['answer'] > data['question'].max_value):
                raise option_error

            return super().validate(data)

    url = fields.AdjudicatorFeedbackIdentityField(view_name='api-feedback-detail')
    adjudicator = fields.TournamentHyperlinkedRelatedField(view_name='api-adjudicator-detail', queryset=Adjudicator.objects.all())
    source = SubmitterSourceField(source='*')
    participant_submitter = fields.ParticipantSourceField(allow_null=True)
    debate = DebateHyperlinkedRelatedField(view_name='api-pairing-detail', queryset=Debate.objects.all(), lookup_url_kwarg='debate_pk')
    answers = FeedbackAnswerSerializer(many=True, source='get_answers', required=False)

    class Meta:
        model = AdjudicatorFeedback
        exclude = ('source_adjudicator', 'source_team')
        read_only_fields = ('timestamp', 'version',
            'submitter_type', 'participant_submitter', 'submitter',
            'confirmer', 'confirm_timestamp', 'ip_address', 'private_url')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not is_staff(kwargs.get('context')):
            self.fields.pop('ip_address')
            self.fields.pop('ignored')

    def validate(self, data):
        source = data.pop('source')
        debate = data.pop('debate')

        source_type = 'from_team' if isinstance(source, Team) else 'from_adj'
        required_questions = self.context['tournament'].adjudicatorfeedbackquestion_set.filter(required=True, **{source_type: True})
        answers = data.get('get_answers', [])

        if len(set(required_questions) - set(a['question'] for a in answers)) > 0:
            raise serializers.ValidationError("Answer to required question is missing")

        # Test answers for correct source
        for answer in answers:
            if not getattr(answer['question'], source_type, False):
                raise serializers.ValidationError("Question is not permitted from source.")

        # Test participants in debate
        if not data['adjudicator'].debateadjudicator_set.filter(debate=debate).exists():
            raise serializers.ValidationError("Target is not in debate")

        # Also move the source field into participant_specific fields
        participant = self.context['participant_requester']
        source_type = type(source)
        type_name = source_type.__name__.lower()
        if participant and getattr(participant, type_name, None) != source:
            raise PermissionDenied("Participant may only submit feedback from themselves")
        related_field = getattr(source, 'debate%s_set' % type_name)
        try:
            data['source_%s' % type_name] = related_field.get(debate=debate)
        except related_field.rel.related_model.DoesNotExist:
            raise serializers.ValidationError("Source is not in debate")

        return super().validate(data)

    def get_submitter_fields(self):
        participant = self.context['participant_requester']
        request = self.context['request']
        return {
            'participant_submitter': request.auth if participant else None,
            'submitter': participant or request.user,
            'submitter_type': Submission.Submitter.PUBLIC if participant else Submission.Submitter.TABROOM,
            'ip_address': get_ip_address(request),
        }

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


class BallotSerializer(serializers.ModelSerializer):

    class ResultSerializer(serializers.Serializer):
        class SheetSerializer(serializers.Serializer):

            class TeamResultSerializer(serializers.Serializer):
                side = fields.SideChoiceField(required=False)
                points = serializers.IntegerField(required=False)
                win = serializers.BooleanField(required=False)
                score = serializers.FloatField(required=False, allow_null=True)

                team = fields.TournamentHyperlinkedRelatedField(
                    view_name='api-team-detail',
                    queryset=Team.objects.all(),
                )

                class SpeechSerializer(serializers.Serializer):
                    class CriteriaSerializer(serializers.Serializer):
                        criterion = fields.TournamentHyperlinkedRelatedField(
                            view_name='api-score-criteria-detail',
                            queryset=ScoreCriterion.objects.all(),
                        )
                        score = serializers.FloatField()

                    ghost = serializers.BooleanField(required=False, help_text=SpeakerScore._meta.get_field('ghost').help_text)
                    score = serializers.FloatField()
                    rank = serializers.IntegerField(required=False)

                    speaker = fields.TournamentHyperlinkedRelatedField(
                        view_name='api-speaker-detail',
                        queryset=Speaker.objects.all(),
                        tournament_field='team__tournament',
                    )

                    criteria = CriteriaSerializer(required=False, many=True)

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
                        if kwargs.get('rank') is not None:
                            result.set_speaker_rank(*speaker_args, self.validated_data['rank'])
                        for criterion_score in self.validated_data.get('criteria', []):
                            result.set_criterion_score(*speaker_args, criterion_score.criterion, criterion_score.score)

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
                    side = self.validated_data.get('side', kwargs['seq'])

                    if result.scoresheet_class.uses_declared_winners and self.validated_data.get('win', False):
                        args = [side]
                        if kwargs.get('adjudicator') is not None and not result.ballotsub.single_adj:
                            args.insert(0, kwargs.get('adjudicator'))
                        result.add_winner(*args)

                    for i, speech in enumerate(self.validated_data.get('speeches', []), 1):
                        save_related(self.SpeechSerializer, speech, self.context, {
                            'result': result,
                            'side': side,
                            'seq': i,
                            'adjudicator': kwargs.get('adjudicator'),
                        })
                    return result

            teams = TeamResultSerializer(many=True)
            adjudicator = fields.TournamentHyperlinkedRelatedField(
                view_name='api-adjudicator-detail',
                queryset=Adjudicator.objects.all(),
                required=False, allow_null=True,
            )

            def validate_adjudicator(self, value):
                # Make sure adj is in debate
                if value and not self.context.get('debate').debateadjudicator_set.filter(adjudicator=value).exists():
                    raise serializers.ValidationError('Adjudicator must be in debate')
                return value

            def validate_teams(self, value):
                # Teams in their proper positions - this also checks having proper and consistent sides
                debate = self.context.get('debate')
                if len(value) != debate.debateteam_set.count():
                    raise serializers.ValidationError('Incorrect number of teams')
                for i, team in enumerate(value):
                    if debate.get_team(i) != team['team']:
                        raise serializers.ValidationError('Inconsistent team')
                return value

            def save(self, **kwargs):
                for i, team in enumerate(self.validated_data.get('teams', [])):
                    save_related(self.TeamResultSerializer, team, self.context, {
                        'result': kwargs['result'],
                        'adjudicator': self.validated_data.get('adjudicator'),
                        'seq': i,
                    })
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

            for sheet in validated_data['sheets']:
                save_related(self.SheetSerializer, sheet, self.context, {'result': result})

            try:
                result.save()
            except ResultError as e:
                raise serializers.ValidationError(str(e))

            return result

    class VetoSerializer(serializers.ModelSerializer):
        team = fields.TournamentHyperlinkedRelatedField(
            source='debate_team.team', view_name='api-team-detail', queryset=Team.objects.all())
        motion = fields.TournamentHyperlinkedRelatedField(view_name='api-motion-detail', queryset=Motion.objects.all())

        class Meta:
            model = DebateTeamMotionPreference
            exclude = ('id', 'ballot_submission', 'preference', 'debate_team')

        def create(self, validated_data):
            team = validated_data.pop('debate_team').pop('team')
            try:
                validated_data['debate_team'] = DebateTeam.objects.get(debate=self.context['debate'], team=team)
            except (DebateTeam.DoesNotExist, DebateTeam.MultipleObjectsReturned):
                raise serializers.ValidationError('Team is not in debate')
            return super().create(validated_data)

    result = ResultSerializer(source='result.get_result_info')
    motion = fields.TournamentHyperlinkedRelatedField(view_name='api-motion-detail', required=False, queryset=Motion.objects.all())
    url = fields.DebateHyperlinkedIdentityField(view_name='api-ballot-detail')
    participant_submitter = fields.ParticipantSourceField(allow_null=True, required=False)
    vetos = VetoSerializer(many=True, source='debateteammotionpreference_set', required=False, allow_null=True)

    class Meta:
        model = BallotSubmission
        exclude = ('debate',)
        read_only_fields = ('timestamp', 'version',
            'submitter_type', 'submitter', 'participant_submitter',
            'confirmer', 'confirm_timestamp', 'ip_address', 'private_url')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not is_staff(kwargs.get('context')):
            self.fields.pop('ip_address')

    def clean_confirmed(self, value):
        if value and self.context.get('participant_requester'):
            raise PermissionDenied("Public cannot confirm ballot")
        return value

    def get_submitter_fields(self):
        participant = self.context['participant_requester']
        request = self.context['request']
        if participant is not None and not self.context['debate'].debateadjudicator_set.filter(adjudicator_id=participant.id).exists():
            raise PermissionDenied('Authenticated adjudicator is not in debate')
        return {
            'participant_submitter': participant,
            'submitter': participant or request.user,
            'submitter_type': Submission.Submitter.PUBLIC if participant else Submission.Submitter.TABROOM,
            'ip_address': get_ip_address(request),
        }

    def create(self, validated_data):
        result_data = validated_data.pop('result').pop('get_result_info')
        veto_data = validated_data.pop('debateteammotionpreference_set', None)

        validated_data.update(self.get_submitter_fields())
        if validated_data.get('confirmed', False):
            validated_data['confirmer'] = self.context['request'].user
            validated_data['confirm_timestamp'] = timezone.now()

        stage = 'elim' if self.context['round'].stage == Round.Stage.ELIMINATION else 'prelim'
        if self.context['tournament'].pref('ballots_per_debate_' + stage) == 'per-adj':
            debateadj_count = self.context['debate'].debateadjudicator_set.exclude(type=DebateAdjudicator.TYPE_TRAINEE).count()
            if debateadj_count > 1:
                if len(result_data['sheets']) == 1:
                    validated_data['participant_submitter'] = result_data['sheets'][0].get('adjudicator', validated_data['participant_submitter'])
                    p_sub = validated_data['participant_submitter']
                    if self.context['participant_requester'] is not None and p_sub is not None and p_sub != self.context['participant_requester']:
                        raise PermissionDenied('Cannot submit single-adjudicator ballot for someone else')
                    validated_data['single_adj'] = True
                elif validated_data.get('single_adj', False):
                    raise serializers.ValidationError({'single_adj': 'Single-adjudicator ballots can only have one scoresheet'})
                elif len(result_data['sheets']) != debateadj_count:
                    raise serializers.ValidationError({
                        'result': 'Voting ballots must either have one scoresheet or ballots from all voting adjudicators',
                    })
        else:
            if len(result_data['sheets']) > 1:
                raise serializers.ValidationError({'result': 'Consensus ballots can only have one scoresheet'})
            validated_data['single_adj'] = self.context['tournament'].pref('individual_ballots')

        ballot = super().create(validated_data)

        save_related(self.ResultSerializer, result_data, self.context, {'ballot': ballot})

        if veto_data:
            save_related(self.VetoSerializer, veto_data, self.context, {'ballot_submission': ballot, 'preference': 3})

        return ballot

    def update(self, instance, validated_data):
        if validated_data['confirmed'] and not instance.confirmed:
            instance.confirmer = self.context['request'].user
            instance.confirm_timestamp = timezone.now()

        instance.confirmed = validated_data.get('confirmed', instance.confirmed)
        instance.discarded = validated_data.get('discarded', instance.discarded)
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
            save_related(DebateAdjudicatorSerializer, adjs_data, self.context, {'debate': debate})

        return debate

    def update(self, instance, validated_data):
        if validated_data.get('adjudicators', None) is not None:
            save_related(DebateAdjudicatorSerializer, validated_data.pop('adjudicators'), self.context, {'debate': instance})

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


class UserSerializer(serializers.ModelSerializer):

    class TournamentPermissionsSerializer(serializers.Serializer):
        tournament = serializers.HyperlinkedIdentityField(view_name='api-tournament-detail', lookup_field='slug', lookup_url_kwarg='tournament_slug')
        groups = fields.TournamentHyperlinkedRelatedField(many=True, view_name='api-group-detail', queryset=Group.objects.all(), default=[])
        permissions = serializers.ListField(child=serializers.ChoiceField(choices=Permission.choices), required=False)

    url = serializers.HyperlinkedIdentityField(view_name='api-user-detail')
    tournaments = TournamentPermissionsSerializer(many=True, required=False)

    class Meta:
        model = get_user_model()
        fields = ('id', 'url', 'username', 'password', 'is_superuser', 'is_staff', 'email', 'is_active', 'date_joined', 'last_login', 'tournaments')
        read_only_fields = ('date_joined', 'last_login')
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        user = self.Meta.model(**validated_data)
        user.set_password(validated_data['password'])
        user.save()

        return user


class GroupSerializer(serializers.ModelSerializer):
    url = fields.TournamentHyperlinkedIdentityField(view_name='api-group-detail')

    class Meta:
        model = Group
        exclude = ('tournament',)


class ScoreCriterionSerializer(serializers.ModelSerializer):
    url = fields.TournamentHyperlinkedIdentityField(view_name='api-score-criteria-detail')

    class Meta:
        model = ScoreCriterion
        exclude = ('tournament',)


class ParticipantIdentificationSerializer(serializers.ModelSerializer):
    class ParticipantIdField(fields.BaseSourceField):
        field_source_name = 'pk'
        models = {
            'api-speaker-detail': (Speaker, 'pk'),
            'api-adjudicator-detail': (Adjudicator, 'pk'),
        }

    url = ParticipantIdField()

    class Meta:
        model = Person
        fields = '__all__'


class FullRoundPairingSerializer(RoundPairingSerializer):
    confirmed_ballot = BallotSerializer()

    def create(self, validated_data):
        confirmed_ballot = validated_data.pop('confirmed_ballot', None)
        debate = super().create(validated_data)

        if confirmed_ballot is not None:
            save_related(BallotSerializer, confirmed_ballot, self.context, {'debate': debate})

        return debate


class FullRoundSerializer(RoundSerializer):
    pairings = FullRoundPairingSerializer(many=True, source='debate_set')
    preformed_panels = PreformedPanelSerializer(many=True, source='preformedpanel_set')

    def create(self, validated_data):
        pairings = validated_data.pop('debate_set', [])
        preformed_panels = validated_data.pop('preformedpanel_set', [])

        round = super().create(validated_data)

        save_related(FullRoundPairingSerializer, pairings, self.context, {'round': round})
        save_related(PreformedPanelSerializer, preformed_panels, self.context, {'round': round})

        return round


class FullAdjudicatorSerializer(AdjudicatorSerializer):
    feedback = FeedbackSerializer(many=True, source='adjudicatorfeedback_set')


class FullTournamentSerializer(TournamentSerializer):
    rounds = FullRoundSerializer(many=True, source='round_set')
    teams = TeamSerializer(many=True, source='team_set')
    adjudicators = FullAdjudicatorSerializer(many=True, source='adjudicator_set')
    break_categories = BreakCategorySerializer(many=True, source='breakcategory_set')
    speaker_categories = SpeakerCategorySerializer(many=True, source='speakercategory_set')
    venues = VenueSerializer(many=True, source='venue_set')
    venue_categories = VenueCategorySerializer(many=True, source='venuecategory_set')
    score_criteria = ScoreCriterionSerializer(many=True, source='scorecriterion_set')
    # institutions = InstitutionSerializer(many=True)
    # feedback_questions = FeedbackQuestionSerializer(many=True, source='question_set')
