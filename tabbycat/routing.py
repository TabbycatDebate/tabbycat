from channels.routing import route
from consumers import ws_message


channel_routing = [
    route("websocket.receive", ws_message),
]
