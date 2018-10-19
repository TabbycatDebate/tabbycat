from rest_framework import serializers

from participants.serializers import AdjudicatorSerializer
from utils.serializers import DebateSerializerMixin

from .models import PreformedPanel


class EditPanelOrDebateAdjudicatorSerializer(AdjudicatorSerializer):
    """ Returns adjudicators for use in views where they are allocated """

    # score = serializers.IntegerField()
    # fetch conflicts
    pass


class EditDebateAdjudicatorsDebateSerializer(DebateSerializerMixin):
    """ Returns debates for the Edit Adjudicator Allocation view"""

    # TODO override fetching the full debate adjudicators to just use primary key
    pass


class EditPanelAdjudicatorsPanelSerializer(serializers.ModelSerializer):
    """ Returns debates for the Edit Panels Allocation view"""
    class Meta:
        model = PreformedPanel
        fields = ('id', 'importance')
