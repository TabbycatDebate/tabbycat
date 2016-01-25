import sys
import os
import urllib.parse

PROJECT_PATH        = os.path.dirname(os.path.abspath(__file__))
STATICFILES_DIRS    = (os.path.join(PROJECT_PATH, 'static'),)
STATIC_ROOT         = 'staticfiles'
STATIC_URL          = '/static/'
MEDIA_ROOT          = (os.path.join(PROJECT_PATH, 'media'),)
SECRET_KEY          = '#2q43u&tp4((4&m3i8v%w-6z6pp7m(v0-6@w@i!j5n)n15epwc'

# ========================
# = Overwritten in Local =
# ========================

ADMINS              = ('Philip and CZ', 'tabbycat@philipbelesky.com')
MANAGERS            = ADMINS
DEBUG               = False
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

TABBYCAT_APPS = (
    'actionlog',
    'adjallocation',
    'adjfeedback',
    'availability',
    'breakqual',
    'draw',
    'motions',
    'options',
    'participants',
    'results',
    'tournaments',
    'venues',
    'utils',
    'standings',
    'importer',
)

INSTALLED_APPS = (
    'jet',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.messages') \
    + TABBYCAT_APPS + (
    'dynamic_preferences',
    'static_precompiler'
    )


LOGIN_REDIRECT_URL = '/'

MIGRATION_MODULES = {
    'blog': 'blog.db_migrations'
}

# ===========
# = Templates =
# ===========

TEMPLATES = [
    {
        'BACKEND':      'django.template.backends.django.DjangoTemplates',
        'DIRS':         [os.path.join(PROJECT_PATH, 'templates')],
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',           # For Jet
                'utils.context_processors.debate_context',              # For tournament config vars
                'utils.context_processors.get_menu_highlight',          # For nav highlight
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

# ===========
# = Caching =
# ===========

PUBLIC_PAGE_CACHE_TIMEOUT = int(os.environ.get('PUBLIC_PAGE_CACHE_TIMEOUT', 60 * 1))
TAB_PAGES_CACHE_TIMEOUT = int(os.environ.get('TAB_PAGES_CACHE_TIMEOUT', 60 * 120))

# Default non-heroku cache is to use local memory
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake'
    }
}

# Use the cache for sessions rather than the db
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

# =============
# = Pipelines =
# =============

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'static_precompiler.finders.StaticPrecompilerFinder',
)

STATIC_PRECOMPILER_COMPILERS = (
    ('static_precompiler.compilers.libsass.SCSS', {"sourcemap_enabled": True, "load_paths": ["/scss"]}),
)

# ===========
# = Logging =
# ===========

if os.environ.get('DEBUG', ''):
    DEBUG = bool(int(os.environ['DEBUG']))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
    },
}

for app in TABBYCAT_APPS:
    LOGGING['loggers'][app] = {
        'handlers': ['console'],
        'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG' if DEBUG else 'INFO'),
    }


# ===========
# = Heroku  =
# ===========

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

if os.environ.get('SENDGRID_USERNAME', ''):
    EMAIL_HOST= 'smtp.sendgrid.net'
    EMAIL_HOST_USER = os.environ['SENDGRID_USERNAME']
    EMAIL_HOST_PASSWORD = os.environ['SENDGRID_PASSWORD']
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True

# =============
# = Travis CI =
# =============

if os.environ.get('TRAVIS', '') == 'true':
    DATABASES = {
        'default': {
            'ENGINE':   'django.db.backends.postgresql_psycopg2',
            'USER':     'postgres',
            'PASSWORD': '',
            'HOST':     'localhost',
            'PORT':     '',
        }
    }

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
