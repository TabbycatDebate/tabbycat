from channels.routing import route

from .consumers import ws_add, ws_disconnect, ws_message


channel_routing = [
    # Listen for the stream of latest actions
    route("websocket.connect", ws_add, path=r"^/latest/"),
    route("websocket.receive", ws_message, path=r"^/latest/"),
    route("websocket.disconnect", ws_disconnect, path=r"^/latest/"),
]
