from urllib import parse

from django.db import IntegrityError
from django.db.models import QuerySet
from django.urls import get_script_prefix, resolve, Resolver404
from django.utils import timezone
from django.utils.encoding import uri_to_iri
from rest_framework import serializers
from rest_framework.relations import Hyperlink

from adjallocation.models import DebateAdjudicator
from adjfeedback.models import AdjudicatorFeedback, AdjudicatorFeedbackQuestion
from breakqual.models import BreakCategory, BreakingTeam
from draw.models import Debate, DebateTeam
from motions.models import Motion
from participants.emoji import pick_unused_emoji
from participants.models import Adjudicator, Institution, Region, Speaker, SpeakerCategory, Team
from privateurls.utils import populate_url_keys
from results.mixins import TabroomSubmissionFieldsMixin
from results.models import BallotSubmission
from results.result import DebateResult
from tournaments.models import Round, Tournament
from venues.models import Venue, VenueCategory

from . import fields


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
    class RoundMotionsSerializer(serializers.ModelSerializer):
        url = fields.MotionHyperlinkedIdentityField(view_name='api-motion-detail')

        class Meta:
            model = Motion
            exclude = ('round',)

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
    motions = RoundMotionsSerializer(many=True, source='motion_set')

    _links = RoundLinksSerializer(source='*', read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not kwargs['context']['request'].user.is_staff:
            self.fields.pop('feedback_weight')

            # Can't show in a ListSerializer
            if isinstance(self.instance, QuerySet) or not self.instance.motions_released:
                self.fields.pop('motions')

    class Meta:
        model = Round
        exclude = ('tournament',)

    def validate(self, data):
        if (data.get('break_category') is None) == (data.get('stage', Round.STAGE_ELIMINATION) == Round.STAGE_ELIMINATION):
            # break category is None _XNOR_ stage is elimination
            raise serializers.ValidationError("Rounds are elimination iff they have a break category.")
        return super().validate(data)

    def create(self, validated_data):
        motions_data = validated_data.pop('motion_set')
        round = super().create(validated_data)

        if len(motions_data) > 0:
            motions = self.RoundMotionsSerializer(many=True, context=self.context)
            motions._validated_data = motions_data  # Data was already validated
            motions.save(round=round)

        return round

    def update(self, instance, validated_data):
        motions_data = validated_data.pop('motion_set')
        for motion in motions_data:
            try:
                Motion.objects.update_or_create(round=instance, seq=motion.get('seq'), defaults={
                    'text': motion.get('text'),
                    'reference': motion.get('reference'),
                    'info_slide': motion.get('info_slide'),
                })
            except (IntegrityError, TypeError) as e:
                raise serializers.ValidationError(e)
        return super().update(instance, validated_data)


class MotionSerializer(serializers.ModelSerializer):
    class RoundsSerializer(serializers.ModelSerializer):
        round = fields.TournamentHyperlinkedRelatedField(view_name='api-round-detail',
            lookup_field='seq', lookup_url_kwarg='round_seq',
            queryset=Round.objects.all())

        class Meta:
            model = Motion
            fields = ('round', 'seq')

    url = fields.MotionHyperlinkedIdentityField(view_name='api-motion-detail')
    rounds = RoundsSerializer(many=True, source='as_iterable')

    class Meta:
        model = Motion
        exclude = ('round', 'seq')

    def validate(self, data):
        """While the fields for the rounds is within a nested serializer,
        as there isn't already a many-to-many relationship, there will
        always only be one value. This method modifies validated_data in
        place to directly have the fields from the nested serializer."""
        rounds = data.pop('as_iterable')
        data['round'] = rounds[0].get('round')
        data['seq'] = rounds[0].get('seq')
        return data


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
        fields = ('name', 'slug', 'seq', 'break_size', 'is_general', 'priority',
                  'limit', 'rule', 'url', '_links')


class SpeakerCategorySerializer(serializers.ModelSerializer):

    class SpeakerCategoryLinksSerializer(serializers.Serializer):
        eligibility = fields.TournamentHyperlinkedIdentityField(
            view_name='api-speakercategory-eligibility', lookup_field='pk')

    url = fields.TournamentHyperlinkedIdentityField(
        view_name='api-speakercategory-detail', lookup_field='pk')
    _links = SpeakerCategoryLinksSerializer(source='*', read_only=True)

    class Meta:
        model = SpeakerCategory
        fields = ('name', 'slug', 'seq', 'limit', 'public', 'url', '_links')


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

    class LinksSerializer(serializers.Serializer):
        checkin = fields.TournamentHyperlinkedIdentityField(tournament_field='team__tournament', view_name='api-speaker-checkin')

    url = fields.TournamentHyperlinkedIdentityField(tournament_field='team__tournament', view_name='api-speaker-detail')
    team = fields.TournamentHyperlinkedRelatedField(view_name='api-team-detail', queryset=Team.objects.all())
    categories = fields.TournamentHyperlinkedRelatedField(
        many=True,
        view_name='api-speakercategory-detail',
        queryset=SpeakerCategory.objects.all(),
    )
    _links = LinksSerializer(source='*', read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not kwargs['context']['request'].user.is_staff:
            self.fields.pop('gender')
            self.fields.pop('email')
            self.fields.pop('phone')
            self.fields.pop('pronoun')
            self.fields.pop('anonymous')
            self.fields.pop('url_key')

    class Meta:
        model = Speaker
        fields = ('url', 'id', 'name', 'gender', 'email', 'phone', 'anonymous', 'pronoun',
                  'categories', 'url_key', '_links', 'team')

    def create(self, validated_data):
        url_key = validated_data.pop('url_key', None)
        if url_key is not None and len(url_key) != 0:  # Let an empty string be null for the uniqueness constraint
            validated_data['url_key'] = url_key

        speaker = super().create(validated_data)

        if url_key is None:
            populate_url_keys([speaker])

        return speaker


class AdjudicatorSerializer(serializers.ModelSerializer):

    class LinksSerializer(serializers.Serializer):
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
    _links = LinksSerializer(source='*', read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Remove private fields in the public endpoint if needed
        if not kwargs['context']['request'].user.is_staff:
            self.fields.pop('institution_conflicts')
            self.fields.pop('team_conflicts')
            self.fields.pop('adjudicator_conflicts')

            t = kwargs['context']['tournament']
            if not t.pref('show_adjudicator_institutions'):
                self.fields.pop('institution')
            if not t.pref('public_breaking_adjs'):
                self.fields.pop('breaking')

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
        fields = ('url', 'id', 'name', 'gender', 'email', 'phone', 'anonymous', 'pronoun',
                  'institution', 'base_score', 'breaking', 'trainee', 'independent', 'adj_core',
                  'institution_conflicts', 'team_conflicts', 'adjudicator_conflicts', 'url_key', '_links')

    def create(self, validated_data):
        url_key = validated_data.pop('url_key', None)
        if url_key is not None and len(url_key) != 0:  # Let an empty string be null for the uniqueness constraint
            validated_data['url_key'] = url_key

        adj = super().create(validated_data)

        if url_key is None:  # If explicitly null (and not just an empty string)
            populate_url_keys([adj])

        if adj.institution is not None:
            adj.adjudicatorinstitutionconflict_set.get_or_create(institution=adj.institution)

        return adj


class TeamSerializer(serializers.ModelSerializer):
    class TeamSpeakerSerializer(SpeakerSerializer):
        class Meta(SpeakerSerializer.Meta):
            fields = ('url', 'id', 'name', 'gender', 'email', 'phone', 'anonymous', 'pronoun',
                      'categories', 'url_key', '_links')

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

    class Meta:
        model = Team
        fields = ('url', 'id', 'reference', 'short_reference', 'code_name', 'emoji', 'short_name', 'long_name',
                  'institution', 'speakers', 'use_institution_prefix', 'break_categories',
                  'institution_conflicts')

    def __init__(self, *args, **kwargs):
        self.fields['speakers'] = self.TeamSpeakerSerializer(*args, many=True, required=False, **kwargs)

        super().__init__(*args, **kwargs)

        # Remove private fields in the public endpoint if needed
        if not kwargs['context']['request'].user.is_staff:
            self.fields.pop('institution_conflicts')

            t = kwargs['context']['tournament']
            if t.pref('team_code_names') in ('admin-tooltips-code', 'admin-tooltips-real', 'everywhere'):
                self.fields.pop('institution')
                self.fields.pop('use_institution_prefix')
                self.fields.pop('reference')
                self.fields.pop('short_name')
                self.fields.pop('long_name')
            elif not t.pref('show_team_institutions'):
                self.fields.pop('institution')
                self.fields.pop('use_institution_prefix')
            if not t.pref('public_break_categories'):
                self.fields.pop('break_categories')

    def validate(self, data):
        if data.get('use_institution_prefix', False) and data.get('institution') is None:
            raise serializers.ValidationError("Cannot include institution prefix without institution.")
        return super().validate(data)

    def create(self, validated_data):
        """Four things must be done, excluding saving the Team object:
        1. Create the short_reference based on 'reference',
        2. Create emoji/code name if not stated,
        3. Create the speakers.
        4. Add institution conflict"""

        if len(validated_data['short_reference']) == 0:
            validated_data['short_reference'] = validated_data['reference'][:34]

        speakers_data = validated_data.pop('speakers')
        break_categories = validated_data.pop('break_categories')

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

        if team.institution is not None:
            team.teaminstitutionconflict_set.get_or_create(institution=team.institution)

        return team

    def update(self, instance, validated_data):
        speakers_data = validated_data.pop('speakers')
        if len(speakers_data) > 0:
            speakers = SpeakerSerializer(many=True, context=self.context)
            speakers._validated_data = speakers_data  # Data was already validated
            speakers.save(team=instance)

        return super().update(instance, validated_data)


class InstitutionSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='api-global-institution-detail')
    region = fields.CreatableSlugRelatedField(slug_field='name', queryset=Region.objects.all(), required=False)

    class Meta:
        model = Institution
        fields = '__all__'


class PerTournamentInstitutionSerializer(InstitutionSerializer):
    teams = fields.TournamentHyperlinkedRelatedField(
        source='team_set',
        many=True,
        view_name='api-team-detail',
    )
    adjudicators = fields.TournamentHyperlinkedRelatedField(
        source='adjudicator_set',
        many=True,
        view_name='api-adjudicator-detail',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not kwargs['context']['request'].user.is_staff:
            self.fields.pop('teams')
            self.fields.pop('adjudicators')


class VenueSerializer(serializers.ModelSerializer):

    class LinksSerializer(serializers.Serializer):
        checkin = fields.TournamentHyperlinkedIdentityField(view_name='api-venue-checkin')

    url = fields.TournamentHyperlinkedIdentityField(view_name='api-venue-detail')
    categories = fields.TournamentHyperlinkedRelatedField(
        source='venuecategory_set', many=True,
        view_name='api-venuecategory-detail',
        queryset=VenueCategory.objects.all(),
    )
    display_name = serializers.ReadOnlyField()
    external_url = serializers.URLField(source='url', required=False, allow_blank=True)
    _links = LinksSerializer(source='*', read_only=True)

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


class BaseStandingsSerializer(serializers.Serializer):
    rank = serializers.SerializerMethodField()
    tied = serializers.SerializerMethodField()
    metrics = serializers.SerializerMethodField()

    def get_rank(self, obj):
        return obj.rankings['rank'][0]

    def get_tied(self, obj):
        return obj.rankings['rank'][1]

    def get_metrics(self, obj):
        return [{'metric': s, 'value': v} for s, v in obj.metrics.items()]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TeamStandingsSerializer(BaseStandingsSerializer):
    team = fields.TournamentHyperlinkedRelatedField(view_name='api-team-detail', queryset=Team.objects.all())


class SpeakerStandingsSerializer(BaseStandingsSerializer):
    speaker = fields.AnonymisingHyperlinkedTournamentRelatedField(view_name='api-speaker-detail', anonymous_source='anonymous')


class RoundPairingSerializer(serializers.ModelSerializer):
    class DebateTeamSerializer(serializers.ModelSerializer):
        team = fields.TournamentHyperlinkedRelatedField(view_name='api-team-detail', queryset=Team.objects.all())

        class Meta:
            model = DebateTeam
            fields = ('team', 'side')

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

    url = fields.RoundHyperlinkedIdentityField(view_name='api-pairing-detail', lookup_url_kwarg='debate_pk')
    venue = fields.TournamentHyperlinkedRelatedField(view_name='api-venue-detail', queryset=Venue.objects.all())
    teams = DebateTeamSerializer(many=True, source='debateteam_set')
    adjudicators = DebateAdjudicatorSerializer()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not kwargs['context']['request'].user.is_staff:
            self.fields.pop('bracket')
            self.fields.pop('room_rank')
            self.fields.pop('importance')
            self.fields.pop('result_status')

    class Meta:
        model = Debate
        exclude = ('round', 'flags')

    def create(self, validated_data):
        teams_data = validated_data.pop('debateteam_set')
        adjs_data = validated_data.pop('adjudicators')

        validated_data['round'] = self.context['round']
        debate = super().create(validated_data)

        teams = self.DebateTeamSerializer(many=True)
        teams._validated_data = teams_data  # Data was already validated
        teams.save(debate=debate)

        adjudicators = self.DebateAdjudicatorSerializer()
        adjudicators._validated_data = adjs_data
        adjudicators.save(debate=debate)

        return debate

    def update(self, instance, validated_data):
        for team in validated_data.pop('debateteam_set'):
            try:
                DebateTeam.objects.update_or_create(debate=instance, side=team.get('side'), defaults={
                    'team': team.get('team'),
                })
            except (IntegrityError, TypeError) as e:
                raise serializers.ValidationError(e)

        adjudicators = self.DebateAdjudicatorSerializer()
        adjudicators._validated_data = validated_data.pop('adjudicators')
        adjudicators.save(debate=instance)

        return super().update(instance, validated_data)


class FeedbackQuestionSerializer(serializers.ModelSerializer):
    url = fields.TournamentHyperlinkedIdentityField(view_name='api-feedbackquestion-detail')

    class Meta:
        model = AdjudicatorFeedbackQuestion
        exclude = ('tournament',)


class FeedbackSerializer(TabroomSubmissionFieldsMixin, serializers.ModelSerializer):

    class SourceField(fields.TournamentHyperlinkedRelatedField):
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
            if value.source_adjudicator is not None:
                url = self.get_url(value.source_adjudicator.adjudicator, 'api-adjudicator-detail', self.context['request'], format)
            elif value.source_team is not None:
                url = self.get_url(value.source_team.team, 'api-team-detail', self.context['request'], format)

            if url is None:
                return None

            return Hyperlink(url, value)

        def to_internal_value(self, data):
            self.source_attrs = ['source']  # Must set

            # Was the value already entered?
            if isinstance(data, Adjudicator) or isinstance(data, Team):
                return data

            try:
                http_prefix = data.startswith(('http:', 'https:'))
            except AttributeError:
                self.fail('incorrect_type', data_type=type(data).__name__)

            if http_prefix:
                # If needed convert absolute URLs to relative path
                data = parse.urlparse(data).path
                prefix = get_script_prefix()
                if data.startswith(prefix):
                    data = '/' + data[len(prefix):]

            data = uri_to_iri(data)
            try:
                match = resolve(data)
            except Resolver404:
                self.fail('no_match')

            self.model = {
                'api-adjudicator-detail': Adjudicator,
                'api-team-detail': Team,
            }[match.view_name]

            try:
                return self.get_object(match.view_name, match.args, match.kwargs)
            except self.model.DoesNotExist:
                self.fail('does_not_exist')

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
    source = SourceField(source='*')
    debate = DebateHyperlinkedRelatedField(view_name='api-pairing-detail', queryset=Debate.objects.all())
    answers = FeedbackAnswerSerializer(many=True, source='get_answers', required=False)

    class Meta:
        model = AdjudicatorFeedback
        exclude = ('source_adjudicator', 'source_team')
        read_only_fields = ('timestamp', 'version', 'submitter_type', 'submitter', 'confirmer', 'confirm_timestamp', 'ip_address')

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
                side = serializers.CharField()
                points = serializers.IntegerField(required=False)
                win = serializers.BooleanField(required=False)
                score = serializers.FloatField(required=False)

                team = fields.TournamentHyperlinkedRelatedField(
                    view_name='api-team-detail',
                    queryset=Team.objects.all(),
                )

                class SpeechSerializer(serializers.Serializer):
                    ghost = serializers.BooleanField(required=False)
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
                    speeches = data.get('speeches', None)
                    if speeches is None:
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

            def validate(self, data):
                # Make sure adj is in debate
                adj = data.get('adjudicator', None)
                debate = self.context.get('debate')
                if adj is not None and not debate.debateadjudicator_set.filter(adjudicator=adj).exists():
                    raise serializers.ValidationError('Adjudicator must be in debate')

                # Teams in their proper positions - this also checks having proper and consistent sides
                teams = data.get('teams', {})
                if len(teams) != debate.debateteam_set.count():
                    raise serializers.ValidationError('Incorrect number of teams')
                for team in teams:
                    if debate.get_team(team['side']) != team['team']:
                        raise serializers.ValidationError('Inconsistent team')

                return data

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

    result = ResultSerializer(source='result.get_result_info')
    motion = fields.MotionHyperlinkedRelatedField(view_name='api-motion-detail', required=False, tournament_field='round__tournament',
        queryset=Motion.objects.all())
    url = fields.DebateHyperlinkedIdentityField(view_name='api-ballot-detail')

    class Meta:
        model = BallotSubmission
        exclude = ('debate',)
        read_only_fields = ('timestamp', 'version', 'submitter_type', 'submitter', 'confirmer', 'confirm_timestamp', 'ip_address')

    def get_request(self):
        return self.context['request']

    def create(self, validated_data):
        result_data = validated_data.pop('result').pop('get_result_info')
        validated_data.update(self.get_submitter_fields())
        if validated_data.get('confirmed', False):
            validated_data['confirmer'] = self.context['request'].user
            validated_data['confirm_timestamp'] = timezone.now()

        ballot = super().create(validated_data)

        result = self.ResultSerializer(context=self.context)
        result._validated_data = result_data
        result._errors = []
        result.save(ballot=ballot)

        return ballot

    def update(self, instance, validated_data):
        if validated_data['confirmed'] and not instance.confirmed:
            validated_data['confirmer'] = self.context['request'].user
            validated_data['confirm_timestamp'] = timezone.now()

        instance.confirmed = validated_data['confirmed']
        instance.discarded = validated_data['discarded']
        instance.ignored = validated_data['ignored']
        instance.save()
