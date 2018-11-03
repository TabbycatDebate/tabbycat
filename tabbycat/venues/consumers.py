from django.utils.translation import gettext as _

from actionlog.models import ActionLogEntry
from draw.consumers import EditDebateOrPanelWorkerMixin
from tournaments.models import Round

from .allocator import allocate_venues
from .serializers import SimpleDebateVenueSerializer


class VenuesWorkerConsumer(EditDebateOrPanelWorkerMixin):

    def allocate_debate_venues(self, event):
        round = Round.objects.get(pk=event['extra']['round_id'])

        # if self.round.draw_status == Round.STATUS_RELEASED:
        #     info = "Draw is already released, unrelease draw to redo auto-allocations."
        #     logger.warning(info)
        #     raise BadJsonRequestError(info)
        # if self.round.draw_status != Round.STATUS_CONFIRMED:
        #     info = "Draw is not confirmed, confirm draw to run auto-allocations."
        #     logger.warning(info)
        #     raise BadJsonRequestError(info)

        allocate_venues(round)
        self.log_action(event['extra'], round, ActionLogEntry.ACTION_TYPE_VENUES_AUTOALLOCATE)

        content = self.reserialize_debates(SimpleDebateVenueSerializer, round)
        msg = _("Succesfully auto-allocated venues to debates.")
        self.return_response(content, event['extra']['group_name'], msg, 'success')
