"""
ASGI entrypoint. Configures Django and then runs the application
defined in the ASGI_APPLICATION setting.
"""

import logging
import os

import django
import sentry_sdk

from channels.routing import get_default_application
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.redis import RedisIntegration

from settings.core import TABBYCAT_VERSION

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

if not os.environ.get('DISABLE_SENTRY'):
    sentry_sdk.init(
        dsn="https://6bf2099f349542f4b9baf73ca9789597@sentry.io/185382",
        integrations=[
            DjangoIntegration(),
            LoggingIntegration(event_level=logging.WARNING),
            RedisIntegration(),
        ],
        send_default_pii=True,
        release=TABBYCAT_VERSION,
    )

    # Override dictionary trimming so that all preferences will be included in Sentry reports
    # https://forum.sentry.io/t/python-sdk-extra-data-capped-at-400-characters/6909
    sentry_sdk.serializer.MAX_DATABAG_BREADTH = 200

django.setup()

if os.environ.get('DISABLE_SENTRY'):
    application = get_default_application()
else:
    # Wrap ASGI middleware; as per docs.sentry.io/platforms/python/asgi/
    application = SentryAsgiMiddleware(get_default_application())
