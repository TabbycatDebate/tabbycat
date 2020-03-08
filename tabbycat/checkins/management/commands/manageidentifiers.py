from argparse import ArgumentParser

from django.db.models import Q

from checkins.models import PersonIdentifier, VenueIdentifier
from participants.models import Person
from utils.management.base import TournamentCommand

from ...utils import create_identifiers, delete_identifiers


class Command(TournamentCommand):

    help = "Generates or deletes check-in identifiers"

    def add_arguments(self, parser):
        parent = ArgumentParser(add_help=False)
        parent.add_argument('-m', '--model', type=str, choices=['person', 'venue'], default='person',
            help="Which model to use to create identifiers")

        subparsers = parser.add_subparsers(dest="subcommand", parser_class=ArgumentParser)
        subparsers.required = True

        generate = subparsers.add_parser("generate", parents=[parent])
        super().add_arguments(generate)
        generate.add_argument('-O', '--overwrite', action="store_true", default=False,
            help="Overwrite existing URL keys")

        delete = subparsers.add_parser("delete", parents=[parent])
        super().add_arguments(delete)

    def handle_tournament(self, tournament, **options):
        if options['model'] == 'person':
            queryset = Person.objects.filter(
                Q(adjudicator__tournament=tournament) | Q(speaker__team__tournament=tournament),
            )
            identifier_model = PersonIdentifier
            plural = 'people'
        elif options['model'] == 'venue':
            queryset = tournament.venue_set.all()
            identifier_model = VenueIdentifier
            plural = 'venues'

        existing_count = queryset.filter(checkin_identifier__isnull=False).count()
        if options['subcommand'] == "delete" or options['subcommand'] == "generate" and options['overwrite']:
            _, counts = delete_identifiers(queryset)
            self.stdout.write("Deleted check-in identifiers for all {0:d} {1:s}".format(existing_count, plural))
            for model, count in counts.items():
                self.stdout.write(" - deleted {0:d} {1:s} instances".format(count, model))

        if options['subcommand'] == "generate":
            queryset = queryset.filter(checkin_identifier__isnull=True)

            if not options['overwrite']:
                self.stdout.write("Skipping {0:d} existing identifiers".format(existing_count))

            self.stdout.write("Generated check-in identifiers for {0:d} {1:s}".format(queryset.count(), plural))
            create_identifiers(identifier_model, queryset)
