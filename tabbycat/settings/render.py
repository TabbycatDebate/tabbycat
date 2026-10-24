import copy
import logging
import os

import dj_database_url
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.django import DjangoIntegration

from .core import TABBYCAT_VERSION
from .postgres_channels_cache import postgres_channel_layers, postgres_database_cache


def _truthy_env(name: str) -> bool:
    return os.environ.get(name, '').lower() in ('1', 'true', 'yes')

# ==============================================================================
# Render per https://render.com/docs/deploy-django
# ==============================================================================

# Store Tab Director Emails for reporting purposes
if os.environ.get('TAB_DIRECTOR_EMAIL', ''):
    TAB_DIRECTOR_EMAIL = os.environ.get('TAB_DIRECTOR_EMAIL')

if os.environ.get('DJANGO_SECRET_KEY', ''):
    SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# https://docs.djangoproject.com/en/3.0/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['*']

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# ==============================================================================
# Postgres
# ==============================================================================

# Parse database configuration from $DATABASE_URL
DATABASES = {
    'default': dj_database_url.config(
        # Feel free to alter this value to suit your needs.
        default='postgresql://postgres:postgres@localhost:5432/mysite',
        conn_max_age=600
    )
}

# ==============================================================================
# Channels & cache (PostgreSQL by default; optional Redis)
# ==============================================================================

USE_REDIS_CHANNELS_CACHE = _truthy_env('TABBYCAT_USE_REDIS_CHANNELS_CACHE')

if USE_REDIS_CHANNELS_CACHE:
    REDIS_HOST = os.environ.get('REDIS_HOST')
    REDIS_PORT = os.environ.get('REDIS_PORT')

    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': 'redis://' + REDIS_HOST + ':' + REDIS_PORT,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'SOCKET_CONNECT_TIMEOUT': 5,
                'SOCKET_TIMEOUT': 60,
                'IGNORE_EXCEPTIONS': True,
            },
        },
    }

    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                'hosts': ['redis://' + REDIS_HOST + ':' + REDIS_PORT],
                'group_expiry': 10800,
            },
        },
    }
else:
    DATABASES['channels_postgres'] = copy.deepcopy(DATABASES['default'])
    CACHES = postgres_database_cache()
    CHANNEL_LAYERS = postgres_channel_layers(copy.deepcopy(DATABASES['default']))

# ==============================================================================
# Sentry
# ==============================================================================

if not os.environ.get('DISABLE_SENTRY'):
    DISABLE_SENTRY = False
    _sentry_integrations = [
        DjangoIntegration(),
        LoggingIntegration(event_level=logging.WARNING),
    ]
    if USE_REDIS_CHANNELS_CACHE:
        from sentry_sdk.integrations.redis import RedisIntegration

        _sentry_integrations.append(RedisIntegration())
    sentry_sdk.init(
        dsn="https://6bf2099f349542f4b9baf73ca9789597@o85113.ingest.sentry.io/185382",
        integrations=_sentry_integrations,
        send_default_pii=True,
        release=TABBYCAT_VERSION,
    )
