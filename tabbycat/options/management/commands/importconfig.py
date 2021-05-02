import argparse
import json

from utils.management.base import TournamentCommand


class Command(TournamentCommand):

    help = "Imports a tournament configuration from a JSON file."

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument("file", type=argparse.FileType('r'),
            help="Input file")

    def handle_tournament(self, tournament, **options):
        config = json.load(options['file'])
        for key, value in config.items():
            tournament.preferences[key] = value
        print("Imported {n:d} options to tournament {tournament}".format(
            n=len(config), tournament=tournament))
