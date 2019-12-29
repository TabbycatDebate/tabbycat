from rest_framework import serializers

from breakqual.models import BreakCategory
from participants.models import Speaker, SpeakerCategory
from tournaments.models import Tournament

from .fields import TournamentHyperlinkedIdentityField


class TournamentAtRootSerializer(serializers.HyperlinkedModelSerializer):

    url = serializers.HyperlinkedIdentityField(
        view_name='api-tournament-detail',
        lookup_field='slug', lookup_url_kwarg='tournament_slug')

    class Meta:
        model = Tournament
        fields = ('name', 'short_name', 'slug', 'url', 'active')


class TournamentEndpointsSerializer(serializers.Serializer):

    break_categories = serializers.HyperlinkedIdentityField(
        view_name='api-breakcategory-list',
        lookup_field='slug', lookup_url_kwarg='tournament_slug')
    speaker_categories = serializers.HyperlinkedIdentityField(
        view_name='api-speakercategory-list',
        lookup_field='slug', lookup_url_kwarg='tournament_slug')


class TournamentSerializer(serializers.ModelSerializer):

    urls = TournamentEndpointsSerializer(source='*', read_only=True)

    class Meta:
        model = Tournament
        fields = ('name', 'short_name', 'slug', 'seq', 'active', 'urls')


class BreakCategoryEndpointsSerializer(serializers.Serializer):

    eligibility = TournamentHyperlinkedIdentityField(
        view_name='api-breakcategory-eligibility', lookup_field='slug')


class BreakCategorySerializer(serializers.ModelSerializer):

    url = TournamentHyperlinkedIdentityField(
        view_name='api-breakcategory-detail', lookup_field='slug')
    urls = BreakCategoryEndpointsSerializer(source='*', read_only=True)

    class Meta:
        model = BreakCategory
        fields = ('name', 'slug', 'seq', 'break_size', 'is_general', 'priority',
                  'limit', 'rule', 'url', 'urls')


class SpeakerCategoryEndpointsSerializer(serializers.Serializer):

    eligibility = TournamentHyperlinkedIdentityField(
        view_name='api-speakercategory-eligibility', lookup_field='slug')


class SpeakerCategorySerializer(serializers.ModelSerializer):

    url = TournamentHyperlinkedIdentityField(
        view_name='api-speakercategory-detail', lookup_field='slug')
    urls = SpeakerCategoryEndpointsSerializer(source='*', read_only=True)

    class Meta:
        model = SpeakerCategory
        fields = ('name', 'slug', 'seq', 'limit', 'public', 'url', 'urls')


class BreakEligibilitySerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['team_set'] = serializers.PrimaryKeyRelatedField(
            many=True,
            queryset=kwargs['context']['tournament'].team_set.all()
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
            queryset=Speaker.objects.filter(team__tournament=kwargs['context']['tournament'])
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
