import sys
import os
import urlparse

PROJECT_PATH        = os.path.dirname(os.path.abspath(__file__))
STATICFILES_DIRS    = (os.path.join(PROJECT_PATH, 'static'),)
STATIC_ROOT         = 'staticfiles'
STATIC_URL          = '/static/'
TEMPLATE_DIRS       = (os.path.join(PROJECT_PATH, 'templates'),)
MEDIA_ROOT          = (os.path.join(PROJECT_PATH, 'media'),)
SECRET_KEY          = '#2q43u&tp4((4&m3i8v%w-6z6pp7m(v0-6@w@i!j5n)n15epwc'

# ===================
# = Overwritten in Local =
# ===================

ADMINS              = ('Test', 'test@test.com')
MANAGERS            = ADMINS
DEBUG               = False
TEMPLATE_DEBUG      = DEBUG
DEBUG_ASSETS        = DEBUG

# ===================
# = Global Settings =
# ===================

ADMIN_MEDIA_PREFIX  = '/media/'
MEDIA_URL           = '/media/'
STATIC_URL          = '/static/'
TIME_ZONE           = 'Australia/Melbourne'
LANGUAGE_CODE       = 'en-us'
USE_I18N            = True
TEST_RUNNER         = 'django.test.runner.DiscoverRunner'

# ===========================
# = Django-specific Modules =
# ===========================

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'utils.middleware.DebateMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.csrf",
    "django.core.context_processors.static",
    "utils.context_processors.debate_context", # For tournament config vars
    "utils.context_processors.get_menu_highlight", # For nav highlights
    'django.core.context_processors.request', # For SUIT
)

INSTALLED_APPS = (
    'suit',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.messages',
    'action_log',
    'allocations',
    'availability',
    'breaking',
    'draws',
    'feedback',
    'motions',
    'options',
    'participants',
    'results',
    'standings',
    'tournaments',
    'venues',
    'utils', # So management commands can be used
    'compressor',
    'cachalot',
)

LOGIN_REDIRECT_URL = '/'

# =========
# = Caching =
# =========

PUBLIC_PAGE_CACHE_TIMEOUT = int(os.environ.get('PUBLIC_PAGE_CACHE_TIMEOUT', 60 * 1))
TAB_PAGES_CACHE_TIMEOUT = int(os.environ.get('TAB_PAGES_CACHE_TIMEOUT', 60 * 120))

# Default non-heroku cache is to use local memory
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake'
    }
}

# Caching enabled for templates
TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)

# Use the cache for sessions rather than the db
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

# =========
# = Pipelines =
# =========

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # other finders..
    'compressor.finders.CompressorFinder',
)
COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'), # SASS for stylesheets
)
LIBSASS_OUTPUT_STYLE = 'nested' if DEBUG else 'compressed'
LIBSASS_SOURCE_COMMENTS = False

COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
COMPRESS_URL = STATIC_URL
COMPRESS_OFFLINE_MANIFEST = "manifest.json"
COMPRESS_ROOT = STATIC_ROOT # Absolute path written to
COMPRESS_STORAGE = 'compressor.storage.GzipCompressorFileStorage' # Gzip compression

# ===========================
# = Heroku
# ===========================

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
        os.environ['MEMCACHE_SERVERS'] = os.environ['MEMCACHIER_SERVERS'].replace(',', ';')
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
    TEMPLATE_DEBUG = DEBUG

# ===========================
# = Local Overrides
# ===========================

try:
    LOCAL_SETTINGS
except NameError:
    try:
        from local_settings import *
    except ImportError:
        pass
