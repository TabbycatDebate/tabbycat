from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from django.utils.translation import gettext_lazy as _

from options.utils import use_team_code_names_data_entry
from tournaments.mixins import TournamentWebsocketMixin
from users.permissions import has_permission, Permission

from .models import Event, Identifier
from .utils import get_unexpired_checkins


class CheckInEventConsumer(TournamentWebsocketMixin, JsonWebsocketConsumer):

    group_prefix = 'checkins'

    edit_permission = Permission.EDIT_PARTICIPANT_CHECKIN

    def receive_json(self, content):
        # Because the public can receive but not send checkins we need to
        # re-authenticate here:
        if not has_permission(self.scope["user"], self.edit_permission, self.tournament):
            return

        # Send message to room group about the new checkin
        async_to_sync(self.channel_layer.group_send)(
            self.group_name(), {
                'type': 'broadcast_checkin',
                'content': content,
            },
        )

    # Issue the relevant checkins
    def broadcast_checkin(self, event):
        content = event['content']
        barcode_ids = [b for b in content['barcodes'] if b is not None]
        return_content = {'created': content['status'], 'checkins': [],
                          'component_id': content['component_id']}

        use_team_code_names = use_team_code_names_data_entry(self.tournament, True)

        identifiers = {i.barcode: i for i in Identifier.objects.filter(barcode__in=barcode_ids)}
        non_existent_barcodes = set(barcode_ids) - set(identifiers.keys())
        if non_existent_barcodes and len(non_existent_barcodes) == len(barcode_ids):
            msg = _("Sent checkin identifier doesn't exist")
            self.send_error(_("Checkins"), msg, content)
            return

        for identifier in identifiers.values():
            if content['status'] is True:
                # If checking-in someone
                checkin = Event.objects.create(identifier=identifier,
                                                tournament=self.tournament)
                checkin_dict = checkin.serialize()

                if hasattr(identifier.owner, 'matchup'):
                    if use_team_code_names:
                        checkin_dict['owner_name'] = identifier.owner.matchup_codes
                    else:
                        checkin_dict['owner_name'] = identifier.owner.matchup
                else:
                    checkin_dict['owner_name'] = identifier.owner.name

                return_content['checkins'].append(checkin_dict)
            else:
                # If undoing/revoking a check-in
                if content['type'] == 'people':
                    window = 'checkin_window_people'
                else:
                    window = 'checkin_window_venues'

                checkins = get_unexpired_checkins(self.tournament, window)
                checkins.filter(identifier=identifier).delete()
                return_content['checkins'].append({'identifier': identifier.barcode})

        if len(return_content['checkins']) == 0 and content['status'] is not False:
            msg = _("No checkin identifiers exist for sent barcodes")
            self.send_error(_("Checkins"), msg, content)
            return

        self.send_json(return_content)
