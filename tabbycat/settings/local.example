ON_LOCAL = True

# ==============================================================================
# Settings that you should specify
# ==============================================================================

DATABASES = {
    'default': {
        'ENGINE'      : 'django.db.backends.postgresql',
        'NAME'        : '',  # put your PostgreSQL database's name in here
        'USER'        : '',  # put your PostgreSQL login role's user name in here
        'PASSWORD'    : '',  # put your PostgreSQL login role's password in here
        'HOST'        : 'localhost',
        'PORT'        : '5432',
        'CONN_MAX_AGE': None,
    }
}

# Replace this with your time zone, as defined in the IANA time zone database:
# https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List
TIME_ZONE = 'Australia/Melbourne'

# ==============================================================================
# Overwrites main settings
# ==============================================================================

ADMINS              = ()
MANAGERS            = ADMINS
DEBUG               = True
DEBUG_ASSETS        = True
SECRET_KEY          = '#2q43u&tp4((4&m3i8v%w-6z6pp7m(v0-6@w@i!j5n)n15epwc'

# ==============================================================================
# Django-specific Modules
# ==============================================================================

INTERNAL_IPS = (
    '0.0.0.0',
    '127.0.0.1'
)

# ==============================================================================
# Caching
# ==============================================================================

PUBLIC_FAST_CACHE_TIMEOUT   = 0
PUBLIC_SLOW_CACHE_TIMEOUT   = 0
TAB_PAGES_CACHE_TIMEOUT     = 0

CACHES = { # Use a dummy cache in development
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
   }
}

# Use the cache with database write through for local sessions
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
