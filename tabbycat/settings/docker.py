# ==============================================================================
# Docker
# ==============================================================================

import copy

from .postgres_channels_cache import postgres_channel_layers, postgres_database_cache

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'tabbycat',
        'USER': 'tabbycat',
        'PASSWORD': 'tabbycat',
        'HOST': 'db',
        'PORT': 5432,  # Non-standard to prevent collisions,
    },
}

DATABASES['channels_postgres'] = copy.deepcopy(DATABASES['default'])
CACHES = postgres_database_cache()
CHANNEL_LAYERS = postgres_channel_layers(copy.deepcopy(DATABASES['default']))
