import logging

from asgiref.sync import async_to_sync
from channels.consumer import SyncConsumer
from channels.generic.websocket import JsonWebsocketConsumer
from channels.layers import get_channel_layer

from actionlog.models import ActionLogEntry
from adjallocation.serializers import SimpleDebateAllocationSerializer, SimpleDebateImportanceSerializer
from tournaments.mixins import RoundWebsocketMixin
from utils.mixins import SuperuserRequiredWebsocketMixin

from .models import Debate

logger = logging.getLogger(__name__)


class BaseAdjudicatorContainerConsumer(SuperuserRequiredWebsocketMixin, RoundWebsocketMixin, JsonWebsocketConsumer):
    """For receiving updates to either debates or preformed panels; making the
    supplied modifications; and re-broadcasting them. The intent is that the
    socket provides a dict of objects, which in turn have a dict of attributes
    that can be updated directly and the original object returned. This avoids
    having to serialise/re-serialise objects that creates many more queries"""

    def receive_json(self, content):
        """ Select the appropriate method given the indicated attribute in JSON
        i.e. from { "importance": { "73" : "1" }, "componentID": 2885 } """
        for (key, value) in content.items():
            if key == 'action':
                self.receive_action(content['action'], self.scope["user"])
            elif key == 'importance':
                self.receive_importance(content)
            elif key == 'adjudicators':
                self.receive_adjudicators(content)

    def receive_action(self, action_function, user):
        # TODO: Make this selection mechanism more robust
        worker = "venues" if action_function == "allocate_debate_venues" else "adjallocation"
        async_to_sync(get_channel_layer().send)(worker, {
            "type": action_function, # Corresponds to the function
            "extra": {'user_id': user.id, 'round_id': self.round.id,
                      'tournament_id': self.tournament.id,
                      'group_name': self.group_name()}
        })

    def get_debates_or_panels(self, debates_or_panels):
        """ Retrieve either the debates or panels from the JSON id keys """
        ids = [id for (id, d_or_p) in debates_or_panels.items()]
        debates_or_panels = list(self.model.objects.filter(id__in=ids))
        # TODO: error handling if return items fewer/more than expected
        return debates_or_panels

    def receive_importance(self, content):
        """ Update importances on the django data then reserialize/return it """
        changes = {int(c['id']): c for c in content['importance']}
        debates_or_panels = self.get_debates_or_panels(changes)
        for d_or_p in debates_or_panels:
            d_or_p.importance = changes[d_or_p.id]['importance']
            d_or_p.save()

        serialized = self.importance_serializer(debates_or_panels, many=True)
        del content['importance'] # Reserialise as debatesOrPanels
        self.return_attributes(content, serialized)

    def delete_adjudicators(self, debate_or_panel, adj_ids):
        return debate_or_panel.related_adjudicator_set.exclude(
            adjudicator_id__in=adj_ids).delete()

    def create_adjudicators(self, debate_or_panel, adj_id, adj_type):
        return debate_or_panel.related_adjudicator_set.update_or_create(
            adjudicator_id=adj_id, defaults={'type': adj_type})

    def receive_adjudicators(self, content):
        """ Update adjudicators on the django data then reserialize/return it """
        changes = {int(c['id']): c for c in content['adjudicators']}
        # TODO: prefetch the adjudicator allocation objects
        debates_or_panels = self.get_debates_or_panels(changes)
        for d_or_p in debates_or_panels:
            sent_allocation = changes[d_or_p.id]['adjudicators']
            sent_allocation_ids = []
            for (position, position_ids) in sent_allocation.items():
                sent_allocation_ids.extend(adj_id for adj_id in position_ids)

            # Delete adjudicators in the posted information
            delete_count, deleted = self.delete_adjudicators(d_or_p, sent_allocation_ids)
            # Re-create positions of adjudicators in debate
            for (position, position_ids) in sent_allocation.items():
                for adjudicator_id in position_ids:
                    obj, created = self.create_adjudicators(d_or_p, adjudicator_id, position)

        # Re-fetch the modified data
        # TODO: is it necessary to re-fetch? Or should the objects be returned?
        debates_or_panels = self.get_debates_or_panels(changes)
        serialized = self.adjudicators_serializer(debates_or_panels, many=True)
        del content['adjudicators']
        self.return_attributes(content, serialized)

    def return_attributes(self, original_content, serialized_content):
        """ Return the original JSON but with the generic debatesOrPanels key """
        original_content['debatesOrPanels'] = serialized_content.data
        async_to_sync(get_channel_layer().group_send)(
            self.group_name(), {
                'type': 'broadcast_debates_or_panels',
                'content': original_content
            }
        )

    def broadcast_debates_or_panels(self, event):
        self.send_json(event['content'])


class DebateEditConsumer(BaseAdjudicatorContainerConsumer):
    group_prefix = 'debates'
    model = Debate
    importance_serializer = SimpleDebateImportanceSerializer
    adjudicators_serializer = SimpleDebateAllocationSerializer


class EditDebateOrPanelWorkerMixin(SyncConsumer):
    """ Mixin for consumers that are run by synchronous workers that perform
    actions to edit and re-serialise debates/panels """

    def log_action(self, extra, round, type):
        ActionLogEntry.objects.log(type=type, user_id=extra['user_id'],
                round=round, tournament=round.tournament, content_object=round)

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

    def return_response(self, serialized_debates_or_panels, group_name,
                        message_text, message_type):
        content = {
            'debatesOrPanels': serialized_debates_or_panels.data,
            'message': {'text': message_text, 'type': message_type}
        }
        async_to_sync(get_channel_layer().group_send)(
            group_name, {
                'type': 'broadcast_debates_or_panels',
                'content': content
            }
        )
