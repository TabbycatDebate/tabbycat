import json

from asgiref.sync import AsyncToSync
from django.core.exceptions import ObjectDoesNotExist

from utils.consumers import TournamentConsumer, WSPublicAccessMixin

from .models import Event, Identifier
from .utils import get_unexpired_checkins


class CheckInEventConsumer(TournamentConsumer, WSPublicAccessMixin):

    group_prefix = 'checkins'

    def receive(self, text_data):
        # Because the public can receive but not send checkins we need to
        # re-authenticate here:
        if not self.scope["user"].is_authenticated:
            return
        if not self.scope["user"].is_superuser:
            return

        payload = self.checkin_identifiers(text_data)
        # Send message to room group about the new checkin
        AsyncToSync(self.channel_layer.group_send)(self.group_name(), {
            'type': 'broadcast_checkin',
            'payload': payload
        })

    def broadcast_checkin(self, event):
        payload = event['payload']
        print('broadcast_checkin', event)

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'data': payload
        }))

    # Issue the relevant checkins and return the new objects
    def checkin_identifiers(self, text_data):
        barcode_ids = json.loads(text_data)['barcodes']
        barcode_ids = [b for b in barcode_ids if b is not None]
        status = json.loads(text_data)['status']
        events = []
        tournament = self.identify_tournament()
        for barcode in barcode_ids:
            try:
                identifier = Identifier.objects.get(barcode=barcode)
                if status is True: # If checking-in someone
                    event = Event.objects.create(identifier=identifier,
                                                 tournament=tournament)
                    events.append(event)
                else:
                    # If undoing/revoking a check-in
                    if json.loads(self.text_data)['type'] == 'people':
                        window = 'checkin_window_people'
                    else:
                        window = 'checkin_window_venues'

                    events = get_unexpired_checkins(tournament, window)
                    events.filter(identifier=identifier).delete()

            except ObjectDoesNotExist:
                # Only raise an error for single check-ins as for multi-check-in
                # events via the status page its clear what has failed or not
                if len(barcode_ids) == 1:
                    raise("Identifier doesn't exist")

        if len(events) > 0 or status is False:
            return [e.serialize() for e in events]
        else:
            raise("No identifiers exist for given barcodes")
