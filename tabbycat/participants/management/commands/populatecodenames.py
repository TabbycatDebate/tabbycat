from utils.management.base import TournamentCommand

from ...emoji import populate_code_names_from_emoji


class Command(TournamentCommand):

    help = "Populates teams' code names based on their emoji"

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument("--overwrite", action="store_true",
            help="Overwrite all existing code names")

    def handle_tournament(self, tournament, **options):
        count = populate_code_names_from_emoji(tournament.team_set.all(), overwrite=options["overwrite"])
        self.stdout.write("Populated code names for {count} teams in tournament {tournament}".format(
                count=count, tournament=tournament))
