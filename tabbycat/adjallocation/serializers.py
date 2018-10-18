from rest_framework import serializers

from draw.serializers import DebateSerializer
# from participants.serializers import BaseAdjudicatorSerializer

from .models import PreformedPanel

# class PanelOrDebateAdjudicatorSerializer(BaseAdjudicatorSerializer):
#     """ For use in views where adjs are edited """
#     # score = serializers.IntegerField()
#     # fetch conflicts
#     pass


class EditDebateAdjudicatorsDebateSerializer(DebateSerializer):
    # override fetching the debate adjs to just use primary key
    pass


class EditPanelAdjudicatorsPanelSerializer(serializers.ModelSerializer):
    # override fetching the panel adjs to just use primary key
    class Meta:
        model = PreformedPanel
        fields = ('id', 'importance')
