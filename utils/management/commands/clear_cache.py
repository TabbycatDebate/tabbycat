from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache

class Command(BaseCommand):

    help = "Clears django's cache"

    def handle(self, *args, **options):
        cache.clear()
        self.stdout.write("Cache has been cleared")