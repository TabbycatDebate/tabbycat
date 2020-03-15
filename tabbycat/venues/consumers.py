from django.utils.translation import gettext as _

from actionlog.models import ActionLogEntry
from draw.consumers import EditDebateOrPanelWorkerMixin
from tournaments.models import Round

from .allocator import allocate_venues
from .serializers import SimpleDebateVenueSerializer


class VenuesWorkerConsumer(EditDebateOrPanelWorkerMixin):

    def allocate_debate_venues(self, event):
        round = Round.objects.get(pk=event['extra']['round_id'])
        group = event['extra']['group_name']

        if round.draw_status == Round.STATUS_RELEASED:
            self.return_error(group, _("Draw is already released, unrelease draw to assign rooms."))
            return
        if round.draw_status != Round.STATUS_CONFIRMED:
            self.return_error(group, _("Draw is not confirmed, confirm draw to assign rooms."))
            return

        allocate_venues(round)
        self.log_action(event['extra'], round, ActionLogEntry.ACTION_TYPE_VENUES_AUTOALLOCATE)

        content = self.reserialize_debates(SimpleDebateVenueSerializer, round)
        msg = _("Successfully auto-allocated rooms to debates.")
        self.return_response(content, group, msg, 'success')
