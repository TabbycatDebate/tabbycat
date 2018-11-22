from rest_framework import serializers

from .models import Adjudicator, Institution, Region, Speaker, Team


class SpeakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Speaker
        fields = ('id', 'name', 'gender')


class InstitutionSerializer(serializers.ModelSerializer):
    region = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Institution
        fields = ('id', 'name', 'code', 'region')


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ('id', 'name')


class AdjudicatorSerializer(serializers.ModelSerializer):
    institution = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Adjudicator
        fields = ('id', 'name', 'gender', 'institution',)


class TeamSerializer(serializers.ModelSerializer):
    institution = serializers.PrimaryKeyRelatedField(read_only=True)
    speakers = SpeakerSerializer(read_only=True, many=True)
    points = serializers.SerializerMethodField(read_only=True)

    def get_points(self, obj):
        return obj.points_count

    class Meta:
        model = Team
        fields = ('id', 'short_name', 'long_name', 'points',
                  'institution', 'speakers')
