import copy
import logging
from os import environ

import dj_database_url
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.django import DjangoIntegration

from .core import TABBYCAT_VERSION
from .postgres_channels_cache import postgres_channel_layers, postgres_database_cache


def _truthy_env(name: str) -> bool:
    return environ.get(name, '').lower() in ('1', 'true', 'yes')

# ==============================================================================
# Heroku
# ==============================================================================

# Store Tab Director Emails for reporting purposes
if environ.get('TAB_DIRECTOR_EMAIL', ''):
    TAB_DIRECTOR_EMAIL = environ.get('TAB_DIRECTOR_EMAIL')

if environ.get('DJANGO_SECRET_KEY', ''):
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
# Channels & cache (PostgreSQL by default; optional Redis)
# ==============================================================================

# Set TABBYCAT_USE_REDIS_CHANNELS_CACHE=1 and provision Redis to use the legacy
# Redis channel layer and django-redis. Matching packages live in Pipfile
# [redis-channels-cache] and are installed at deploy when this var is set.
USE_REDIS_CHANNELS_CACHE = _truthy_env('TABBYCAT_USE_REDIS_CHANNELS_CACHE')

if USE_REDIS_CHANNELS_CACHE:
    if environ.get('REDISCLOUD_URL'):
        ALT_REDIS_URL = environ.get('REDISCLOUD_URL')
    else:
        ALT_REDIS_URL = environ.get('REDIS_URL')

    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': ALT_REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'SOCKET_CONNECT_TIMEOUT': 5,
                'SOCKET_TIMEOUT': 60,
            },
        },
    }

    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                'hosts': [{
                    'address': environ.get('REDIS_URL'),
                    'ssl_cert_reqs': None,
                }],
                'group_expiry': 10800,
            },
        },
    }
else:
    DATABASES['channels_postgres'] = copy.deepcopy(DATABASES['default'])
    CACHES = postgres_database_cache()
    CHANNEL_LAYERS = postgres_channel_layers(copy.deepcopy(DATABASES['default']))

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
    EMAIL_USE_TLS = environ.get('EMAIL_USE_TLS', 'true').lower() == 'true'

elif environ.get('SENDGRID_API_KEY', ''):
    SERVER_EMAIL = environ.get('DEFAULT_FROM_EMAIL', 'root@localhost')
    DEFAULT_FROM_EMAIL = environ.get('DEFAULT_FROM_EMAIL', 'notconfigured@tabbycatsite')
    EMAIL_HOST = 'smtp.sendgrid.net'
    EMAIL_HOST_USER = 'apikey'
    EMAIL_HOST_PASSWORD = environ['SENDGRID_API_KEY']
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True

elif environ.get('SENDGRID_USERNAME', ''):
    # These settings are deprecated as of Tabbycat 2.6.0 (Ocicat).
    # When removing, also remove utils.mixins.WarnAboutLegacySendgridConfigVarsMixin and
    # templates/errors/legacy_sendgrid_warning.html (and references thereto).
    USING_LEGACY_SENDGRID_CONFIG_VARS = True
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
