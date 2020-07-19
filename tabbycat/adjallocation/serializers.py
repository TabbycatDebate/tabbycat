from rest_framework import serializers

from participants.serializers import AdjudicatorSerializer
from utils.serializers import DebateSerializerMixin, VueDraggableItemMixin

from .models import PreformedPanel


class EditPanelOrDebateAdjSerializer(AdjudicatorSerializer, VueDraggableItemMixin):
    """ Returns adjudicators for use in views where they are allocated """
    score = serializers.SerializerMethodField(read_only=True)

    def get_score(self, obj):
        return obj.weighted_score(self.context['feedback_weight'])

    class Meta:
        model = AdjudicatorSerializer.Meta.model
        fields = (*AdjudicatorSerializer.Meta.fields,
                  *VueDraggableItemMixin.Meta.fields,
                  'score')


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
        fields = ('id', 'importance', 'adjudicators', 'sort_index',
                  'bracket_min', 'bracket_max', 'room_rank', 'liveness')

# Below classes serialise only a specified field (i.e. allocated adjudicators);
# i.e. they act as a a lightweight data update to be broadcast back over the
# websocket in response to websocket actions or updates rather than needing to
# construct a complete representation of the debate or panelfrom scratch


class SimpleDebateImportanceSerializer(EditDebateAdjsDebateSerializer):
    class Meta:
        model = EditDebateAdjsDebateSerializer.Meta.model
        fields = ('id', 'importance')


class SimplePanelImportanceSerializer(EditPanelAdjsPanelSerializer):
    class Meta:
        model = EditPanelAdjsPanelSerializer.Meta.model
        fields = ('id', 'importance')


class SimpleDebateAllocationSerializer(EditDebateAdjsDebateSerializer):
    class Meta:
        model = EditDebateAdjsDebateSerializer.Meta.model
        fields = ('id', 'adjudicators')


class SimplePanelAllocationSerializer(EditPanelAdjsPanelSerializer):
    class Meta:
        model = EditPanelAdjsPanelSerializer.Meta.model
        fields = ('id', 'adjudicators')
