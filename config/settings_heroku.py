import os

import dj_database_url

from settings.base import INSTALLED_APPS


# ==============================================================================
# Heroku
# ==============================================================================

# Store Tab Director Emails for reporting purposes
if 'TAB_DIRECTOR_EMAIL' in os.environ:
    TAB_DIRECTOR_EMAIL = os.environ.get('TAB_DIRECTOR_EMAIL', '')

# Get key from heroku config env else use a fall back
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY', r'#2q43u&tp4((4&m3i8v%w-6z6pp7m(v0-6@w@i!j5n)n15epwc')

# Allow all host headers
ALLOWED_HOSTS = ['*']

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Require HTTPS
if 'DJANGO_SECRET_KEY' in os.environ and os.environ.get('DISABLE_HTTPS_REDIRECTS', '') != 'disable':
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
if os.environ.get('REDIS_POOL_SIZE'):
    REDIS_POOL_SIZE = int(os.environ.get('REDIS_POOL_SIZE'))
else:
    REDIS_POOL_SIZE = 19

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ.get('REDIS_URL'),
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
if os.environ.get('REDISCLOUD_URL'):
    CHANNEL_HOSTS = [os.environ.get('REDISCLOUD_URL')]
else:
    CHANNEL_HOSTS = [os.environ.get('REDIS_URL')]

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

if os.environ.get('SENDGRID_USERNAME', ''):
    SERVER_EMAIL = os.environ['SENDGRID_USERNAME']
    DEFAULT_FROM_EMAIL = os.environ['SENDGRID_USERNAME']
    EMAIL_HOST = 'smtp.sendgrid.net'
    EMAIL_HOST_USER = os.environ['SENDGRID_USERNAME']
    EMAIL_HOST_PASSWORD = os.environ['SENDGRID_PASSWORD']
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True

# ==============================================================================
# Instrumentation
# ==============================================================================

SCOUT_NAME = "Tabbycat"

if os.environ.get('SCOUT_MONITOR'):
    # Scout should be listed first; prepend it to the existing list if added
    INSTALLED_APPS = ('scout_apm.django', *INSTALLED_APPS)
