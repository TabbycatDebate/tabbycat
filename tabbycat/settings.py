import os

from django.contrib.messages import constants as messages
from django.utils.translation import gettext_lazy as _


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ==============================================================================
# Overwritten in local_settings.py
# ==============================================================================

ADMINS = ('Philip and Chuan-Zheng', 'tabbycat@philipbelesky.com'),
MANAGERS = ADMINS
DEBUG = bool(int(os.environ['DEBUG'])) if 'DEBUG' in os.environ else False
DEBUG_ASSETS = DEBUG

# ==============================================================================
# Version
# ==============================================================================

TABBYCAT_VERSION = '2.2.0b'
TABBYCAT_CODENAME = 'Khao Manee'
READTHEDOCS_VERSION = 'v2.2.0'

# ==============================================================================
# Internationalization and Localization
# ==============================================================================

USE_I18N = True
USE_TZ = True
USE_L10N = True
LANGUAGE_CODE = 'en'
TIME_ZONE = os.environ.get('TIME_ZONE', 'Australia/Melbourne')

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

# Languages that should be available in the switcher
LANGUAGES = [
    ('ar', _('Arabic')),
    ('en', _('English')),
    ('es', _('Spanish')),
    ('fr', _('French')),
    ('ja', _('Japanese')),
]

STATICI18N_ROOT = os.path.join(BASE_DIR, "locale")

FORMAT_MODULE_PATH = [
    'utils.formats',
]

# ==============================================================================
# Django-specific Module
# ==============================================================================

MIDDLEWARE = [
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # For Static Files
    'django.contrib.sessions.middleware.SessionMiddleware',
    # User language preferences; must be after Session
    'django.middleware.locale.LocaleMiddleware',
    # Set Etags; i.e. cached requests not on network; must precede Common
    'django.middleware.http.ConditionalGetMiddleware',
    'django.middleware.common.CommonMiddleware',
    # Must be after SessionMiddleware
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.common.CommonMiddleware',
    # Must be after SessionMiddleware
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'utils.middleware.DebateMiddleware'
]

TABBYCAT_APPS = (
    'actionlog',
    'adjallocation',
    'adjfeedback',
    'availability',
    'breakqual',
    'checkins',
    'divisions',
    'draw',
    'motions',
    'options',
    'participants',
    'printing',
    'privateurls',
    'results',
    'tournaments',
    'venues',
    'utils',
    'users',
    'standings',
    'notifications',
    'importer'
)

INSTALLED_APPS = (
    # Scout should be listed first
    'scout_apm.django', 'jet' if os.environ.get('SCOUT_MONITOR') is True else 'jet',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'channels', # For Websockets / real-time connections (above whitenoise)
    'whitenoise.runserver_nostatic',  # Use whitenoise with runserver
    'raven.contrib.django.raven_compat',  # Client for Sentry error tracking
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django_summernote',  # Keep above our apps; as we unregister an admin model
    'django.contrib.messages') \
    + TABBYCAT_APPS + (
    'dynamic_preferences',
    'django_extensions',  # For Secret Generation Command
    'gfklookupwidget',
    'formtools',
    'statici18n' # Compile js translations as static file; saving requests
)

ROOT_URLCONF = 'urls'
LOGIN_REDIRECT_URL = '/'

# ==============================================================================
# Templates
# ==============================================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',  # for Jet
                'utils.context_processors.debate_context',  # for tournament config vars
                'django.template.context_processors.i18n'  # for serving static language translations
            ],
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ]),
            ]
        }
    }
]

# ==============================================================================
# Caching
# ==============================================================================

PUBLIC_FAST_CACHE_TIMEOUT = int(os.environ.get('PUBLIC_FAST_CACHE_TIMEOUT', 60 * 1))
PUBLIC_SLOW_CACHE_TIMEOUT = int(os.environ.get('PUBLIC_SLOW_CACHE_TIMEOUT', 60 * 3.5))
TAB_PAGES_CACHE_TIMEOUT = int(os.environ.get('TAB_PAGES_CACHE_TIMEOUT', 60 * 120))

# Default non-heroku cache is to use local memory
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

# ==============================================================================
# Static Files and Compilation
# ==============================================================================

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'), )

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Whitenoise Gzipping and unique names
STATICFILES_STORAGE = 'utils.misc.SquashedWhitenoiseStorage'
# Serve files that must be at root (robots; favicon) from this folder
WHITENOISE_ROOT = os.path.join(BASE_DIR, 'static/root')

# ==============================================================================
# Logging
# ==============================================================================

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

if os.environ.get('SENDGRID_USERNAME', ''):
    SERVER_EMAIL = os.environ['SENDGRID_USERNAME']
    DEFAULT_FROM_EMAIL = os.environ['SENDGRID_USERNAME']
    EMAIL_HOST = 'smtp.sendgrid.net'
    EMAIL_HOST_USER = os.environ['SENDGRID_USERNAME']
    EMAIL_HOST_PASSWORD = os.environ['SENDGRID_PASSWORD']
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'sentry': {
            'level': 'WARNING',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
        'django.request': {
            'handlers': ['sentry'],
            'level': 'ERROR',
        },
        'raven': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False,
        },
    },
    'formatters': {
        'standard': {
            'format': '[%(asctime)s] %(levelname)s %(name)s: %(message)s',
        },
    },
}

for app in TABBYCAT_APPS:
    LOGGING['loggers'][app] = {
        'handlers': ['console', 'sentry'],
        'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
    }
# ==============================================================================

# Scout
# ==============================================================================

SCOUT_NAME = "Tabbycat"

# ==============================================================================
# Sentry
# ==============================================================================

DISABLE_SENTRY = True

if 'DATABASE_URL' in os.environ and not DEBUG:
    DISABLE_SENTRY = False  # Only log JS errors in production on heroku

    RAVEN_CONFIG = {
        'dsn': 'https://6bf2099f349542f4b9baf73ca9789597:57b33798cc2a4d44be67456f2b154067@sentry.io/185382',
        'release': TABBYCAT_VERSION,
    }

    # Custom implementation makes the user ID the e-mail address, rather than the primary key
    SENTRY_CLIENT = 'utils.raven.TabbycatRavenClient'

# ==============================================================================
# Messages
# ==============================================================================

MESSAGE_TAGS = {messages.ERROR: 'danger', }

# ==============================================================================
# Summernote (WYSWIG)
# ==============================================================================

SUMMERNOTE_CONFIG = {
    'width': '100%',
    'height': '480',
    'toolbar': [
        ['style', ['bold', 'italic', 'underline', 'fontsize', 'color', 'clear']],
        ['para', ['ul', 'ol']],
        ['insert', ['link', 'picture', 'video', 'hr']],
        ['misc', ['undo', 'redo', 'codeview']],
        ['help', ['help']]
    ],
    'disable_upload': True,
    'iframe': True, # When django-summernote supports Bootstrap4 change this
}

# ==============================================================================
# Channels
# ==============================================================================

ASGI_APPLICATION = "routing.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

# ==============================================================================
# Heroku
# ==============================================================================

# Get key from heroku config env else use a fall back
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY', r'#2q43u&tp4((4&m3i8v%w-6z6pp7m(v0-6@w@i!j5n)n15epwc')

# Parse database configuration from $DATABASE_URL
# Note connection max age is in seconds
try:
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(default='postgres://localhost', conn_max_age=10)
    }
except:
    pass

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Require HTTPS
if 'DJANGO_SECRET_KEY' in os.environ and os.environ.get('DISABLE_HTTPS_REDIRECTS', '') != 'disable':
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# Allow all host headers
ALLOWED_HOSTS = ['*']

# Store Tab Director Emails for reporting purposes
if 'TAB_DIRECTOR_EMAIL' in os.environ:
    TAB_DIRECTOR_EMAIL = os.environ.get('TAB_DIRECTOR_EMAIL', '')

# Redis Services
if os.environ.get('REDIS_URL', ''):
    try:
        CACHES = {
            "default": {
                "BACKEND": "django_redis.cache.RedisCache",
                "LOCATION": os.environ.get('REDIS_URL'),
                "OPTIONS": {
                    "CLIENT_CLASS": "django_redis.client.DefaultClient",
                    "IGNORE_EXCEPTIONS": True, # Don't crash on say ConnectionError due to limits
                }
            }
        }
        CHANNEL_LAYERS = {
            "default": {
                "BACKEND": "channels_redis.core.RedisChannelLayer",
                "CONFIG": {
                    "hosts": [os.environ.get('REDIS_URL')],
                },
            },
        }
    except:
        pass

# ==============================================================================
# Travis CI
# ==============================================================================

FIXTURE_DIRS = (os.path.join(os.path.dirname(BASE_DIR), 'data', 'fixtures'), )

if os.environ.get('TRAVIS', '') == 'true':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'USER': 'postgres',
            'PASSWORD': '',
            'HOST': 'localhost',
            'PORT': '',
        }
    }

# ==============================================================================
# Debug Toolbar
# ==============================================================================

DEBUG_TOOLBAR_PATCH_SETTINGS = False

DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
)

DEBUG_TOOLBAR_CONFIG = {
    'JQUERY_URL': '/static/js/vendor/jquery.js', # Enables offline work
    'SHOW_COLLAPSED': True
}

# Must default to false; usually overridden in local_settings
ENABLE_DEBUG_TOOLBAR = False

# That said provide a flag to turn it on in Heroku
if 'DEBUG_TOOLBAR' in os.environ and bool(int(os.environ['DEBUG_TOOLBAR'])):
    ENABLE_DEBUG_TOOLBAR = True
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware',]
    INSTALLED_APPS += ('debug_toolbar',)
    # Override check for internal IPs (and DEBUG=1) on Heroku
    DEBUG_TOOLBAR_CONFIG['SHOW_TOOLBAR_CALLBACK'] = 'settings.show_toolbar'


def show_toolbar(request):
    return request.user.is_staff

# ==============================================================================
# Local Overrides and Docker
# ==============================================================================

# Hide league-related configuration options unless explicitly enabled
LEAGUE = bool(int(os.environ['LEAGUE'])) if 'LEAGUE' in os.environ else False

if os.environ.get('IN_DOCKER', '') and bool(int(os.environ['IN_DOCKER'])):
    DEBUG = True # Just to be sure
    ALLOWED_HOSTS = ["*"]
    DATABASES = {
        'default': {
             'ENGINE': 'django.db.backends.postgresql',
             'NAME': 'tabbycat',
             'USER': 'tabbycat',
             'PASSWORD': 'tabbycat',
             'HOST': 'db',
             'PORT': 5432, # Non-standard to prevent collisions
        }
    }
else:
    try:
        LOCAL_SETTINGS
    except NameError:
        try:
            from local_settings import *   # noqa
        except ImportError:
            pass
