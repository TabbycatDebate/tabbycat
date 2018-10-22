import logging
import random

from asgiref.sync import async_to_sync
from channels.consumer import SyncConsumer
from channels.layers import get_channel_layer

from actionlog.models import ActionLogEntry
from draw.consumers import BaseAdjudicatorContainerConsumer
from tournaments.models import Round

from .models import PreformedPanel
from .allocators.hungarian import ConsensusHungarianAllocator, VotingHungarianAllocator
from .preformed import copy_panels_to_debates
from .preformed.dumb import DumbPreformedPanelAllocator

logger = logging.getLogger(__name__)


class PanelEditConsumer(BaseAdjudicatorContainerConsumer):
    group_prefix = 'panels'
    model = PreformedPanel


class AdjudicatorAllocationWorkerConsumer(SyncConsumer):

    def log_action(self, extra, type):
        ActionLogEntry.objects.log(type=type,
                                   user_id=extra['user_id'],
                                   round_id=extra['round_id'],
                                   tournament_id=extra['tournament_id'])

    def return_response(self, content, group_name):
        async_to_sync(get_channel_layer().group_send)(
            group_name, {
                'type': 'broadcast_debates_or_panels',
                'content': content
            }
        )

    def allocate_debate_adjs(self, event):
        print('AllocateDebateAdjudicatorsTask allocate_debate_adjs', event)
        self.log_action(event['extra'], ActionLogEntry.ACTION_TYPE_ADJUDICATORS_AUTO)
        round = Round.objects.get(pk=event['extra']['round_id'])

        # TODO: fix the error handling below
        # if round.draw_status == round.STATUS_RELEASED:
        #     info = _("Draw is already released, unrelease draw to redo auto-allocations.")
        #     logger.warning(info)
        #     # raise BadJsonRequestError(info)
        # if round.draw_status != round.STATUS_CONFIRMED:
        #     info = _("Draw is not confirmed, confirm draw to run auto-allocations.")
        #     logger.warning(info)
        #     # raise BadJsonRequestError(info)

        debates = round.debate_set.all()
        adjs = round.active_adjudicators.all()
        if round.ballots_per_debate == 'per-adj':
            allocator = VotingHungarianAllocator(debates, adjs, round)
        else:
            allocator = ConsensusHungarianAllocator(debates, adjs, round)

        for alloc in allocator.allocate():
            alloc.save()

        # TODO: return values (will require modifying the allocate function
        # self.return_response(content, event['extra']['group_name'])

    def allocate_panel_adjs(self, event):
        print('AllocatePanelAdjudicatorsTask allocate_panel_adjudicators', event)
        self.log_action(event['extra'], ActionLogEntry.ACTION_TYPE_PREFORMED_PANELS_ADJUDICATOR_AUTO)

        round = Round.objects.get(pk=event['extra']['round_id'])
        panels = round.preformedpanel_set.all()
        adjs = round.active_adjudicators.all()
        if round.ballots_per_debate == 'per-adj':
            allocator = VotingHungarianAllocator(panels, adjs, round)
        else:
            allocator = ConsensusHungarianAllocator(panels, adjs, round)

        for alloc in allocator.allocate():
            alloc.save()

        # self.return_response(content, event['extra']['group_name'])

    def allocate_panels_to_debates(self, event):
        round = Round.objects.get(pk=event['extra']['round_id'])

        debates = round.debate_set.all()
        panels = round.preformedpanel_set.all()
        allocator = DumbPreformedPanelAllocator(debates, panels, round)
        debates, panels = allocator.allocate()
        copy_panels_to_debates(debates, panels)

    def prioritise_debate_adjs(self, event):
        # PROOF OF CONCEPT DEMO
        content = {'debatesOrPanels': {}}
        for debate_id in [117, 118, 119, 120]:
            content['debatesOrPanels'][debate_id] = {'importance': random.randint(-2, 2)}
        self.return_response(content, event['extra']['group_name'])

    def prioritise_panel_adjs(self, event):
        # PROOF OF CONCEPT DEMO
        content = {'debatesOrPanels': {}}
        for debate_id in [117, 118, 119, 120]:
            content['debatesOrPanels'][debate_id] = {'importance': random.randint(-2, 2)}
        self.return_response(content, event['extra']['group_name'])
