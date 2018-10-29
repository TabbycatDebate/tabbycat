from rest_framework import serializers

from utils.serializers import DebateSerializerMixin, VenueSerializer, VueDraggableItemMixin


class EditDebateVenuesDebateSerializer(DebateSerializerMixin):
    """ Returns debates for the Edit Debate Teams view"""
    # Only need the PK of the venues as they are fetched separately
    venue = serializers.PrimaryKeyRelatedField(read_only=True)


class EditDebateVenuesVenueSerializer(VenueSerializer, VueDraggableItemMixin):
    """ Returns venues for use in the allocate Debate Venues view """

    # TODO: fetch categories
    # TODO: fetch constraints
    class Meta:
        model = VenueSerializer.Meta.model
        fields = (*VenueSerializer.Meta.fields,
                  *VueDraggableItemMixin.Meta.fields,
                  'priority')
