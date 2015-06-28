from django.core.management.base import BaseCommand, CommandError
from debate.utils import populate_url_hashes, delete_url_hashes
from debate.models import Tournament
from argparse import ArgumentParser

class Command(BaseCommand):

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="subcommand", parser_class=ArgumentParser)
        parser.add_argument('tournament', help="Slug of tournament to generate URL hashes for")

        generate = subparsers.add_parser("generate")
        generate.add_argument('--teams-only', action="store_true", default=False,
            help="Only generate hashes for teams")
        generate.add_argument('--adjs-only', action="store_true", default=False,
            help="Only generate hashes for adjudicators")
        generate.add_argument('-l', '--length', type=int, default=8,
            help="Length of URL hash to generate (default 8)")
        generate.add_argument('-O', '--overwrite', action="store_true", default=False,
            help="Overwrite existing hashes")

        delete = subparsers.add_parser("delete")

    def handle(self, *args, **options):
        try:
            tournament = Tournament.objects.get(slug=options['tournament'])
        except Tournament.DoesNotExist:
            raise CommandError("There is no tournament with slug %r", options['tournament'])

        self.options = options

        if options['subcommand'] == "delete":
            self.stdout.write("Deleting all URL hashes...")
            delete_url_hashes(tournament.adjudicator_set.all())
            delete_url_hashes(tournament.team_set.all())

        elif options['subcommand'] == "generate":
            if not options['teams_only']:
                self.populate_url_hashes(tournament.adjudicator_set)
            if not options['adjs_only']:
                self.populate_url_hashes(tournament.team_set)

    def populate_url_hashes(self, relatedmanager):
        if self.options['overwrite']:
            queryset = relatedmanager.all()
            existing = relatedmanager.none()
        else:
            queryset = relatedmanager.filter(url_hash__isnull=True)
            existing = relatedmanager.filter(url_hash__isnull=False)

        model_name = relatedmanager.model._meta.verbose_name_plural.lower()
        if existing.exists():
            self.stdout.write("* Skipping %d %s that already have URL hashes. Use --overwrite to overwrite them.\n" % (existing.count(), model_name))

        self.stdout.write("Generating URL hashes for %d %s" % (queryset.count(), model_name))
        populate_url_hashes(queryset, self.options['length'])
