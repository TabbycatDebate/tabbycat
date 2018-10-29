from channels.consumer import SyncConsumer

from actionlog.models import ActionLogEntry
from tournaments.models import Round

from .allocator import allocate_venues


class VenuesWorkerConsumer(SyncConsumer):

    def log_action(self, extra, round, type):
        ActionLogEntry.objects.log(type=type, user_id=extra['user_id'],
                round=round, tournament=round.tournament, content_object=round)

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

        # TODO: return values (will require modifying the allocate function
        # self.return_response(content, event['extra']['group_name'])
