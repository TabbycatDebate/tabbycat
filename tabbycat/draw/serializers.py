from participants.serializers import TeamSerializer
from utils.serializers import DebateSerializerMixin, VueDraggableItemMixin


class EditDebateTeamsDebateSerializer(DebateSerializerMixin):
    """ Returns debates for the Edit Debate Teams view"""

    def team_representation(self, debate_team):
        # Only need the PK of the teams as they are fetched separately
        return debate_team.team.pk


class EditDebateTeamsTeamSerializer(TeamSerializer, VueDraggableItemMixin):
    """ Returns teams for use in the allocate Debate Teams view """

    class Meta:
        model = TeamSerializer.Meta.model
        fields = (*TeamSerializer.Meta.fields, 'vue_is_locked', 'vue_last_modified')
