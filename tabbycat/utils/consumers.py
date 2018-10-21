from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer

from django.core.cache import cache
from django.shortcuts import get_object_or_404

from tournaments.models import Round, Tournament


class WSLoginRequiredMixin():

    def authentication_needed(self):
        return self.scope["user"].is_authenticated


class WSSuperUserRequiredMixin():

    def authentication_needed(self):
        return self.scope["user"].is_superuser


class WSPublicAccessMixin():

    def authentication_needed(self):
        return True


class TournamentConsumerMixin(JsonWebsocketConsumer):
    """For a channel consumer specific to a tournament and whose path includes
    a tournament_slug. Must provide a group_prefix that serves as a stream_name
    to be follow by "_" and tournament_slug."""

    group_prefix = None

    tournament_slug_url_kwarg = "tournament_slug"
    tournament_cache_key = "{slug}_tournament_object"
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
            self.close()

    def disconnect(self, message):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name(), self.channel_name
        )
        super().disconnect(message)


class RoundConsumerMixin(TournamentConsumerMixin):
    """For a channel consumer specific to a round and whose path includes
    a round_seq. Must provide a group_prefix that serves as a stream_name
    to be follow by "_" then tournament_slug then "_" then round_seq."""

    group_prefix = None

    round_seq_url_kwarg = "round_seq"
    round_cache_key = "{seq}_round_object"

    def round(self):
        # First look in self
        if hasattr(self, "_round_from_url"):
            return self._round_from_url

        # Then look in cache
        seq = self.scope["url_route"]["kwargs"][self.round_seq_url_kwarg]
        key = self.round_cache_key.format(seq=seq)
        cached_round = cache.get(key)
        if cached_round:
            self._round_from_url = cached_round
            return cached_round

        # If it was in neither place, retrieve the object
        round = get_object_or_404(Round, seq=seq, tournament=self.tournament())
        cache.set(key, round, None)
        self._round_from_url = round
        return round

    def group_name(self):
        tournament_path = super().group_name()
        return tournament_path + '_' + str(self.round().seq)
