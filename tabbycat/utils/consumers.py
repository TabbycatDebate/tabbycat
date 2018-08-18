from asgiref.sync import async_to_sync
from django.core.cache import cache
from django.shortcuts import get_object_or_404

from channels.generic.websocket import JsonWebsocketConsumer

from tournaments.models import Tournament


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

    def send_error(self, error, message):
        # Need to forcibly decode the string (for translations)
        self.send_json({'error': str(error), 'message': str(message)})
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
