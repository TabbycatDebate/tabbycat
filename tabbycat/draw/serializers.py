from participants.serializers import TeamSerializer
from utils.serializers import DebateSerializerMixin


class EditDebateTeamsDebateSerializer(DebateSerializerMixin):
    """ Returns debates for the Edit Debate Teams view"""
    pass


class EditDebateTeamsTeamSerializer(TeamSerializer):
    """ Returns teams for use in the allocate Debate Teams view """
    pass
