from channels.routing import route_class

from .consumers import ActionLogEntryConsumer


channel_routing = [
    # Listen for the stream of latest actions
    route_class(ActionLogEntryConsumer, path="^/overviews/"),
]
