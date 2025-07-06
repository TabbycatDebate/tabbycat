import logging
from os import environ

from .core import TABBYCAT_VERSION

# ==============================================================================
# Digital Ocean Production Settings
# ==============================================================================

# Store Tab Director Emails for reporting purposes
if environ.get('TAB_DIRECTOR_EMAIL', ''):
    TAB_DIRECTOR_EMAIL = environ.get('TAB_DIRECTOR_EMAIL')

if environ.get('DJANGO_SECRET_KEY', ''):
    SECRET_KEY = environ.get('DJANGO_SECRET_KEY')

# Allow your domain and IP
ALLOWED_HOSTS = [
    '159.223.204.248',  # Your droplet IP
    'localhost',
    '127.0.0.1',
    '.yourdomain.com',  # Add your domain when you set it up
]

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# For production, enable HTTPS redirects (comment out for initial setup)
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True

# ==============================================================================
# PostgreSQL Database Configuration
# ==============================================================================

# Use the provided external database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'tab_2yw0',
        'USER': 'tab',
        'PASSWORD': '57yqNclrMENfxxJuYmbBJ0u26FdDzOkB',
        'HOST': 'dpg-d1l186h5pdvs73bd0nv0-a.oregon-postgres.render.com',
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}

# ==============================================================================
# Redis Configuration (Local Redis for caching and channels)
# ==============================================================================

REDIS_URL = environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0')

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 60,
        },
    },
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [REDIS_URL],
            "group_expiry": 10800,  # 3 hours
        },
    },
}

# ==============================================================================
# Static Files Configuration
# ==============================================================================

STATIC_ROOT = '/var/www/tabbycat/static'
MEDIA_ROOT = '/var/www/tabbycat/media'

# ==============================================================================
# Logging Configuration
# ==============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/tabbycat/django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# ==============================================================================
# Security Settings
# ==============================================================================

# Enable debug only if explicitly set
DEBUG = bool(int(environ.get('DEBUG', '0')))

# Disable debug toolbar in production
ENABLE_DEBUG_TOOLBAR = False

# Email configuration (optional - configure if you need email functionality)
if environ.get('EMAIL_HOST'):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = environ.get('EMAIL_HOST')
    EMAIL_PORT = int(environ.get('EMAIL_PORT', '587'))
    EMAIL_USE_TLS = bool(int(environ.get('EMAIL_USE_TLS', '1')))
    EMAIL_HOST_USER = environ.get('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = environ.get('EMAIL_HOST_PASSWORD')
    DEFAULT_FROM_EMAIL = environ.get('DEFAULT_FROM_EMAIL', 'noreply@yourdomain.com')
