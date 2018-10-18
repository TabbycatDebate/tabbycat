from rest_framework import serializers

from .models import Debate


class DebateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Debate
        fields = ('id', 'bracket', 'room_rank', 'importance', 'result_status',
                  'sides_confirmed')

    # venue = VenueSerializer
    # debate adjudicators = DebateAdjudicatorSerializer
    # debate teams = DebateTeamSerializer


class EditDebateTeamsDebateSerializer(DebateSerializer):
    pass


# class DebateTeamSerializer(serializers.ModelSerializer):
#     # This should be a flat model; i.e. collapse debate team and team
#     pass


# class DebateAdjudicatorSerializer(serializers.ModelSerializer):
#     # This should be a flat model; i.e. collapse debate adjudicator and adj
#     pass
