from channels.routing import route_class
# from channels.routing import route

from .consumers import TournamentOverviewDemultiplexer
# from .consumers import ws_add, ws_disconnect, ws_message


channel_routing = [
    # Listen for the stream of latest actions
    route_class(TournamentOverviewDemultiplexer, path="^/overviews/"),
]
