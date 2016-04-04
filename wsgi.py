# Needed for WSGI Callable
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# Needed for waitress/gunicorn serving
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Fix django closing connection to MemCachier after every request (#11331)
# Added as per:
# https://devcenter.heroku.com/articles/django-memcache#optimize-performance
from django.core.cache.backends.memcached import BaseMemcachedCache
BaseMemcachedCache.close = lambda self, **kwargs: None
