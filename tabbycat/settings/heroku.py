from os import environ

from core import *

import dj_database_url


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
    'default': dj_database_url.config(default='postgres://localhost')
}

# ==============================================================================
# Redis
# ==============================================================================

# Set the connection pool to match Heroku's free tier; but allow for upgrades
if environ.get('REDIS_POOL_SIZE'):
    REDIS_POOL_SIZE = int(environ.get('REDIS_POOL_SIZE'))
else:
    REDIS_POOL_SIZE = 19

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": environ.get('REDIS_URL'),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # Don't crash on say ConnectionError due to limits
            "IGNORE_EXCEPTIONS": True,
            # Limit connections to stick within limits of the Heroku plan
            "CONNECTION_POOL_KWARGS": {"max_connections": 100}
        }
    }
}

# Use separate Redis addon for channels to reduce chance of connection limits
# With fallback for Tabbykitten installs (no addons) or for pre-2.2 instances
if environ.get('REDISCLOUD_URL'):
    CHANNEL_HOSTS = [environ.get('REDISCLOUD_URL')]
else:
    CHANNEL_HOSTS = [environ.get('REDIS_URL')]

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": CHANNEL_HOSTS, # RedisChannelLayer should pool by default
        },
    },
}

# ==============================================================================
# SendGrid
# ==============================================================================

if environ.get('SENDGRID_USERNAME', ''):
    SERVER_EMAIL = environ['SENDGRID_USERNAME']
    DEFAULT_FROM_EMAIL = environ['SENDGRID_USERNAME']
    EMAIL_HOST = 'smtp.sendgrid.net'
    EMAIL_HOST_USER = environ['SENDGRID_USERNAME']
    EMAIL_HOST_PASSWORD = environ['SENDGRID_PASSWORD']
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True

# ==============================================================================
# Sentry
# ==============================================================================

if environ.get('DISABLE_SENTRY'):
    DISABLE_SENTRY = True
else:
    DISABLE_SENTRY = False

RAVEN_CONFIG = {
    'dsn': 'https://6bf2099f349542f4b9baf73ca9789597:57b33798cc2a4d44be67456f2b154067@sentry.io/185382',
    'release': TABBYCAT_VERSION,
}

# Custom implementation makes the user ID the e-mail address, rather than the primary key
SENTRY_CLIENT = 'utils.raven.TabbycatRavenClient'

# ==============================================================================
# Scout
# ==============================================================================

SCOUT_NAME = "Tabbycat"

if environ.get('SCOUT_MONITOR'):
    # Scout should be listed first; prepend it to the existing list if added
    INSTALLED_APPS = ('scout_apm.django', *INSTALLED_APPS)
