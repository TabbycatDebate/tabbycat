import sys
import os

PROJECT_PATH         = os.path.dirname(os.path.abspath(__file__))
STATICFILES_DIRS = (
    os.path.join(PROJECT_PATH, 'static'),
)
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
DEBUG               = True
TEMPLATE_DEBUG      = DEBUG
DEBUG_ASSETS        = DEBUG

# ===================
# = Global Settings =
# ===================

ADMIN_MEDIA_PREFIX  = '/media/'
MEDIA_URL           = '/media/'
STATIC_URL          = '/static/'
TIME_ZONE           = 'Pacific/Auckland'
LANGUAGE_CODE       = 'en-us'
SITE_ID             = 1
USE_I18N            = True

# ===========================
# = Django-specific Modules =
# ===========================

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'debate.middleware.DebateMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.csrf",
    "django.core.context_processors.static",
    "debate.context_processors.debate_context",
    'django.core.context_processors.request',
)

INSTALLED_APPS = (
    'suit',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'debate',
    'emoji',
    'debug_toolbar',
    'gunicorn',
)

LOGIN_REDIRECT_URL = '/'

# =========
# = Cache =
# =========
def get_cache():
  import os
  try:
    os.environ['MEMCACHE_SERVERS'] = os.environ['MEMCACHIER_SERVERS'].replace(',', ';')
    os.environ['MEMCACHE_USERNAME'] = os.environ['MEMCACHIER_USERNAME']
    os.environ['MEMCACHE_PASSWORD'] = os.environ['MEMCACHIER_PASSWORD']
    return {
      'default': {
        'BACKEND': 'django_pylibmc.memcached.PyLibMCCache',
        'TIMEOUT': 500,
        'BINARY': True,
        'OPTIONS': { 'tcp_nodelay': True }
      }
    }
  except:
    return {
      'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
      }
    }

CACHES = get_cache()

# ==================
# = Configurations =
# ==================

DEBUG_TOOLBAR_PATCH_SETTINGS = False
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

# Heroku
if 'HEROKU' in os.environ:
    DEBUG = True
    # Parse database configuration from $DATABASE_URL
    import dj_database_url
    DATABASES = {'default': dj_database_url.config(default='postgres://localhost')}
    # Honor the 'X-Forwarded-Proto' header for request.is_secure()
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    # Allow all host headers
    ALLOWED_HOSTS = ['*']


# Local
try:
    from local_settings import *
except Exception as e:
    pass
