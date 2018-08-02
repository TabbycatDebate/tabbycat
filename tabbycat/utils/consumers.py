from asgiref.sync import AsyncToSync
from django.core.cache import cache
from django.shortcuts import get_object_or_404

from channels.generic.websocket import JsonWebsocketConsumer

from tournaments.models import Tournament


class WSLoginRequiredMixin():

    def is_authenticated(self):
        return self.scope["user"].is_authenticated


class WSSuperUserRequiredMixin():

    def is_authenticated(self):
        return self.scope["user"].is_superuser


class WSPublicAccessMixin():

    def is_authenticated(self):
        return True


class TournamentConsumer(JsonWebsocketConsumer):
    """For a channel consumer specific to a tournament and whose path includes
    a tournament_slug. Must provide a group_prefix that serves as a stream_name
    to be follow by "_" and tournament_slug."""

    group_prefix = None

    tournament_slug_url_kwarg = "tournament_slug"
    tournament_cache_key = "{slug}_object"
    tournament_redirect_pattern_name = None

    # TODO: unify with TournamentMixin()
    def identify_tournament(self):
        # First look in self,
        if hasattr(self, "_tournament_from_url"):
            return self._tournament_from_url

        # then look in cache,
        slug = self.scope["url_route"]["kwargs"][self.tournament_slug_url_kwarg]
        key = self.tournament_cache_key.format(slug=slug)
        cached_tournament = cache.get(key)
        if cached_tournament:
            self._tournament_from_url = cached_tournament
            return cached_tournament

        # and if it was in neither place, retrieve the object
        tournament = get_object_or_404(Tournament, slug=slug)
        cache.set(key, tournament, None)
        self._tournament_from_url = tournament
        return tournament

    def group_name(self):
        return self.group_prefix + '_' + self.identify_tournament().slug

    def connect(self):
        if self.is_authenticated():
            AsyncToSync(self.channel_layer.group_add)(self.group_name(), self.channel_name)
            self.accept()
        else:
            pass

    def disconnect(self, message):
        AsyncToSync(self.channel_layer.group_discard)(self.group_name(), self.channel_name)
        # print('Channels: disconnect from', self.channel_name, self.group_name())
        super().disconnect(message)

    def broadcast(self, event):
        # Handles the "broadcast" event when sent out from outside the class
        # print('Channels: broadcast for', self.group_name(), event)
        self.send_json(event["data"])

    @classmethod
    def get_data(cls, data):
        # Optional; allows for custom methods to act on data before JSONing
        return data
