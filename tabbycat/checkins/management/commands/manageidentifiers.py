from argparse import ArgumentParser

from django.db.models import Q

from participants.models import Person
from utils.management.base import TournamentCommand
from venues.models import Venue

from ...utils import create_identifiers, delete_identifiers


class Command(TournamentCommand):

    help = "Generates or deletes check-in identifiers"

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="subcommand", parser_class=ArgumentParser,
              metavar="{generate,delete}")
        subparsers.required = True

        generate = subparsers.add_parser("generate")
        super(Command, self).add_arguments(generate)
        generate.add_argument('-l', '--length', type=int, default=6,
            help="Length of URL key to generate (default 6)")
        generate.add_argument('-O', '--overwrite', action="store_true", default=False,
            help="Overwrite existing URL keys")
        generate.add_argument('-m', '--model', type=str, choices=['person', 'venue'], default='person',
            help="Which model for whoch to create identifiers")

        delete = subparsers.add_parser("delete")
        super(Command, self).add_arguments(delete)

    def handle_tournament(self, tournament, **options):
        self.options = options

        model = {
            'person': Person,
            'venue': Venue,
        }[self.options['model']]

        model_query = model.objects.all()
        if self.options['model'] == 'venue':
            model_query = model_query.filter(tournament=tournament)
        else:
            model_query = model_query.filter(Q(adjudicator__tournament=tournament) | Q(speaker__team__tournament=tournament))

        if options['subcommand'] == "generate" and self.options['overwrite'] or options['subcommand'] == "delete":
            self.stdout.write("Deleting all check-in identifiers for {0:s}...".format(self.options['model']))
            delete_identifiers(model_query)

        if options['subcommand'] == "generate":
            self.stdout.write("Creating all check-in identifiers for {0:s}...".format(self.options['model']))
            if self.options['overwrite']:
                delete_identifiers(model_query.filter(checkin_identifier__isnull=False))

            queryset = model_query.filter(checkin_identifier__isnull=True)
            self.stdout.write("Generating check-in identifiers for {0:d} {1:s}".format(queryset.count(), self.options['model']))
            create_identifiers(queryset, length=self.options['length'])
