import logging

from asgiref.sync import async_to_sync
from channels.consumer import SyncConsumer
from channels.layers import get_channel_layer

from actionlog.models import ActionLogEntry
from adjallocation.models import DebateAdjudicator
from adjallocation.consumers import AllocateDebateAdjudicatorsTask, AllocatePanelAdjudicatorsTask, PrioritiseDebateAdjudicatorsTask, PrioritisePanelAdjudicatorsTask
from draw.mixins import BaseDebateOrPanelConsumer
from venues.consumers import AllocateDebateVenuesTask

from .models import Debate

logger = logging.getLogger(__name__)


class DebateEditConsumer(BaseDebateOrPanelConsumer):
    """ Adapts the generic methods for updating adjudicators to update debate
    adjudicators specifically (instead of preformed panel adjudicators) """

    group_prefix = 'debates'

    def delete_adjudicators(self, debate, adj_ids):
        return debate.debateadjudicator_set.exclude(adjudicator_id__in=adj_ids).delete()

    def create_adjudicators(self, debate, adj_id, adj_type):
        return DebateAdjudicator.objects.update_or_create(
            debate=debate,
            adjudicator_id=adj_id, defaults={'type': adj_type})

    def get_objects(self, ids):
        return Debate.objects.filter(id__in=ids)


class DebateOrPanelWorkerConsumer(SyncConsumer,
                                  AllocateDebateAdjudicatorsTask,
                                  AllocateDebateVenuesTask,
                                  AllocatePanelAdjudicatorsTask,
                                  PrioritiseDebateAdjudicatorsTask,
                                  PrioritisePanelAdjudicatorsTask):
    """ Base class for specific actions triggered from a websocket that are then
    offloaded to a worker that then re-broadcasts the results over a socket.
    There are two types of inheritors: one for allocation tasks and one for
    prioritisation tasks """

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
