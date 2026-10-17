# Note: Needs to be in this directory for the proper asgi import

# ==============================================================================
# Logging Setup
# ==============================================================================

import logging
import os

logger = logging.getLogger(__name__)

# ==============================================================================
# Uvicorn Setup
# ==============================================================================

# import uvicorn # noqa: E402

# Start Uvicorn. Render deploys must bind to 0.0 not localhost or 127.0
# logger.info('TC_DEPLOY: Initialising uvicorn')
# uvicorn.run("asgi:application", log_level="info", host="0.0.0.0", proxy_headers=True)

# ==============================================================================
# Daphne Setup
# ==============================================================================

import asgi # noqa: E402
from daphne.endpoints import build_endpoint_description_strings # noqa: E402
from daphne.server import Server # noqa: E402

# Docker/Heroku environments use NGINX and must bind to a socket; others bind to address
if 'USING_NGINX' in os.environ and bool(int(os.environ['USING_NGINX'])):
    logger.info('TC_DEPLOY: Initialising Daphne with NGINX')
    Server(
        application=asgi.application,
        endpoints=build_endpoint_description_strings(
            unix_socket="/tmp/asgi.socket",
        ),
        ping_interval=15,
        ping_timeout=30,
        websocket_timeout=10800, # 3 hours maximum length
        websocket_connect_timeout=10,
        application_close_timeout=10,
        verbosity=1,
        proxy_forwarded_address_header="X-Forwarded-For",
        proxy_forwarded_port_header="X-Forwarded-Port",
        proxy_forwarded_proto_header="X-Forwarded-Proto",
    ).run()
else:
    logger.info('TC_DEPLOY: Initialising Daphne with Host/Port')
    port = os.environ.get('PORT', '8000')
    Server(
        application=asgi.application,
        endpoints=build_endpoint_description_strings(
            host="0.0.0.0",
            port=port,
        ),
        ping_interval=15,
        ping_timeout=30,
        websocket_timeout=10800, # 3 hours maximum length
        websocket_connect_timeout=10,
        application_close_timeout=10,
        verbosity=1,
        proxy_forwarded_address_header="X-Forwarded-For",
        proxy_forwarded_port_header="X-Forwarded-Port",
        proxy_forwarded_proto_header="X-Forwarded-Proto",
    ).run()
