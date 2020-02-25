# ==============================================================================
# Travis CI
# ==============================================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'USER': 'postgres',
        'NAME': 'travisci',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '',
    },
}
