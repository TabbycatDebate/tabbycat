from rest_framework import serializers

from participants.serializers import AdjudicatorSerializer
from utils.serializers import DebateSerializerMixin

from .models import PreformedPanel


class EditPanelOrDebateAdjSerializer(AdjudicatorSerializer):
    """ Returns adjudicators for use in views where they are allocated """
    score = serializers.SerializerMethodField(read_only=True)

    def get_score(self, obj):
        return obj.weighted_score(self.context['feedback_weight'])

    class Meta:
        model = AdjudicatorSerializer.Meta.model
        fields = (*AdjudicatorSerializer.Meta.fields, 'score') # Add fields


class EditDebateAdjsDebateSerializer(DebateSerializerMixin):
    """ Returns debates for the Edit Adjudicator Allocation view"""

    def adjudicator_representation(self, debate_or_panel_adj):
        return debate_or_panel_adj.adjudicator.pk


class EditPanelAdjsPanelSerializer(EditDebateAdjsDebateSerializer):
    """ Returns panels for the Edit Panels Allocation view"""

    def debate_or_panel_adjudicators(self, obj):
        return obj.preformedpaneladjudicator_set.all()

    class Meta:
        model = PreformedPanel
        fields = ('id', 'importance', 'adjudicators')
