from asgiref.sync import async_to_sync

from django.utils.encoding import force_text

from tournaments.mixins import RoundFromUrlMixin, TournamentFromUrlMixin


class AccessWebsocketMixin:
    """Checks the user's permissions before allowing a connection.
    Classes using this mixin must inherit from WebsocketConsumer."""

    def connect(self):
        if self.access_permitted():
            return super().connect()
        else:
            return self.close()


class LoginRequiredWebsocketMixin(AccessWebsocketMixin):

    def access_permitted(self):
        return self.scope["user"].is_authenticated


class SuperuserRequiredWebsocketMixin(AccessWebsocketMixin):

    def access_permitted(self):
        return self.scope["user"].is_superuser


class TournamentWebsocketMixin(TournamentFromUrlMixin):
    """Mixin for websocket consumers that listen for changes relating to a
    particular tournament.

    Subclasses must provide a `group_prefix` that serves as a name for the
    stream; the name of the group is a concatenation fo this and the tournament
    slug."""

    group_prefix = None

    tournament_cache_key = "{slug}_tournament_object"

    def get_url_kwargs(self):
        return self.scope["url_route"]["kwargs"]

    def group_name(self):
        return self.group_prefix + '_' + self.tournament.slug

    def send_error(self, error, message, original_content):
        # Need to forcibly decode the string (for translations)
        self.send_json({
            'error': force_text(error),
            'message': force_text(message),
            'original_content': original_content,
            'component_id': original_content['component_id']
        })
        return super()

    def connect(self):
        async_to_sync(self.channel_layer.group_add)(
            self.group_name(), self.channel_name
        )
        super().connect()

    def disconnect(self, message):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name(), self.channel_name
        )
        super().disconnect(message)


class RoundWebsocketMixin(RoundFromUrlMixin, TournamentWebsocketMixin):
    """For a channel consumer specific to a round and whose path includes
    a round_seq. Must provide a group_prefix that serves as a stream_name
    to be follow by "_" then tournament_slug then "_" then round_seq."""

    group_prefix = None

    def group_name(self):
        tournament_path = super().group_name()
        return tournament_path + '_' + str(self.round.seq)
