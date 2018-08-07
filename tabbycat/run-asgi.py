# Note: Needs to be in this directory for the proper wsgi import

import uvicorn
import asgi

print("TC_DEPLOY: Initialising uvicorn")


# Same Command
# uvicorn asgi:application --uds "/tmp/asgi.socket" --log-level debug --proxy-headers

# Start Uvicorn
uvicorn.run(asgi.application, log_level="info",
                              uds="/tmp/asgi.socket", proxy_headers=True)
