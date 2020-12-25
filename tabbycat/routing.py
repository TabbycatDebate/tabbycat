from channels.auth import AuthMiddlewareStack
from channels.routing import ChannelNameRouter, ProtocolTypeRouter, URLRouter
from django.conf.urls import url

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
            url(r'^ws/(?P<tournament_slug>[-\w_]+)/action_logs/$', ActionLogEntryConsumer),
            url(r'^ws/(?P<tournament_slug>[-\w_]+)/ballot_results/$', BallotResultConsumer),
            url(r'^ws/(?P<tournament_slug>[-\w_]+)/ballot_statuses/$', BallotStatusConsumer),
            # CheckInStatusContainer
            url(r'^ws/(?P<tournament_slug>[-\w_]+)/checkins/$', CheckInEventConsumer),
            # Draw and Preformed Panel Edits
            url(r'^ws/(?P<tournament_slug>[-\w_]+)/round/(?P<round_seq>[-\w_]+)/debates/$', DebateEditConsumer),
            url(r'^ws/(?P<tournament_slug>[-\w_]+)/round/(?P<round_seq>[-\w_]+)/panels/$', PanelEditConsumer),
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
