from django.core.management.base import BaseCommand, CommandError
from debate.utils import populate_url_hashes
from debate.models import Tournament

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('tournament', help="Slug of tournament to generate URL hashes for")
        parser.add_argument('--teams-only', action="store_true", default=False,
            help="Only generate hashes for teams")
        parser.add_argument('--adjs-only', action="store_true", default=False,
            help="Only generate hashes for adjudicators")
        parser.add_argument('-l', '--length', type=int, default=8,
            help="Length of URL hash to generate (default 8)")
        parser.add_argument('-f', '--force', action="store_true", default=False,
            help="Overwrite existing hashes")

    def handle(self, *args, **options):
        try:
            tournament = Tournament.objects.get(slug=options['tournament'])
        except Tournament.DoesNotExist:
            raise CommandError("There is no tournament with slug %r", options['tournament'])

        self.options = options

        if not options['teams_only']:
            self.populate_url_hashes(tournament.adjudicator_set, "adjudicator")

        if not options['adjs_only']:
            self.populate_url_hashes(tournament.team_set, "team")

    def populate_url_hashes(self, relatedmanager, name):
        if not self.options['force'] and relatedmanager.filter(url_hash__isnull=False).exists():
            self.stdout.write("Error: Some %ss already have URL hashes. Use --force to overwrite." % name)
            return
        populate_url_hashes(relatedmanager.all(), self.options['length'])
