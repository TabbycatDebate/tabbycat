import os

from django.core.cache.backends.memcached import BaseMemcachedCache
from django.core.wsgi import get_wsgi_application

# Needed for WSGI Callable
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# Needed for waitress/gunicorn serving
application = get_wsgi_application()

# Fix django closing connection to MemCachier after every request (#11331)
# Added as per:
# https://devcenter.heroku.com/articles/django-memcache#optimize-performance
BaseMemcachedCache.close = lambda self, **kwargs: None
