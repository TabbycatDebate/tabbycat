from draw.serializers import DebateSerializer


# class VenueSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Venue
#         fields = ('id', 'name', 'priority', 'display_name')


class EditDebateVenuesDebateSerializer(DebateSerializer):
    # override fetching the debate adjs to just use primary key
    pass


# class EditDebateVenuesVenue(VenueSerializer):
#     # fetch categories
#     # fetch constraints
