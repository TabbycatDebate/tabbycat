import logging

from asgiref.sync import async_to_sync
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _

from channels.generic.websocket import JsonWebsocketConsumer

from tournaments.models import Tournament

logger = logging.getLogger(__name__)


class WSLoginRequiredMixin():

    def authentication_needed(self):
        return self.scope["user"].is_authenticated


class WSSuperUserRequiredMixin():

    def authentication_needed(self):
        return self.scope["user"].is_superuser


class WSPublicAccessMixin():

    def authentication_needed(self):
        return True


class TournamentConsumer(JsonWebsocketConsumer):
    """For a channel consumer specific to a tournament and whose path includes
    a tournament_slug. Must provide a group_prefix that serves as a stream_name
    to be follow by "_" and tournament_slug."""

    group_prefix = None

    tournament_slug_url_kwarg = "tournament_slug"
    tournament_cache_key = "{slug}_object"
    tournament_redirect_pattern_name = None

    def tournament(self):
        # First look in self
        if hasattr(self, "_tournament_from_url"):
            return self._tournament_from_url

        # Then look in cache
        slug = self.scope["url_route"]["kwargs"][self.tournament_slug_url_kwarg]
        key = self.tournament_cache_key.format(slug=slug)
        cached_tournament = cache.get(key)
        if cached_tournament:
            self._tournament_from_url = cached_tournament
            return cached_tournament

        # If it was in neither place, retrieve the object
        tournament = get_object_or_404(Tournament, slug=slug)
        cache.set(key, tournament, None)
        self._tournament_from_url = tournament
        return tournament

    def group_name(self):
        return self.group_prefix + '_' + self.tournament().slug

    def send_error(self, error, message, original_content):
        # Need to forcibly decode the string (for translations)
        self.send_json({
            'error': str(error),
            'message': str(message),
            'original_content': original_content,
            'component_id': original_content['component_id']
        })
        return super()

    def connect(self):
        if self.authentication_needed():
            async_to_sync(self.channel_layer.group_add)(
                self.group_name(), self.channel_name
            )
            self.accept()
        else:
            pass

    def disconnect(self, message):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name(), self.channel_name
        )
        super().disconnect(message)


class DebateOrPanelConsumer(TournamentConsumer, WSSuperUserRequiredMixin):
    """For receiving updates to either debates or preformed panels, making the
    supplied modifications, and re-broadcasting them. This intent is that the
    socket provides a dict of objects, which in turn have a dict of attributes
    that can be updated directly and the original object returned. This avoids
    having to serialise/re-serialise objects that creates many more queries"""

    def update_adjudicators(self, debate_or_panl, adjudicators):
        # Delete adjudicators who aren't in the posted information
        adj_ids = [a["adjudicator"]["id"] for a in adjudicators]
        delete_count, deleted = self.delete_adjudicators(debate_or_panl, adj_ids)
        logger.debug("Deleted %d adjudicators from %s", delete_count, debate_or_panl)

        # Update or create positions of adjudicators in debate
        for adjudicator in adjudicators:
            adj_id = adjudicator['adjudicator']['id']
            adj_type = adjudicator['position']
            obj, created = self.create_adjudicators(debate_or_panl, adj_id, adj_type)

    def receive_json(self, content):
        # Retrieve either the debates or panels
        json_objects = content['debatesOrPanels']
        debates_or_panels = self.get_objects(json_objects.keys())
        if debates_or_panels.count() == 0:
            self.send_error(_("TODO: error"), _("TODO: msg"), content)

        # Make and save the change to the objects based on the provided change
        # TODO: these should be a bulk update operation (F expression?) if they
        # are ever used to update a non trivial amount of objects
        for object_id, object_changes in json_objects.items():
            debate_or_panel = debates_or_panels.get(id=int(object_id))
            for attribute, value in object_changes.items():
                if attribute == "adjudicators":
                    # Manually handle setting debate or panel allocation
                    self.update_adjudicators(debate_or_panel, value)
                else:
                    setattr(debate_or_panel, attribute, value)
                    debate_or_panel.save()

        # Re-Broadcast initial payload to confirm the change to websockets
        async_to_sync(self.channel_layer.group_send)(
            self.group_name(), {
                'type': 'broadcast_checkin',
                'content': content
            }
        )

    def broadcast_checkin(self, event):
        self.send_json(event['content'])
