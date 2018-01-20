from channels import Group
from channels.auth import channel_session_user, channel_session_user_from_http


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
