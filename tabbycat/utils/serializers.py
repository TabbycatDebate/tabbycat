from rest_framework import serializers

from adjallocation.models import DebateAdjudicator
from draw.models import Debate
from participants.serializers import AdjudicatorSerializer, TeamSerializer
from venues.models import Venue


class VenueSerializer(serializers.ModelSerializer):
    """ Like the below class this cant live in venue/serializers as they depend
    on the DebateSerializerMixin """
    class Meta:
        model = Venue
        fields = ('id', 'name', 'display_name')


class DebateSerializerMixin(serializers.ModelSerializer):
    """ Returns a basic debate object; overriden for each drag/drop view"""
    """ This can't be defined in draw otherwise it creates circular imports """
    venue = VenueSerializer(read_only=True)
    adjudicators = serializers.SerializerMethodField(read_only=True)
    teams = serializers.SerializerMethodField(read_only=True)

    def adjudicator_representation(self, debate_or_panel_adj):
        return AdjudicatorSerializer(debate_or_panel_adj.adjudicator).data

    def debate_or_panel_adjudicators(self, obj):
        return obj.debateadjudicator_set.all()

    def get_adjudicators(self, obj):
        types = DebateAdjudicator.TYPE_CHOICES
        adjudicators = {key: [] for (key, label) in types}
        for debate_adj in self.debate_or_panel_adjudicators(obj):
            adjudicator = self.adjudicator_representation(debate_adj)
            adjudicators[debate_adj.type].append(adjudicator)
        return adjudicators

    def team_representation(self, debate_team):
        return TeamSerializer(debate_team.team).data

    def get_teams(self, obj):
        sides = {side: None for (side) in self.context['sides']}
        for debate_team in obj.debateteam_set.all():
            sides[debate_team.side] = self.team_representation(debate_team)
        return sides

    class Meta:
        model = Debate
        fields = ('id', 'bracket', 'room_rank', 'importance', 'result_status',
                  'sides_confirmed', 'venue', 'teams', 'adjudicators')
