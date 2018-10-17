from asgiref.sync import async_to_sync
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _

from utils.consumers import TournamentConsumerMixin, WSPublicAccessMixin

from .models import Event, Identifier
from .utils import get_unexpired_checkins


class CheckInEventConsumer(TournamentConsumerMixin, WSPublicAccessMixin):

    group_prefix = 'checkins'

    def receive_json(self, content):
        # Because the public can receive but not send checkins we need to
        # re-authenticate here:
        if not self.scope["user"].is_authenticated:
            return

        # Send message to room group about the new checkin
        async_to_sync(self.channel_layer.group_send)(
            self.group_name(), {
                'type': 'broadcast_checkin',
                'content': content
            }
        )

    # Issue the relevant checkins
    def broadcast_checkin(self, event):
        content = event['content']
        tournament = self.tournament()
        barcode_ids = [b for b in content['barcodes'] if b is not None]
        return_content = {'created': content['status'], 'checkins': [],
                          'component_id': content['component_id']}

        for barcode in barcode_ids:
            try:
                identifier = Identifier.objects.get(barcode=barcode)
                if content['status'] is True:
                    # If checking-in someone
                    checkin = Event.objects.create(identifier=identifier,
                                                   tournament=tournament)
                    return_content['checkins'].append(checkin.serialize())
                else:
                    # If undoing/revoking a check-in
                    if content['type'] == 'people':
                        window = 'checkin_window_people'
                    else:
                        window = 'checkin_window_venues'

                    checkins = get_unexpired_checkins(tournament, window)
                    checkins.filter(identifier=identifier).delete()
                    return_content['checkins'].append({'identifier': barcode})

            except ObjectDoesNotExist:
                # Only raise an error for single check-ins as for multi-check-in
                # events via the status page its clear what has failed or not
                if len(barcode_ids) == 1:
                    msg = _("Sent checkin identifier doesn't exist")
                    self.send_error(_("Checkins"), msg, content)
                    return

        if len(return_content['checkins']) == 0 and content['status'] is not False:
            msg = _("No checkin identifiers exist for sent barcodes")
            self.send_error(_("Checkins"), msg, content)
            return

        self.send_json(return_content)
