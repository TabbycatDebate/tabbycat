# Note: Needs to be in this directory for the proper wsgi import

import logging
import sys

from waitress import serve

import wsgi


# Setup logging
root = logging.getLogger()
root.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)
root.info('TC_DEPLOY: Initialising waitress')

# Touching /tmp/app-initialized is used to tell NGINX we are ready for traffic
open('/tmp/app-initialized', 'w').close()

# Same Command
# waitress-serve --unix-socket=/tmp/wsgi.socket --expose-tracebacks wsgi:application

# Start Waitress
serve(wsgi.application, unix_socket='/tmp/wsgi.socket', expose_tracebacks=True)
