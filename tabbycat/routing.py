from channels.auth import AuthMiddlewareStack
from channels.routing import ChannelNameRouter, ProtocolTypeRouter, URLRouter
from django.conf.urls import url
from django.core.asgi import get_asgi_application

from actionlog.consumers import ActionLogEntryConsumer
from adjallocation.consumers import AdjudicatorAllocationWorkerConsumer, PanelEditConsumer
from checkins.consumers import CheckInEventConsumer
from draw.consumers import DebateEditConsumer
from notifications.consumers import NotificationQueueConsumer
from results.consumers import BallotResultConsumer, BallotStatusConsumer
from venues.consumers import VenuesWorkerConsumer


# This acts like a urls.py equivalent; need to import the channel routes
# from sub apps into this file (plus specifying their top level URL path)
# Note the lack of trailing "/" (but paths in apps need a trailing "/")

application = ProtocolTypeRouter({

    # HTTP handler
    "http": get_asgi_application(),

    # WebSocket handlers
    "websocket": AuthMiddlewareStack(
        URLRouter([
            # TournamentOverviewContainer
            url(r'^ws/(?P<tournament_slug>[-\w_]+)/action_logs/$', ActionLogEntryConsumer.as_asgi()),
            url(r'^ws/(?P<tournament_slug>[-\w_]+)/ballot_results/$', BallotResultConsumer.as_asgi()),
            url(r'^ws/(?P<tournament_slug>[-\w_]+)/ballot_statuses/$', BallotStatusConsumer.as_asgi()),
            # CheckInStatusContainer
            url(r'^ws/(?P<tournament_slug>[-\w_]+)/checkins/$', CheckInEventConsumer.as_asgi()),
            # Draw and Preformed Panel Edits
            url(r'^ws/(?P<tournament_slug>[-\w_]+)/round/(?P<round_seq>[-\w_]+)/debates/$', DebateEditConsumer.as_asgi()),
            url(r'^ws/(?P<tournament_slug>[-\w_]+)/round/(?P<round_seq>[-\w_]+)/panels/$', PanelEditConsumer.as_asgi()),
        ]),
    ),

    # Worker handlers (which don't need a URL/protocol)
    "channel": ChannelNameRouter({
        # Name used in runworker cmd : SyncConsumer responsible
        "notifications":  NotificationQueueConsumer.as_asgi(), # Email sending
        "adjallocation": AdjudicatorAllocationWorkerConsumer.as_asgi(),
        "venues": VenuesWorkerConsumer.as_asgi(),
    }),
})
