import logging
import random

from actionlog.models import ActionLogEntry
from draw.mixins import DebateOrPanelConsumerMixin
from tournaments.models import Round

from .models import PreformedPanel, PreformedPanelAdjudicator
from .hungarian import ConsensusHungarianAllocator, VotingHungarianAllocator

logger = logging.getLogger(__name__)


class PanelEditConsumer(DebateOrPanelConsumerMixin):
    """ Adapts the generic methods for updating adjudicators to update preformed
    panel adjudicators specifically (instead of debate adjudicators) """

    group_prefix = 'panels'

    def delete_adjudicators(self, panel, adj_ids):
        return panel.preformedpaneladjudicator_set.exclude(adjudicator_id__in=adj_ids).delete()

    def create_adjudicators(self, panel, adj_id, adj_type):
        return PreformedPanelAdjudicator.objects.update_or_create(
            panel=panel,
            adjudicator_id=adj_id, defaults={'type': adj_type})

    def get_objects(self, ids):
        return PreformedPanel.objects.filter(id__in=ids)


class AllocateDebateAdjudicatorsTask():
    """ Mixin to DebateOrPanelWorkerConsumer that specifies a worker task"""

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
        adjs = list(round.active_adjudicators.all())
        if round.ballots_per_debate == 'per-adj':
            allocator = VotingHungarianAllocator(debates, adjs, round)
        else:
            allocator = ConsensusHungarianAllocator(debates, adjs, round)

        for alloc in allocator.allocate():
            alloc.save()

        round.adjudicator_status = round.STATUS_DRAFT
        round.save()

        # TODO: return values (will require modifying the allocate function
        # self.return_response(content, event['extra']['group_name'])


class AllocatePanelAdjudicatorsTask():
    """ Mixin to DebateOrPanelWorkerConsumer that specifies a worker task"""
    action_log_type = None # TODO

    def allocate_panel_adjudicators(self, event):
        # self.log_action(user, round)
        # self.return_response(content, event['extra']['group_name'])
        pass


class PrioritiseDebateAdjudicatorsTask():
    """ Mixin to DebateOrPanelWorkerConsumer that specifies a worker task"""
    action_log_type = None # TODO

    def prioritise_debate_adjs(self, event):
        # PROOF OF CONCEPT DEMO
        content = {'debatesOrPanels': {}}
        for debate_id in [117, 118, 119, 120]:
            content['debatesOrPanels'][debate_id] = {'importance': random.randint(-2, 2)}
        self.return_response(content, event['extra']['group_name'])


class PrioritisePanelAdjudicatorsTask():
    """ Mixin to DebateOrPanelWorkerConsumer that specifies a worker task"""
    action_log_type = None # TODO

    def prioritise_panel_adjs(self, event):
        # PROOF OF CONCEPT DEMO
        content = {'debatesOrPanels': {}}
        for debate_id in [117, 118, 119, 120]:
            content['debatesOrPanels'][debate_id] = {'importance': random.randint(-2, 2)}
        self.return_response(content, event['extra']['group_name'])
