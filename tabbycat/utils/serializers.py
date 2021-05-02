import time

from rest_framework import serializers
from rest_framework.renderers import JSONRenderer

from adjallocation.models import DebateAdjudicator
from draw.models import Debate
from participants.serializers import AdjudicatorSerializer, TeamSerializer
from venues.models import Venue, VenueCategory


def django_rest_json_render(data):
    """ For some reason JSONRenderer produces byte strings which cant be parsed
    into templates or sent over a websocket; so need to intermediate """
    return bytes.decode(JSONRenderer().render(data))


class VueDraggableItemMixin(serializers.Serializer):
    """ Provides properties that the front end sets for draggable items """
    vue_is_locked = serializers.BooleanField(default=False)
    vue_last_modified = serializers.SerializerMethodField(read_only=True)
    available = serializers.SerializerMethodField(read_only=True)

    def get_available(self, debate_or_panel_adj):
        """ Requires the queryset to be annotate with availabilities """
        return debate_or_panel_adj.available

    def get_vue_last_modified(self, object):
        """ Serialise modified as unix time to get around TZ issues in JS """
        return int(time.time())

    class Meta:
        fields = ('vue_is_locked', 'vue_last_modified', 'available')


class VenueCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = VenueCategory
        fields = ('id', 'name', 'description')


class VenueSerializer(serializers.ModelSerializer):
    """ Like the below class this cant live in venue/serializers as they depend
    on the DebateSerializerMixin """

    categories = VenueCategorySerializer(many=True, source='venuecategory_set')

    class Meta:
        model = Venue
        fields = ('id', 'name', 'display_name', 'priority', 'categories')


class DebateSerializerMixin(serializers.ModelSerializer):
    """ Returns a basic debate object; overriden for each drag/drop view"""
    """ This can't be defined in draw otherwise it creates circular imports """
    venue = VenueSerializer(read_only=True)
    adjudicators = serializers.SerializerMethodField(read_only=True)
    teams = serializers.SerializerMethodField(read_only=True)
    sort_index = serializers.SerializerMethodField(read_only=True)

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

    def get_sort_index(self, obj):
        return 1 # Set on front-end; just need the attr set at load time for reactivity triggers

    class Meta:
        model = Debate
        fields = ('id', 'bracket', 'room_rank', 'importance', 'result_status',
                  'sides_confirmed', 'venue', 'teams', 'adjudicators', 'sort_index')
