from django.core.management.base import BaseCommand, CommandError
from django.core.urlresolvers import reverse
from django.utils.cache import get_cache_key
from django.core.cache import cache
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("path")

    def handle(self, *args, **options):
        path = options['path']
        factory = RequestFactory()
        request = factory.get(path)
        request.user = AnonymousUser()
        key = get_cache_key(request, key_prefix=None)
        if not key:
            self.stdout.write("Could not find key for " + str(path) + "\n")
            return
        if not cache.get(key):
            self.stdout.write("Could not find key " + str(key) + "\n")
            return
        if key and cache.get(key):
            cache.delete(key)
            self.stdout.write("Deleted cache for key " + str(key) + "\n")
