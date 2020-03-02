from rest_framework import serializers

from breakqual.models import BreakCategory
from participants.emoji import pick_unused_emoji
from participants.models import Adjudicator, Institution, Speaker, SpeakerCategory, Team
from tournaments.models import Tournament

from .fields import SpeakerHyperlinkedIdentityField, TournamentHyperlinkedIdentityField, TournamentHyperlinkedRelatedField


class TournamentSerializer(serializers.ModelSerializer):

    url = serializers.HyperlinkedIdentityField(
        view_name='api-tournament-detail',
        lookup_field='slug', lookup_url_kwarg='tournament_slug')

    class TournamentLinksSerializer(serializers.Serializer):
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

    _links = TournamentLinksSerializer(source='*', read_only=True)

    class Meta:
        model = Tournament
        fields = ('name', 'short_name', 'slug', 'seq', 'active', 'url', '_links')


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
    speakers = SpeakerSerializer(many=True, required=False)
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
        fields = ('url', 'id', 'reference', 'code_name', 'emoji',
                  'institution', 'speakers', 'use_institution_prefix', 'break_categories')

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
        team.break_categories.set(BreakCategory.objects.filter(tournament=team.tournament, is_general=True))
        team.break_categories.add(*break_categories)

        speakers = SpeakerSerializer(many=True, data=speakers_data, context={'tournament': team.tournament})
        if speakers.is_valid():
            speakers.save(team=team)

        if team.institution is not None:
            team.teaminstitutionconflict_set.create(institution=team.institution)

        return team


class InstitutionSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='api-global-institution-detail')
    teams = TournamentHyperlinkedRelatedField(
        source='team_set',
        many=True,
        read_only=True,
        view_name='api-team-detail',
    )

    class Meta:
        model = Institution
        fields = ('url', 'id', 'name', 'code', 'teams')
