from argparse import ArgumentParser

from participants.models import Person
from utils.management.base import TournamentCommand

from ...utils import delete_url_keys, populate_url_keys


class Command(TournamentCommand):

    help = "Generates or deletes private URLs"

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="subcommand", parser_class=ArgumentParser,
              metavar="{generate,delete}")
        subparsers.required = True

        generate = subparsers.add_parser("generate")
        super(Command, self).add_arguments(generate)
        generate.add_argument('--teams-only', action="store_true", default=False,
            help="Only generate private URLs for teams")
        generate.add_argument('--adjs-only', action="store_true", default=False,
            help="Only generate private URLs for adjudicators")
        generate.add_argument('-l', '--length', type=int, default=8,
            help="Length of URL key to generate (default 8)")
        generate.add_argument('-O', '--overwrite', action="store_true", default=False,
            help="Overwrite existing URL keys")

        delete = subparsers.add_parser("delete")
        super(Command, self).add_arguments(delete)

    def handle_tournament(self, tournament, **options):
        self.options = options

        if options['subcommand'] == "delete":
            self.stdout.write("Deleting all private URLs...")
            delete_url_keys(tournament.participants)

        elif options['subcommand'] == "generate":
            if not options['teams_only']:
                self.populate_url_keys(Person.objects.filter(adjudicator__tournament=tournament))
            if not options['adjs_only']:
                self.populate_url_keys(Person.objects.filter(speaker__team__tournament=tournament))

    def populate_url_keys(self, relatedmanager):
        if self.options['overwrite']:
            queryset = relatedmanager.all()
            existing = relatedmanager.none()
        else:
            queryset = relatedmanager.filter(url_key__isnull=True)
            existing = relatedmanager.filter(url_key__isnull=False)

        model_name = relatedmanager.model._meta.verbose_name_plural.lower()
        if existing.exists():
            self.stdout.write(self.style.WARNING("Skipping {0:d} {1:s} that already have private URLs. Use --overwrite to overwrite them.".format(
                existing.count(), model_name)))

        self.stdout.write("Generating private URLs for {0:d} {1:s}".format(
            queryset.count(), model_name))
        populate_url_keys(queryset, self.options['length'])
