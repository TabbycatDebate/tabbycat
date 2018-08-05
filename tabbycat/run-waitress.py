# Note: Needs to be in this directory for the proper wsgi import

from waitress import serve
import wsgi

print("TC_DEPLOY: Initialising waitress")

# Touching /tmp/app-initialized is used to tell NGINX we are ready for traffic
# This is now redundant when using FORCE=1 in the Procfile
# open('/tmp/app-initialized', 'w').close()

# Same Command
# waitress-serve --unix-socket=/tmp/wsgi.socket --expose-tracebacks wsgi:application

# Start Waitress
serve(wsgi.application, unix_socket='/tmp/wsgi.socket', expose_tracebacks=True)
