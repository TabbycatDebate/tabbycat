from django.core.management.base import BaseCommand, CommandError
from tournaments.keys import populate_url_keys, delete_url_keys
from tournaments.models import Tournament
from argparse import ArgumentParser

class Command(BaseCommand):

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="subcommand", parser_class=ArgumentParser)
        parser.add_argument('tournament', help="Slug of tournament to generate randomised URLs for")

        generate = subparsers.add_parser("generate")
        generate.add_argument('--teams-only', action="store_true", default=False,
            help="Only generate randomised URLs for teams")
        generate.add_argument('--adjs-only', action="store_true", default=False,
            help="Only generate randomised URLs for adjudicators")
        generate.add_argument('-l', '--length', type=int, default=8,
            help="Length of URL key to generate (default 8)")
        generate.add_argument('-O', '--overwrite', action="store_true", default=False,
            help="Overwrite existing URL keys")

        delete = subparsers.add_parser("delete")

    def handle(self, *args, **options):
        try:
            tournament = Tournament.objects.get(slug=options['tournament'])
        except Tournament.DoesNotExist:
            raise CommandError("There is no tournament with slug %r", options['tournament'])

        self.options = options

        if options['subcommand'] == "delete":
            self.stdout.write("Deleting all randomised URLs...")
            delete_url_keys(tournament.adjudicator_set.all())
            delete_url_keys(tournament.team_set.all())

        elif options['subcommand'] == "generate":
            if not options['teams_only']:
                self.populate_url_keys(tournament.adjudicator_set)
            if not options['adjs_only']:
                self.populate_url_keys(tournament.team_set)

    def populate_url_keys(self, relatedmanager):
        if self.options['overwrite']:
            queryset = relatedmanager.all()
            existing = relatedmanager.none()
        else:
            queryset = relatedmanager.filter(url_key__isnull=True)
            existing = relatedmanager.filter(url_key__isnull=False)

        model_name = relatedmanager.model._meta.verbose_name_plural.lower()
        if existing.exists():
            self.stdout.write("* Skipping %d %s that already have randomised URLs. Use --overwrite to overwrite them.\n" % (existing.count(), model_name))

        self.stdout.write("Generating randomised URLs for %d %s" % (queryset.count(), model_name))
        populate_url_keys(queryset, self.options['length'])
