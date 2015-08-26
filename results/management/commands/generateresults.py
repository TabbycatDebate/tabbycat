from utils.management.base import TournamentCommand, CommandError
from results.dbutils import add_ballotset, add_ballotsets_to_round, delete_ballotset, delete_all_ballotsets_for_round, add_ballotsets_to_round_partial

from django.contrib.auth.models import User
from tournaments.models import Round
from draw.models import Debate
from results.models import BallotSubmission

OBJECT_TYPE_CHOICES = ["round", "debate"]
SUBMITTER_TYPE_MAP = {
    'tabroom': BallotSubmission.SUBMITTER_TABROOM,
    'public':  BallotSubmission.SUBMITTER_PUBLIC
}

class Command(TournamentCommand):

    help = "Adds randomly-generated results to the database"

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument("type", type=str, choices=OBJECT_TYPE_CHOICES, help="'round' to add ballot sets to entire round, 'debate' for a particular debate")
        parser.add_argument("specifiers", type=int, nargs="+", help="What to add ballot sets to. For rounds: seq numbers. For debates: database IDs.")
        parser.add_argument("-T", "--submitter-type", type=str, help="Submitter type, either 'tabroom' or 'public'", choices=list(SUBMITTER_TYPE_MAP.keys()), default="tabroom")
        parser.add_argument("-u", "--user", type=str, help="Username of submitter", default="random")

        parser.add_argument("--clean", help="Remove all associated ballot sets first", action="store_true")
        parser.add_argument("--create-user", help="Create user if it doesn't exist", action="store_true")
        parser.add_argument("-N", "--num-ballots", type=int, help="Number of ballot sets to add per round (if round specified"
                ", default all) or debate (if debate specified, default 1)", default=None)

        status = parser.add_mutually_exclusive_group(required=True)
        status.add_argument("-D", "--discarded", action="store_true", help="Make added ballot sets discarded")
        status.add_argument("-d", "--draft", action="store_true", help="Make added ballot sets draft (neither discarded nor confirmed")
        status.add_argument("-c", "--confirmed", action="store_true", help="Make added ballot sets confirmed")

        parser.add_argument("-m", "--min-score", type=float, help="Minimum speaker score (for substantive)", default=72)
        parser.add_argument("-M", "--max-score", type=float, help="Maximum speaker score (for substantive)", default=78)

    @staticmethod
    def _get_user(options):
        try:
            return User.objects.get(username=options["user"])
        except User.DoesNotExist:
            if options["create_user"]:
                return User.objects.create_user(options["user"], "", options["user"])
            else:
                raise CommandError("There is no user called {user!r}. Use the --create-user option to create it.".format(user=options["user"]))

    def handle_tournament(self, tournament, **options):
        ballotset_kwargs = {
            "submitter_type": SUBMITTER_TYPE_MAP[options["submitter_type"]],
            "user"          : self._get_user(options),
            "discarded"     : options["discarded"],
            "confirmed"     : options["confirmed"],
            "min_score"     : options["min_score"],
            "max_score"     : options["max_score"],
        }

        if options["type"] == "round":
            for seq in options["specifiers"]:
                round = Round.objects.get(tournament=tournament, seq=seq)

                if options["clean"]:
                    self.stdout.write("Deleting all ballot sets for round {}...".format(round.name))
                    delete_all_ballotsets_for_round(round)

                self.stdout.write("Generating ballot sets for round {}...".format(round.name))
                try:
                    if options["num_ballots"] is not None:
                        add_ballotsets_to_round_partial(round, options["num_ballots"], **ballotset_kwargs)
                    else:
                        add_ballotsets_to_round(round, **ballotset_kwargs)
                except ValueError as e:
                    raise CommandError(e)

        elif options["type"] == "debate":
            for debate_id in options["specifiers"]:
                debate = Debate.objects.get(round__tournament=tournament, id=debate_id)

                if options["clean"]:
                    self.stdout.write("Deleting all ballot sets for debate {}...".format(debate.matchup))
                    delete_ballotset(debate)

                self.stdout.write("Generating ballot set for debate {}...".format(debate.matchup))
                try:
                    for i in range(options["num_ballots"]):
                        add_ballotset(debate, **ballotset_kwargs)
                except ValueError as e:
                    raise CommandError(e)
