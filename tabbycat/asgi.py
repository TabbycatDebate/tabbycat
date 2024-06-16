import os

import django
from channels.auth import AuthMiddlewareStack
from channels.routing import ChannelNameRouter, ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import re_path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from actionlog.consumers import ActionLogEntryConsumer  # noqa: E402 (has to come after settings)
from adjallocation.consumers import (  # noqa: E402 (has to come after settings)
    AdjudicatorAllocationWorkerConsumer,
    PanelEditConsumer,
)
from checkins.consumers import CheckInEventConsumer  # noqa: E402 (has to come after settings)
from draw.consumers import DebateEditConsumer  # noqa: E402 (has to come after settings)
from notifications.consumers import (  # noqa: E402 (has to come after settings)
    NotificationQueueConsumer,
)
from results.consumers import (  # noqa: E402 (has to come after settings)
    BallotResultConsumer,
    BallotStatusConsumer,
)
from venues.consumers import VenuesWorkerConsumer  # noqa: E402 (has to come after settings)

application = ProtocolTypeRouter(
    {
        # Django's ASGI application to handle traditional HTTP requests
        "http": get_asgi_application(),
        # WebSocket handlers
        "websocket": AuthMiddlewareStack(
            URLRouter(
                [
                    # TournamentOverviewContainer
                    re_path(
                        r"^ws/(?P<tournament_slug>[-\w_]+)/action_logs/$",
                        ActionLogEntryConsumer.as_asgi(),
                    ),
                    re_path(
                        r"^ws/(?P<tournament_slug>[-\w_]+)/ballot_results/$",
                        BallotResultConsumer.as_asgi(),
                    ),
                    re_path(
                        r"^ws/(?P<tournament_slug>[-\w_]+)/ballot_statuses/$",
                        BallotStatusConsumer.as_asgi(),
                    ),
                    # CheckInStatusContainer
                    re_path(
                        r"^ws/(?P<tournament_slug>[-\w_]+)/checkins/$",
                        CheckInEventConsumer.as_asgi(),
                    ),
                    # Draw and Preformed Panel Edits
                    re_path(
                        r"^ws/(?P<tournament_slug>[-\w_]+)/round/(?P<round_seq>[-\w_]+)/debates/$",
                        DebateEditConsumer.as_asgi(),
                    ),
                    re_path(
                        r"^ws/(?P<tournament_slug>[-\w_]+)/round/(?P<round_seq>[-\w_]+)/panels/$",
                        PanelEditConsumer.as_asgi(),
                    ),
                ]
            ),
        ),
        # Worker handlers (which don't need a URL/protocol)
        "channel": ChannelNameRouter(
            {
                # Name used in runworker cmd : SyncConsumer responsible
                "notifications": NotificationQueueConsumer.as_asgi(),  # Email sending
                "adjallocation": AdjudicatorAllocationWorkerConsumer.as_asgi(),
                "venues": VenuesWorkerConsumer.as_asgi(),
            }
        ),
    }
)
