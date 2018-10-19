from rest_framework import serializers

from adjallocation.models import DebateAdjudicator
from draw.models import Debate, DebateTeam
from participants.serializers import AdjudicatorSerializer, TeamSerializer
from venues.models import Venue


class VenueSerializer(serializers.ModelSerializer):
    """ Like the below class this cant live in venue/serializers as they depend
    on the DebateSerializerMixin """
    class Meta:
        model = Venue
        fields = ('id', 'name', 'display_name')


class DebateTeamSerializer(serializers.ModelSerializer):
    """ Returns adjudicators for use in views where they are not allocated """
    team = TeamSerializer(read_only=True)

    class Meta:
        model = DebateTeam
        fields = ('side', 'team')


class DebateAdjudicatorSerializer(serializers.ModelSerializer):
    """ Returns adjudicators for use in views where they are not allocated """
    adjudicator = AdjudicatorSerializer(read_only=True)

    class Meta:
        model = DebateAdjudicator
        fields = ('type', 'adjudicator')


class DebateSerializerMixin(serializers.ModelSerializer):
    """ Returns a basic debate object; overriden for each drag/drop view"""
    """ This can't be defined in draw otherwise it creates circular imports """
    venue = VenueSerializer(read_only=True)
    teams = DebateTeamSerializer(many=True, read_only=True,
                                 source='debateteam_set')
    adjudicators = DebateAdjudicatorSerializer(many=True, read_only=True,
                                               source='debateadjudicator_set')

    class Meta:
        model = Debate
        fields = ('id', 'bracket', 'room_rank', 'importance', 'result_status',
                  'sides_confirmed', 'venue', 'adjudicators', 'teams')
