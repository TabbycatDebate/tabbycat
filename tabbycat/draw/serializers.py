from participants.serializers import TeamSerializer
from utils.serializers import DebateSerializerMixin


class EditDebateTeamsDebateSerializer(DebateSerializerMixin):
    """ Returns debates for the Edit Debate Teams view"""

    def team_representation(self, debate_team):
        # Only need the PK of the teams as they are fetched separately
        return debate_team.team.pk


class EditDebateTeamsTeamSerializer(TeamSerializer):
    """ Returns teams for use in the allocate Debate Teams view """
    pass
