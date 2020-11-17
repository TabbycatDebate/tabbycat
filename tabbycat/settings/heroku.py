import logging
from os import environ

import dj_database_url
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration

from .core import TABBYCAT_VERSION


# ==============================================================================
# Heroku
# ==============================================================================

# Store Tab Director Emails for reporting purposes
if 'TAB_DIRECTOR_EMAIL' in environ:
    TAB_DIRECTOR_EMAIL = environ.get('TAB_DIRECTOR_EMAIL', '')

# Get key from heroku config env else use a fall back
if environ.get('DJANGO_SECRET_KEY'):
    SECRET_KEY = environ.get('DJANGO_SECRET_KEY')

# Allow all host headers
ALLOWED_HOSTS = ['*']

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Require HTTPS
if 'DJANGO_SECRET_KEY' in environ and environ.get('DISABLE_HTTPS_REDIRECTS', '') != 'disable':
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# ==============================================================================
# Postgres
# ==============================================================================

# Parse database configuration from $DATABASE_URL
DATABASES = {
    'default': dj_database_url.config(default='postgres://localhost'),
}

# ==============================================================================
# Redis
# ==============================================================================

# Use a separate Redis addon for channels to reduce number of connections
# With fallback for Tabbykitten installs (no addons) or pre-2.2 instances
if environ.get('REDISCLOUD_URL'):
    ALT_REDIS_URL = environ.get('REDISCLOUD_URL') # 30 clients on free
else:
    ALT_REDIS_URL = environ.get('REDIS_URL') # 20 clients on free

# Connection/Pooling Notes
# ========================
# From testing each dyno seems to use, at a maximum, 8 connections for
# serving standard traffic. Channels seems to use 1 connection per dyno.
# Setting the connection pool could enforce limits to keep this under the
# maximum, however that just shifts the point of failure to the pool's max
# which is trickier to calibrate as it is traffic/dyno dependenent.
# It seems that connections are essentially per-process (so 5 per dyno;
# following the unicorn worker count) along with some left idle waiting to
# be closed (Heroku by default closes after 5 minutes)
# ========================
# The below config sets a more aggressive timeout but does not limit
# total connections — so the limit of 30 could be theoretically be hit if
# running 4 or so dynos. If this becomes a problem then we need to implement
# a pooling logic that ensures connections are shared amonst unicorn workers
# ========================

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": ALT_REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # "IGNORE_EXCEPTIONS": True, # Supresses ConnectionError at max
            # "CONNECTION_POOL_KWARGS": {"max_connections": 5} # See above
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 60,
        },
    },
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [environ.get('REDIS_URL')],
            # Remove channels from groups after 3 hours
            # This matches websocket_timeout in Daphne
            "group_expiry": 10800,
        },
        # RedisChannelLayer should pool by default,
    },
}

# ==============================================================================
# Email / SendGrid
# ==============================================================================

if environ.get('EMAIL_HOST', ''):
    SERVER_EMAIL = environ['DEFAULT_FROM_EMAIL']
    DEFAULT_FROM_EMAIL = environ['DEFAULT_FROM_EMAIL']
    EMAIL_HOST = environ['EMAIL_HOST']
    EMAIL_HOST_USER = environ['EMAIL_HOST_USER']
    EMAIL_HOST_PASSWORD = environ['EMAIL_HOST_PASSWORD']
    EMAIL_PORT = int(environ.get('EMAIL_PORT', 587))
    EMAIL_USE_TLS = bool(environ.get('EMAIL_USE_TLS', True))
elif environ.get('SENDGRID_USERNAME', ''):
    SERVER_EMAIL = environ['SENDGRID_USERNAME']
    DEFAULT_FROM_EMAIL = environ.get('DEFAULT_FROM_EMAIL', environ['SENDGRID_USERNAME'])
    EMAIL_HOST = 'smtp.sendgrid.net'
    EMAIL_HOST_USER = environ['SENDGRID_USERNAME']
    EMAIL_HOST_PASSWORD = environ['SENDGRID_PASSWORD']
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True

# ==============================================================================
# Sentry
# ==============================================================================

if not environ.get('DISABLE_SENTRY'):
    DISABLE_SENTRY = False
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

# ==============================================================================
# Scout
# ==============================================================================

SCOUT_NAME = "Tabbycat"

if environ.get('SCOUT_MONITOR'):
    # Scout should be listed first; prepend it to the existing list if added
    INSTALLED_APPS = ('scout_apm.django', *INSTALLED_APPS)
