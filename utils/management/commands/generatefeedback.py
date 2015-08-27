from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache

class Command(BaseCommand):

    help = "Generates random feedback"