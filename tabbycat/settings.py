import os

from django.contrib.messages import constants as messages

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_ROOT = (os.path.join(BASE_DIR, 'media'), )

# ==============================================================================
# Overwritten in Local
# ==============================================================================

ADMINS = ('Philip and Chuan-Zheng', 'tabbycat@philipbelesky.com'),
MANAGERS = ADMINS
DEBUG = False
DEBUG_ASSETS = DEBUG

# ==============================================================================
# Global Settings
# ==============================================================================

MEDIA_URL = '/media/'
TIME_ZONE = 'Australia/Melbourne'
LANGUAGE_CODE = 'en-us'
USE_I18N = True
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

TABBYCAT_VERSION = '1.0.0'
TABBYCAT_CODENAME = 'Devon Rex'
READTHEDOCS_VERSION = 'v1.0.0'

# ==============================================================================
# Django-specific Module
# ==============================================================================

MIDDLEWARE_CLASSES = (
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # For Static Files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'utils.middleware.DebateMiddleware')

TABBYCAT_APPS = ('actionlog',
                 'adjallocation',
                 'adjfeedback',
                 'availability',
                 'breakqual',
                 'divisions',
                 'draw',
                 'motions',
                 'options',
                 'participants',
                 'printing',
                 'results',
                 'tournaments',
                 'venues',
                 'utils',
                 'standings',
                 'importer', )

INSTALLED_APPS = (
    'jet',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django_gulp',  # Asset compilation; must be before staticfiles
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.messages') \
    + TABBYCAT_APPS + (
    'dynamic_preferences',
    'django_extensions')  # For Secret Generation Command

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
                # For Jet
                'django.template.context_processors.request',
                # For tournament config vars
                'utils.context_processors.debate_context',
                # For nav highlights
                'utils.context_processors.get_menu_highlight',
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

PUBLIC_PAGE_CACHE_TIMEOUT = int(os.environ.get('PUBLIC_PAGE_CACHE_TIMEOUT',
                                60 * 1))
TAB_PAGES_CACHE_TIMEOUT = int(os.environ.get('TAB_PAGES_CACHE_TIMEOUT',
                                60 * 120))

# Default non-heroku cache is to use local memory
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake'
    }
}

# Use the cache for sessions rather than the db
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

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
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# When running server side always use build not watch
GULP_PRODUCTION_COMMAND = "npm run gulp build -- --production"
GULP_DEVELOP_COMMAND = "npm run gulp build -- --development"

# ==============================================================================
# Logging
# ==============================================================================

if os.environ.get('SENDGRID_USERNAME', ''):
    SERVER_EMAIL = os.environ['SENDGRID_USERNAME']
    DEFAULT_FROM_EMAIL = os.environ['SENDGRID_USERNAME']
    EMAIL_HOST = 'smtp.sendgrid.net'
    EMAIL_HOST_USER = os.environ['SENDGRID_USERNAME']
    EMAIL_HOST_PASSWORD = os.environ['SENDGRID_PASSWORD']
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True

if os.environ.get('DEBUG', ''):
    DEBUG = bool(int(os.environ['DEBUG']))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            # Only send emails to admins when debug is false
            '()': 'django.utils.log.RequireDebugFalse',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'mail_admins': {
            # Any log item marked ERROR or higher will be sent to admins
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
        'django.request': {
            # Pass all ERRORS to mail_admins handler
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
    'formatters': {
        'standard': {
            'format': '[%(asctime)s] %(levelname)s %(name)s: %(message)s',
            'datefmt': '%d/%b/%Y %H:%M:%S'
        },
    },
}

for app in TABBYCAT_APPS:
    LOGGING['loggers'][app] = {
        'handlers': ['console'],
        'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG' if DEBUG else 'INFO'),
    }

# ==============================================================================
# Messages
# ==============================================================================

MESSAGE_TAGS = {messages.ERROR: 'danger', }

# ==============================================================================
# Heroku
# ==============================================================================

# Get key from heroku config env else use a fall back
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY', '#2q43u&tp4((4&m3i8v%w-6z6pp7m(v0-6@w@i!j5n)n15epwc')

# Parse database configuration from $DATABASE_URL
try:
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(default='postgres://localhost')
    }
except:
    pass

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# Allow all host headers
ALLOWED_HOSTS = ['*']

if os.environ.get('MEMCACHIER_SERVERS', ''):
    try:
        os.environ['MEMCACHE_SERVERS'] = os.environ[
            'MEMCACHIER_SERVERS'].replace(',', ';')
        os.environ['MEMCACHE_USERNAME'] = os.environ['MEMCACHIER_USERNAME']
        os.environ['MEMCACHE_PASSWORD'] = os.environ['MEMCACHIER_PASSWORD']
        CACHES = {
            'default': {
                'BACKEND': 'django_pylibmc.memcached.PyLibMCCache',
                'TIMEOUT': 36000,
                'BINARY': True,
                'OPTIONS': {  # Maps to pylibmc "behaviors"
                    # Enable faster IO
                    'no_block': True,
                    'tcp_nodelay': True,
                },
                # Timeout for set/get requests
                '_poll_timeout': 2000,
            }
        }
    except:
        CACHES = {
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
            }
        }

if os.environ.get('DEBUG', ''):
    DEBUG = bool(int(os.environ['DEBUG']))
    TEMPLATES[0]['OPTIONS']['debug'] = True

# ==============================================================================
# Travis CI
# ==============================================================================

FIXTURE_DIRS = (os.path.join(os.path.dirname(BASE_DIR), 'data', 'fixtures'), )

if os.environ.get('TRAVIS', '') == 'true':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'USER': 'postgres',
            'PASSWORD': '',
            'HOST': 'localhost',
            'PORT': '',
        }
    }

# ==============================================================================
# Local Overrides
# ==============================================================================

try:
    LOCAL_SETTINGS
except NameError:
    try:
        from local_settings import *   # flake8: noqa
    except ImportError:
        pass
