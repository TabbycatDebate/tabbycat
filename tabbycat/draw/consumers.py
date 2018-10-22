import logging

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from channels.layers import get_channel_layer
from django.utils.translation import gettext as _
from rest_framework.renderers import JSONRenderer

from adjallocation.serializers import SimpleDebateAllocationSerializer, SimpleDebateImportanceSerializer
from tournaments.mixins import RoundWebsocketMixin
from utils.mixins import SuperuserRequiredWebsocketMixin
from utils.serializers import django_rest_json_render

from .models import Debate

logger = logging.getLogger(__name__)


class BaseAdjudicatorContainerConsumer(SuperuserRequiredWebsocketMixin, RoundWebsocketMixin, JsonWebsocketConsumer):
    """For receiving updates to either debates or preformed panels; making the
    supplied modifications; and re-broadcasting them. The intent is that the
    socket provides a dict of objects, which in turn have a dict of attributes
    that can be updated directly and the original object returned. This avoids
    having to serialise/re-serialise objects that creates many more queries"""

    def delete_adjudicators(self, debate_or_panel, adj_ids):
        return debate_or_panel.related_adjudicator_set.exclude(adjudicator_id__in=adj_ids).delete()

    def create_adjudicators(self, debate_or_panel, adj_id, adj_type):
        return debate_or_panel.related_adjudicator_set.update_or_create(
            adjudicator_id=adj_id, defaults={'type': adj_type})

    def update_adjudicators(self, debate_or_panel, adjudicators):
        # Delete adjudicators who aren't in the posted information
        adj_ids = [a["adjudicator"]["id"] for a in adjudicators]
        delete_count, deleted = self.delete_adjudicators(debate_or_panel, adj_ids)
        logger.debug("Deleted %d adjudicators from %s", delete_count, debate_or_panel)

        # Update or create positions of adjudicators in debate
        for adjudicator in adjudicators:
            adj_id = adjudicator['adjudicator']['id']
            adj_type = adjudicator['position']
            obj, created = self.create_adjudicators(debate_or_panel, adj_id, adj_type)

        return debate_or_panel

    def update_importance(self, debate_or_panel, importance):
        debate_or_panel.importance = int(importance)
        debate_or_panel.save()
        return debate_or_panel

    def get_objects(self, ids):
        return list(self.model.objects.filter(id__in=ids))

    def receive_debates_or_panels(self, json_objects, original_content):
        # Retrieve either the debates or panels
        debates_or_panels = self.get_objects([jo['id'] for jo in json_objects])
        if len(debates_or_panels) != len(json_objects):
            self.send_error(_("TODO: error"), _("TODO: msg"))

        # TODO: ideally the below would use the same serializer class properties
        # i.e. SimpleDebateImportanceSerializer to validate and save the
        # changes to attributes?
        for (debate_or_panel, jo) in zip(debates_or_panels, json_objects):
            if "importance" in jo:
                debate_or_panel = self.update_importance(debate_or_panel, jo['importance'])
            if "adjudicators" in jo:
                debate_or_panel = self.update_adjudicators(debate_or_panel, jo['adjudicators'])

        # TODO: the below obviously doesn't work for serialising adjudicators;
        # need to split the serializer function; at that point should just
        # create seperate receive_paths per property? Or perhaps serialize
        # and broadcast in the update methods
        serializer = self.importance_serializer(debates_or_panels, many=True)

        # Re-Broadcast initial payload to confirm the change to websockets
        async_to_sync(get_channel_layer().group_send)(
            self.group_name(), {
                'type': 'broadcast_debates_or_panels',
                'content': serializer.data
            }
        )

    def receive_action(self, action_function, user):
        # TODO: Make this selection mechanism more robust
        worker = "venues" if action_function == "allocate_debate_venues" else "adjallocation"

        async_to_sync(get_channel_layer().send)(worker, {
            "type": action_function, # Corresponds to the function
            "extra": {'user_id': user.id, 'round_id': self.round.id,
                      'tournament_id': self.tournament.id,
                      'group_name': self.group_name()}
        })

    def receive_json(self, content):
        # For convenience, allocation/Priorisation actions come over this socket
        # TODO: these should be async actions; await the response then send back
        if 'action' in content:
            self.receive_action(content['action'], self.scope["user"])
        else:
            self.receive_debates_or_panels(content['debatesOrPanels'], content)

    def broadcast_debates_or_panels(self, event):
        self.send_json(event['content'])


class DebateEditConsumer(BaseAdjudicatorContainerConsumer):
    group_prefix = 'debates'
    model = Debate
    importance_serializer = SimpleDebateImportanceSerializer
    adjudicators_serializer = SimpleDebateAllocationSerializer
