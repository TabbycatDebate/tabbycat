from actionlog.models import ActionLogEntry
from tournaments.models import Round

from .allocator import allocate_venues


class AllocateDebateVenuesTask():
    """ Mixin to DebateOrPanelWorkerConsumer that specifies the worker's task"""

    def allocate_debate_venues(self, event):
        self.log_action(event['extra'], ActionLogEntry.ACTION_TYPE_VENUES_AUTOALLOCATE)
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

        # TODO: return values (will require modifying the allocate function
        # self.return_response(content, event['extra']['group_name'])
