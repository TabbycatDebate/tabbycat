from rest_framework import serializers

from .models import Adjudicator, Institution, Region, Team


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

    class Meta:
        model = Team
        fields = ('id', 'short_name', 'long_name', 'institution')

    institution = InstitutionSerializer()
