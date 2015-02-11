import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# This application object is used by the development server
# as well as any WSGI server configured to use this file.
# Cling for static files in production, as per
# https://devcenter.heroku.com/articles/django-assets
from django.core.wsgi import get_wsgi_application
from dj_static import Cling

application = Cling(get_wsgi_application())

# Heroku
if 'HEROKU' in os.environ:
    # Fix django closing connection to MemCachier after every request (#11331)
    # Added as per:
    # https://devcenter.heroku.com/articles/django-memcache#optimize-performance
    from django.core.cache.backends.memcached import BaseMemcachedCache
    BaseMemcachedCache.close = lambda self, **kwargs: None