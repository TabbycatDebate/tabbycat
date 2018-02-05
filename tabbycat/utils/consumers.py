from channels import Group
from channels.generic.websockets import JsonWebsocketConsumer


class ConsumerLoginRequiredMixin():
    http_user = True

    def connect(self, message, **kwargs):
        if not message.user.is_authenticated:
            return
        else:
            super().connect(message, **kwargs)


class ConsumerAdminRequiredMixin():
    http_user = True

    def connect(self, message, **kwargs):
        if not message.user.is_admin:
            return
        else:
            super().connect(message, **kwargs)


class TournamentConsumer(JsonWebsocketConsumer):
    """For a channel consumer specific to a tournament and whose path includes
    a tournament_id. Must provide a group_base_string that serves as a group
    prefix and stream_name. Must also provide two @staticmethod:
    - a make_payload() that produces an object that can be serialised
    - a get_tournament_id_from_content() that returns the relevant id from object
    """
    http_user = True
    group_base_string = None # Serves as group prefix and stream_name

    @classmethod
    def group_string(cls, tournament_id):
        # Construct a unique group name for this tournament
        return "%s-%s" % (cls.group_base_string, tournament_id)

    def connection_groups(self, **kwargs):
        return [self.group_string(kwargs["tournament_id"])]

    def connect(self, message, **kwargs):
        # Add the user to the tournament specific group; otherwise reject connection
        if kwargs['tournament_id']:
            Group(self.group_string(kwargs['tournament_id'])).add(message.reply_channel)
        else:
            message.reply_channel.send({"close": True})

    def disconnect(self, message, **kwargs):
        Group(self.group_string(kwargs['tournament_id'])).discard(message.reply_channel)

    @classmethod
    def group_send(cls, content):
        # Serialise data using a specific Tabbycat
        # And add the add stream for frontend ID
        tournament_id = cls.get_tournament_id_from_content(content)
        group_name = cls.group_string(tournament_id)
        content = {
            'stream': cls.group_base_string,
            'payload': cls.make_payload(content)
        }
        super().group_send(group_name, content, False)
