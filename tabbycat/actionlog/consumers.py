from channels import Group
from channels.auth import channel_session_user, channel_session_user_from_http
from channels.binding.websockets import WebsocketBinding
from channels.generic.websockets import WebsocketDemultiplexer

from .models import ActionLogEntry


class ActionLogEntryBinding(WebsocketBinding):

    model = ActionLogEntry
    stream = "actionlogs"
    fields = ["__all__"]

    @classmethod
    def group_names(cls, instance):
        return ["actionlogs-updates"]

    def has_permission(self, user, action, pk):
        return True

    # Override default method
    def serialize_data(self, instance):
        return instance.serialize


class ActionLogDemultiplexer(WebsocketDemultiplexer):

    consumers = {
        "actionlog": ActionLogEntryBinding.consumer,
    }

    def connection_groups(self):
        return ["actionlogs-updates"]


# Connected to websocket.connect
@channel_session_user_from_http
def ws_add(message):
    # Accept the connection
    message.reply_channel.send({"accept": True})
    # Add to the chat group
    Group("chat").add(message.reply_channel)


# Connected to websocket.receive
@channel_session_user
def ws_message(message):
    Group("chat").send({
        "text": "[user] %s" % message.content['text'],
    })


# Connected to websocket.disconnect
@channel_session_user
def ws_disconnect(message):
    Group("chat").discard(message.reply_channel)
