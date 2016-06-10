from django.core.management.base import BaseCommand

from ...models import ActionLogEntry


class Command(BaseCommand):

    help = "Prints every entry in the action log (for all tournaments)"

    def handle(self, **options):
        for al in ActionLogEntry.objects.order_by('-timestamp'):
            self.stdout.write(repr(al))
