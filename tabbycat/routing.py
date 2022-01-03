from channels.auth import AuthMiddlewareStack
from channels.routing import ChannelNameRouter, ProtocolTypeRouter, URLRouter
from django.urls import path

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

    # HTTP handled automatically

    # WebSocket handlers
    "websocket": AuthMiddlewareStack(
        URLRouter([
            # TournamentOverviewContainer
            path('ws/<slug:tournament_slug>/action_logs/', ActionLogEntryConsumer),
            path('ws/<slug:tournament_slug>/ballot_results/', BallotResultConsumer),
            path('ws/<slug:tournament_slug>/ballot_statuses/', BallotStatusConsumer),
            # CheckInStatusContainer
            path('ws/<slug:tournament_slug>/checkins/', CheckInEventConsumer),
            # Draw and Preformed Panel Edits
            path('ws/<slug:tournament_slug>/round/<int:round_seq>/debates/', DebateEditConsumer),
            path('ws/<slug:tournament_slug>/round/<int:round_seq>/panels/', PanelEditConsumer),
        ]),
    ),

    # Worker handlers (which don't need a URL/protocol)
    "channel": ChannelNameRouter({
        # Name used in runworker cmd : SyncConsumer responsible
        "notifications":  NotificationQueueConsumer, # Email sending
        "adjallocation": AdjudicatorAllocationWorkerConsumer,
        "venues": VenuesWorkerConsumer,
    }),
})
