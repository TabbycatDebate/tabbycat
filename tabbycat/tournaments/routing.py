from channels.generic.websockets import WebsocketDemultiplexer
from channels.routing import route_class

from actionlog.consumers import ActionLogEntryConsumer
from results.consumers import BallotSubmissionConsumer


class OverviewDemultiplexer(WebsocketDemultiplexer):
    # Allow for multiple consumers on the same socket
    consumers = {
        "actionlog": ActionLogEntryConsumer,
        "ballot": BallotSubmissionConsumer,
    }


channel_routing = [
    # Listen for the stream of latest actions
    route_class(OverviewDemultiplexer, path="^/overviews/"),
]
