import json

from utils.management.base import TournamentCommand


class Command(TournamentCommand):

    help = "Exports a tournament configuration to a JSON file."

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument("file", nargs="?", type=str, default="config-<t>.json",
            help="Output file, where <t> will be replaced by the tournament slug. "
                 "(default: config-<t>.json)")
        parser.add_argument("--compact", action="store_true",
            help="Don't insert newlines in the JSON file.")
        parser.add_argument("--indent", "-i", type=int, default=2,
            help="Number of spaces by which to indent each line. Ignored if "
                 "--compact is used. (default: 2)")

    def handle_tournament(self, tournament, **options):
        filename = options['file'].replace("<t>", tournament.slug)
        f = open(filename, 'w')
        json.dump(tournament.preferences.all(), f, indent=options['indent'])
        print("Exported configuration to {}".format(filename))
