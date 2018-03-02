from argparse import ArgumentParser

from django.db.models import Q

from participants.models import Person
from utils.management.base import TournamentCommand

from ...utils import delete_identifiers, generate_identifiers


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

        delete = subparsers.add_parser("delete")
        super(Command, self).add_arguments(delete)

    def handle_tournament(self, tournament, **options):
        self.options = options

        people = Person.objects.filter(
            Q(adjudicator__tournament=tournament) | Q(speaker__team__tournament=tournament)
        )

        if options['subcommand'] == "delete":
            self.stdout.write("Deleting all check-in identifiers for people...".format())
            delete_identifiers(people)

        elif options['subcommand'] == "generate":
            self.stdout.write("Deleting all check-in identifiers for people...".format())
            if self.options['overwrite']:
                queryset = people
                existing = Person.objects.none()
            else:
                queryset = people.filter(checkin_identifier__isnull=True)
                existing = people.filter(checkin_identifier__isnull=False)

            if existing.exists():
                self.stdout.write(self.style.WARNING("Skipping {0:d} people who already have "
                    "identifiers. Use --overwrite to overwrite them.".format(existing.count())))

            self.stdout.write("Generating check-in identifiers for {0:d} people".format(queryset.count()))
            generate_identifiers(queryset, length=self.options['length'])
