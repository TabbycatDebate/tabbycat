import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# This application object is used by the development server
# as well as any WSGI server configured to use this file.

from django.core.wsgi import get_wsgi_application
from django.conf import settings
from whitenoise.django import DjangoWhiteNoise


# With thanks to https://gist.github.com/Chronial/45ce9f33615a3b24c51f
class DjangoCompressWhiteNoise(DjangoWhiteNoise):
    def __call__(self, environ, start_response):
        # Handle files generated on the fly by django-compressor
        url = environ['PATH_INFO']
        if url.startswith(self.static_prefix) and url not in self.files:
            if self.is_compressed_file(url):
                self.files[url] = self.find_file(url)

        return super().__call__(environ, start_response)

    def is_compressed_file(self, url):
        if not url.startswith(self.static_prefix):
            return False
        path = url[len(self.static_prefix):]
        return path.startswith(settings.COMPRESS_OUTPUT_DIR + "/")

    def is_immutable_file(self, path, url):
        if self.is_compressed_file(url):
            return True
        else:
            return super().is_immutable_file(path, url)


application = get_wsgi_application()
application = DjangoCompressWhiteNoise(application)

# Fix django closing connection to MemCachier after every request (#11331)
# Added as per:
# https://devcenter.heroku.com/articles/django-memcache#optimize-performance
from django.core.cache.backends.memcached import BaseMemcachedCache
BaseMemcachedCache.close = lambda self, **kwargs: None
