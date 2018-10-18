from rest_framework import serializers

from .models import Institution, Region


class InstitutionSerializer(serializers.ModelSerializer):
    region = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Institution
        fields = ('id', 'name', 'code', 'region')


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ('id', 'name')


# class AdjudicatorSerializer(serializers.Serializer):
#     class Meta:
#         model = Adjudicator
#         fields = ('id', 'name', 'gender')

#     institution = InstitutionSerializer()


# class TeamSerializer(serializers.Serializer):
#     class Meta:
#         model = Team
#         fields = ('id', 'name', 'gender')

#     institution = InstitutionSerializer()
