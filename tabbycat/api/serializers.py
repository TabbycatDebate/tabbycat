from rest_framework import serializers

from breakqual.models import BreakCategory
from draw.models import Debate, DebateTeam
from participants.emoji import pick_unused_emoji
from participants.models import Adjudicator, Institution, Speaker, SpeakerCategory, Team
from tournaments.models import Round, Tournament
from venues.models import Venue, VenueCategory

from .fields import (AnonymisingHyperlinkedTournamentRelatedField, RoundHyperlinkedIdentityField, SpeakerHyperlinkedIdentityField,
    TournamentHyperlinkedIdentityField, TournamentHyperlinkedRelatedField)


class TournamentSerializer(serializers.ModelSerializer):

    url = serializers.HyperlinkedIdentityField(
        view_name='api-tournament-detail',
        lookup_field='slug', lookup_url_kwarg='tournament_slug')

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

    _links = TournamentLinksSerializer(source='*', read_only=True)

    class Meta:
        model = Tournament
        fields = '__all__'


class RoundSerializer(serializers.ModelSerializer):
    tournament = serializers.HyperlinkedRelatedField(
        view_name='api-tournament-detail',
        lookup_field='slug', lookup_url_kwarg='tournament_slug',
        queryset=Tournament.objects.all(),
    )
    url = TournamentHyperlinkedIdentityField(
        view_name='api-round-detail',
        lookup_field='seq', lookup_url_kwarg='round_seq')
    break_category = TournamentHyperlinkedRelatedField(
        view_name='api-breakcategory-detail',
        queryset=BreakCategory.objects.all())

    class RoundLinksSerializer(serializers.Serializer):
        pairing = TournamentHyperlinkedIdentityField(
            view_name='api-pairing-list',
            lookup_field='seq', lookup_url_kwarg='round_seq')

    _links = RoundLinksSerializer(source='*', read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not kwargs['context']['request'].user.is_staff:
            self.fields.pop('feedback_weight')

    class Meta:
        model = Round
        fields = '__all__'


class BreakCategorySerializer(serializers.ModelSerializer):

    class BreakCategoryLinksSerializer(serializers.Serializer):
        eligibility = TournamentHyperlinkedIdentityField(
            view_name='api-breakcategory-eligibility')

    url = TournamentHyperlinkedIdentityField(
        view_name='api-breakcategory-detail')

    _links = BreakCategoryLinksSerializer(source='*', read_only=True)

    class Meta:
        model = BreakCategory
        fields = ('name', 'slug', 'seq', 'break_size', 'is_general', 'priority',
                  'limit', 'rule', 'url', '_links')


class SpeakerCategorySerializer(serializers.ModelSerializer):

    class SpeakerCategoryLinksSerializer(serializers.Serializer):
        eligibility = TournamentHyperlinkedIdentityField(
            view_name='api-speakercategory-eligibility', lookup_field='pk')

    url = TournamentHyperlinkedIdentityField(
        view_name='api-speakercategory-detail', lookup_field='pk')
    _links = SpeakerCategoryLinksSerializer(source='*', read_only=True)

    class Meta:
        model = SpeakerCategory
        fields = ('name', 'slug', 'seq', 'limit', 'public', 'url', '_links')


class BreakEligibilitySerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['team_set'] = serializers.PrimaryKeyRelatedField(
            many=True,
            queryset=kwargs['context']['tournament'].team_set.all(),
        )

    class Meta:
        model = BreakCategory
        fields = ('slug', 'team_set')

    def update(self, instance, validated_data):
        teams = validated_data['team_set']

        if self.partial:
            # Add teams to category, don't remove any
            self.instance.team_set.add(*teams)
        else:
            self.instance.team_set.set(teams)
        return self.instance


class SpeakerEligibilitySerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['speaker_set'] = serializers.PrimaryKeyRelatedField(
            many=True,
            queryset=Speaker.objects.filter(team__tournament=kwargs['context']['tournament']),
        )

    class Meta:
        model = SpeakerCategory
        fields = ('slug', 'speaker_set')

    def update(self, instance, validated_data):
        speakers = validated_data['speaker_set']

        if self.partial:
            # Add speakers to category, don't remove any
            self.instance.speaker_set.add(*speakers)
        else:
            self.instance.speaker_set.set(speakers)
        return self.instance


class SpeakerSerializer(serializers.ModelSerializer):
    url = SpeakerHyperlinkedIdentityField(view_name='api-speaker-detail')
    categories = TournamentHyperlinkedRelatedField(
        many=True,
        view_name='api-speakercategory-detail',
        queryset=SpeakerCategory.objects.all(),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        if not kwargs['context']['request'].user.is_staff:
            self.fields.pop('gender')
            self.fields.pop('email')
            self.fields.pop('phone')
            self.fields.pop('pronoun')
            self.fields.pop('anonymous')

    class Meta:
        model = Speaker
        fields = ('url', 'id', 'name', 'gender', 'email', 'phone', 'anonymous', 'pronoun',
                  'categories')

    def create(self, validated_data):
        speaker_categories = validated_data.pop("categories")
        speaker = super().create(validated_data)
        speaker.categories.set(speaker_categories)
        return speaker


class AdjudicatorSerializer(serializers.ModelSerializer):
    url = TournamentHyperlinkedIdentityField(view_name='api-adjudicator-detail')
    institution = serializers.HyperlinkedRelatedField(
        allow_null=True,
        view_name='api-global-institution-detail',
        queryset=Institution.objects.all(),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Remove private fields in the public endpoint if needed
        if not kwargs['context']['request'].user.is_staff:
            t = kwargs['context']['tournament']
            if not t.pref('show_adjudicator_institutions'):
                self.fields.pop('institution')

            self.fields.pop('base_score')
            self.fields.pop('trainee')
            self.fields.pop('gender')
            self.fields.pop('email')
            self.fields.pop('phone')
            self.fields.pop('pronoun')
            self.fields.pop('anonymous')

    class Meta:
        model = Adjudicator
        fields = ('url', 'id', 'name', 'gender', 'email', 'phone', 'anonymous', 'pronoun',
                  'institution', 'base_score', 'trainee', 'independent', 'adj_core')

    def create(self, validated_data):
        adj = super().create(validated_data)

        if adj.institution is not None:
            adj.adjudicatorinstitutionconflict_set.create(institution=adj.institution)

        return adj


class TeamSerializer(serializers.ModelSerializer):
    url = TournamentHyperlinkedIdentityField(view_name='api-team-detail')
    institution = serializers.HyperlinkedRelatedField(
        allow_null=True,
        view_name='api-global-institution-detail',
        queryset=Institution.objects.all(),
    )
    break_categories = TournamentHyperlinkedRelatedField(
        many=True,
        view_name='api-breakcategory-detail',
        queryset=BreakCategory.objects.all(),
    )

    class Meta:
        model = Team
        fields = ('url', 'id', 'reference', 'code_name', 'emoji', 'short_name', 'long_name',
                  'institution', 'speakers', 'use_institution_prefix', 'break_categories')

    def __init__(self, *args, **kwargs):
        self.fields['speakers'] = SpeakerSerializer(*args, many=True, required=False, **kwargs)

        super().__init__(*args, **kwargs)

        # Remove private fields in the public endpoint if needed
        if not kwargs['context']['request'].user.is_staff:
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

    def create(self, validated_data):
        """Four things must be done, excluding saving the Team object:
        1. Create the short_reference based on 'reference',
        2. Create emoji/code name if not stated,
        3. Create the speakers.
        4. Add institution conflict"""
        validated_data['short_reference'] = validated_data['reference'][:34]
        speakers_data = validated_data.pop('speakers')
        break_categories = validated_data.pop('break_categories')
        emoji, code_name = pick_unused_emoji()
        if 'emoji' not in validated_data:
            validated_data['emoji'] = emoji
        if 'code_name' not in validated_data:
            validated_data['code_name'] = code_name

        team = super().create(validated_data)
        team.break_categories.set(
            list(BreakCategory.objects.filter(tournament=team.tournament, is_general=True)) + break_categories,
        )

        # The data is passed to the sub-serializer so that it handles categories
        speakers = SpeakerSerializer(many=True, context={'tournament': team.tournament})
        speakers._validated_data = speakers_data  # Data was already validated
        speakers.save(team=team)

        if team.institution is not None:
            team.teaminstitutionconflict_set.create(institution=team.institution)

        return team


class InstitutionSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='api-global-institution-detail')
    teams = TournamentHyperlinkedRelatedField(
        source='team_set',
        many=True,
        view_name='api-team-detail',
    )
    adjudicators = TournamentHyperlinkedRelatedField(
        source='adjudicator_set',
        many=True,
        view_name='api-adjudicator-detail',
    )

    class Meta:
        model = Institution
        fields = ('url', 'id', 'name', 'code', 'teams', 'adjudicators')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not kwargs['context']['request'].user.is_staff:
            self.fields.pop('teams')
            self.fields.pop('adjudicators')


class VenueSerializer(serializers.ModelSerializer):
    url = TournamentHyperlinkedIdentityField(view_name='api-venue-detail')
    categories = TournamentHyperlinkedRelatedField(
        source='venuecategory_set',
        many=True,
        view_name='api-venuecategory-detail',
    )
    display_name = serializers.ReadOnlyField()

    class Meta:
        model = Venue
        fields = '__all__'


class VenueCategorySerializer(serializers.ModelSerializer):
    url = TournamentHyperlinkedIdentityField(view_name='api-venuecategory-detail')
    venues = TournamentHyperlinkedRelatedField(
        many=True,
        view_name='api-venue-detail',
    )

    class Meta:
        model = VenueCategory
        fields = '__all__'


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
    team = TournamentHyperlinkedRelatedField(view_name='api-team-detail')


class SpeakerStandingsSerializer(BaseStandingsSerializer):
    speaker = AnonymisingHyperlinkedTournamentRelatedField(view_name='api-speaker-detail', anonymous_source='anonymous')


class RoundPairingSerializer(serializers.ModelSerializer):
    class DebateTeamSerializer(serializers.ModelSerializer):
        team = TournamentHyperlinkedRelatedField(view_name='api-team-detail')
        side = serializers.CharField()

        class Meta:
            model = DebateTeam
            fields = ('team', 'side')

    class DebateAdjudicatorSerializer(serializers.Serializer):
        chair = TournamentHyperlinkedRelatedField(view_name='api-adjudicator-detail')
        panellists = TournamentHyperlinkedRelatedField(many=True, view_name='api-adjudicator-detail')
        trainees = TournamentHyperlinkedRelatedField(many=True, view_name='api-adjudicator-detail')

    url = RoundHyperlinkedIdentityField(view_name='api-pairing-detail')
    venue = TournamentHyperlinkedRelatedField(view_name='api-venue-detail')
    teams = DebateTeamSerializer(many=True, source='debateteam_set')
    adjudicators = DebateAdjudicatorSerializer()

    class Meta:
        model = Debate
        fields = ('url', 'id', 'venue', 'teams', 'adjudicators', 'sides_confirmed')
