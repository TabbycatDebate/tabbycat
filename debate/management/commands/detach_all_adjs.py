from django.core.management.base import BaseCommand, CommandError
import debate.models as m

class Command(BaseCommand):
    help = 'Detach all adjudicators from all tournaments'

    def handle(self, *args, **options):

        m.Adjudicator.objects.all().update(tournament=None)