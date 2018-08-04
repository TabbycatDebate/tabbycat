from django.conf.urls import url

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from actionlog.consumers import ActionLogEntryConsumer
from checkins.consumers import CheckInEventConsumer
from results.consumers import BallotResultConsumer, BallotStatusConsumer


# This acts like a urls.py equivalent; need to import the channel routes
# from sub apps into this file (plus specifying their top level URL path)
# Note the lack of trailing "/" (but paths in apps need a trailing "/")

application = ProtocolTypeRouter({

    # HTTP handled automatically

    # WebSocket handlers
    "websocket": AuthMiddlewareStack(
        URLRouter([
            # TournamentOverviewContainer
            url(r'^ws/(?P<tournament_slug>[-\w_]+)/actionlogs/$', ActionLogEntryConsumer),
            url(r'^ws/(?P<tournament_slug>[-\w_]+)/ballot_results/$', BallotResultConsumer),
            url(r'^ws/(?P<tournament_slug>[-\w_]+)/ballot_statuses/$', BallotStatusConsumer),
            # CheckInStatusContainer
            url(r'^ws/(?P<tournament_slug>[-\w_]+)/checkins/$', CheckInEventConsumer)
        ])
    ),
})
