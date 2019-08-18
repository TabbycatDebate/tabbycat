"""
ASGI entrypoint. Configures Django and then runs the application
defined in the ASGI_APPLICATION setting.
"""

import os

import django
import sentry_sdk

from channels.routing import get_default_application
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
sentry_sdk.init(dsn="https://6bf2099f349542f4b9baf73ca9789597@sentry.io/185382")

django.setup()

# Wrap ASGI middleware; as per docs.sentry.io/platforms/python/asgi/
application = SentryAsgiMiddleware(get_default_application())
