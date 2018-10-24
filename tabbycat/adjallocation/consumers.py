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
from .serializers import (SimpleDebateAllocationSerializer, SimpleDebateImportanceSerializer,
                          SimplePanelAllocationSerializer, SimplePanelImportanceSerializer)

logger = logging.getLogger(__name__)


class PanelEditConsumer(BaseAdjudicatorContainerConsumer):
    group_prefix = 'panels'
    model = PreformedPanel
    importance_serializer = SimplePanelImportanceSerializer
    adjudicators_serializer = SimplePanelAllocationSerializer


class AdjudicatorAllocationWorkerConsumer(SyncConsumer):

    def log_action(self, extra, type):
        ActionLogEntry.objects.log(type=type,
                                   user_id=extra['user_id'],
                                   round_id=extra['round_id'],
                                   tournament_id=extra['tournament_id'])

    def return_response(self, serialized_debates_or_panels, group_name):
        content = {'debatesOrPanels': serialized_debates_or_panels.data}
        async_to_sync(get_channel_layer().group_send)(
            group_name, {
                'type': 'broadcast_debates_or_panels',
                'content': content
            }
        )

    def reserialize_panels(self, serialiser, round, panels=None):
        if not panels:
            panels = round.preformedpanel_set.all() # TODO: prefetch

        serialized_panels = serialiser(panels, many=True)
        return serialized_panels

    def reserialize_debates(self, serialiser, round, debates=None):
        if not debates:
            debates = round.debate_set.all() # TODO: prefetch
        serialized_debates = serialiser(debates, many=True)
        return serialized_debates

    def allocate_debate_adjs(self, event):
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

        # TODO: return debates directly from allocator function?
        content = self.reserialize_debates(SimpleDebateAllocationSerializer, round)
        self.return_response(content, event['extra']['group_name'])

    def allocate_panel_adjs(self, event):
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

        content = self.reserialize_panels(SimplePanelAllocationSerializer, round)
        self.return_response(content, event['extra']['group_name'])

    def allocate_panels_to_debates(self, event):
        self.log_action(event['extra'], ActionLogEntry.ACTION_TYPE_PREFORMED_PANELS_DEBATES_AUTO)

        round = Round.objects.get(pk=event['extra']['round_id'])
        debates = round.debate_set.all()
        panels = round.preformedpanel_set.all()
        allocator = DumbPreformedPanelAllocator(debates, panels, round)
        debates, panels = allocator.allocate()
        copy_panels_to_debates(debates, panels)

        content = self.reserialize_panels(SimplePanelAllocationSerializer, round)
        self.return_response(content, event['extra']['group_name'])

    def prioritise_debates(self, event):
        # PROOF OF CONCEPT DEMO
        self.log_action(event['extra'], ActionLogEntry.ACTION_TYPE_DEBATE_IMPORTANCE_AUTO)

        round = Round.objects.get(pk=event['extra']['round_id'])
        debates = round.debate_set.all()
        for debate in debates:
            debate.importance = random.randint(-2, 2)
            debate.save()

        content = self.reserialize_debates(SimpleDebateImportanceSerializer, round, debates)
        self.return_response(content, event['extra']['group_name'])

    def prioritise_panels(self, event):
        # PROOF OF CONCEPT DEMO
        self.log_action(event['extra'], ActionLogEntry.ACTION_TYPE_PREFORMED_PANELS_IMPORTANCE_AUTO)

        round = Round.objects.get(pk=event['extra']['round_id'])
        panels = round.preformedpanel_set.all()
        for panel in panels:
            panel.importance = random.randint(-2, 2)
            panel.save()

        content = self.reserialize_panels(SimplePanelImportanceSerializer, round, panels)
        self.return_response(content, event['extra']['group_name'])

    def create_preformed_panels(self, event):
        self.log_action(event['extra'], ActionLogEntry.ACTION_TYPE_PREFORMED_PANELS_CREATE)
        # TODO: PROOF OF CONCEPT DEMO
        round = Round.objects.get(pk=event['extra']['round_id'])
        teams_count = round.tournament.team_set.count()
        if round.tournament.pref('teams_in_debate') == 'bp':
            debates_count = teams_count // 4
        else:
            debates_count = teams_count // 2

        new_panels = [PreformedPanel(round=round)] * debates_count
        PreformedPanel.objects.bulk_create(new_panels)
        content = self.reserialize_panels(SimplePanelAllocationSerializer, round)
        self.return_response(content, event['extra']['group_name'])
