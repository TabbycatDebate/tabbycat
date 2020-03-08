# ==============================================================================
# Docker
# ==============================================================================

DEBUG = True # Just to be sure
ALLOWED_HOSTS = ["*"]

DATABASES = {
    'default': {
         'ENGINE': 'django.db.backends.postgresql',
         'NAME': 'tabbycat',
         'USER': 'tabbycat',
         'PASSWORD': 'tabbycat',
         'HOST': 'db',
         'PORT': 5432, # Non-standard to prevent collisions,
    }
}
