import os

from django.contrib.messages import constants as messages
from django.utils.translation import gettext_lazy as _


BASE_DIR = os.path.dirname(os.path.abspath(os.path.join(__file__, os.pardir)))
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ==============================================================================
# Overwritten in local.py or heroku.py
# ==============================================================================

ADMINS = ('Philip and Chuan-Zheng', 'tabbycat@philipbelesky.com'),
MANAGERS = ADMINS
DEBUG = bool(int(os.environ['DEBUG'])) if 'DEBUG' in os.environ else False
ENABLE_DEBUG_TOOLBAR = False # Must default to false
DISABLE_SENTRY = True # Must default to false
SECRET_KEY = r'#2q43u&tp4((4&m3i8v%w-6z6pp7m(v0-6@w@i!j5n)n15epwc'

# Hide league-related configuration options unless explicitly enabled
LEAGUE = bool(int(os.environ['LEAGUE'])) if 'LEAGUE' in os.environ else False

# ==============================================================================
# Version
# ==============================================================================

TABBYCAT_VERSION = '2.3.2'
TABBYCAT_CODENAME = 'LaPerm'
READTHEDOCS_VERSION = 'v2.3.2'

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
    ('pt', _('Portuguese')),
]

STATICI18N_ROOT = os.path.join(BASE_DIR, "locale")

FORMAT_MODULE_PATH = [
    'utils.formats',
]

# ==============================================================================
# Django-specific Modules
# ==============================================================================

MIDDLEWARE = [
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.security.SecurityMiddleware',
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
    'jet',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'channels', # For Websockets / real-time connections (above whitenoise)
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django_summernote',  # Keep above our apps; as we unregister an admin model
    'django.contrib.messages') \
    + TABBYCAT_APPS + (
    'dynamic_preferences',
    'django_extensions',  # For Secret Generation Command
    'gfklookupwidget',
    'formtools',
    'statici18n', # Compile js translations as static file; saving requests
    'polymorphic',
)

ROOT_URLCONF = 'urls'
LOGIN_REDIRECT_URL = '/'
FIXTURE_DIRS = (os.path.join(os.path.dirname(BASE_DIR), 'data', 'fixtures'), )

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

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# ==============================================================================
# Logging
# ==============================================================================

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
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
        'handlers': ['console'],
        'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
    }

# ==============================================================================
# Messages
# ==============================================================================

MESSAGE_TAGS = {messages.ERROR: 'danger', }

# ==============================================================================
# Summernote (WYSWIG)
# ==============================================================================

SUMMERNOTE_THEME = 'bs4' # Bootstrap 4

SUMMERNOTE_CONFIG = {
    'width': '100%',
    'height': '480',
    'toolbar': [
        ['style', ['bold', 'italic', 'underline', 'fontsize', 'color', 'clear']],
        ['para', ['ul', 'ol']],
        ['insert', ['link', 'picture']],
        ['misc', ['undo', 'redo', 'codeview']],
    ],
    'disable_upload': True,
    'iframe': True, # Necessary; if just to compartmentalise jQuery dependency
}

# ==============================================================================
# Database
# ==============================================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
    }
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
# Dynamic preferences
# ==============================================================================

DYNAMIC_PREFERENCES = {
    'REGISTRY_MODULE': 'preferences',
}
