# Note: Needs to be in this directory for the proper asgi import

import logging
import sys

import asgi
from daphne.endpoints import build_endpoint_description_strings
from daphne.server import Server


# Setup logging
root = logging.getLogger()
root.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)
root.info('TC_DEPLOY: Initialising daphne')

# Same Command
# daphne asgi:application --unix-socket "/tmp/asgi.socket" --http-timeout 29 --proxy-headers --ping-interval 15

# Start Daphne
Server(
    application=asgi.application,
    endpoints=build_endpoint_description_strings(
        unix_socket="/tmp/asgi.socket",
    ),
    http_timeout=29,
    ping_interval=15,
    ping_timeout=30,
    websocket_timeout=10800, # 3 hours maximum length
    websocket_connect_timeout=5,
    application_close_timeout=10,
    action_logger=None,
    ws_protocols=None,
    root_path="",
    verbosity=2,
    proxy_forwarded_address_header="X-Forwarded-For",
    proxy_forwarded_port_header="X-Forwarded-Port",
    # proxy_forwarded_proto_header="X-Forwarded-Proto", # Not enabled on currently released daphne,
).run()


# Can re-enable if Uvicorn ever adds keep-alive suport:

# import uvicorn

# Same Command
# uvicorn asgi:application --uds "/tmp/asgi.socket" --log-level debug --proxy-headers

# Start Uvicorn
# uvicorn.run(asgi.application, log_level="info",
#                              uds="/tmp/asgi.socket", proxy_headers=True)
