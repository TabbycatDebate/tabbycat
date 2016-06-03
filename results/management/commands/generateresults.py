from django.contrib.auth import get_user_model

from adjallocation.models import DebateAdjudicator
from draw.models import Debate
from results.models import BallotSubmission
from utils.management.base import CommandError, RoundCommand
from results.dbutils import add_ballotset, add_ballotsets_to_round, add_ballotsets_to_round_partial, delete_all_ballotsets_for_round, delete_ballotset

OBJECT_TYPE_CHOICES = ["round", "debate"]
SUBMITTER_TYPE_MAP = {
    'tabroom': BallotSubmission.SUBMITTER_TABROOM,
    'public':  BallotSubmission.SUBMITTER_PUBLIC
}
User = get_user_model()


class GenerateResultsCommandMixin:

    def add_arguments(self, parser):
        super(GenerateResultsCommandMixin, self).add_arguments(parser)
        parser.add_argument("-T", "--submitter-type", type=str, help="Submitter type, either 'tabroom' or 'public'", choices=list(SUBMITTER_TYPE_MAP.keys()), default="tabroom")
        parser.add_argument("-u", "--user", type=str, help="Username of submitter", default="random")

        parser.add_argument("--create-user", help="Create user if it doesn't exist", action="store_true")

        status = parser.add_mutually_exclusive_group(required=True)
        status.add_argument("-D", "--discarded", action="store_true", help="Make added ballot sets discarded")
        status.add_argument("-d", "--draft", action="store_true", help="Make added ballot sets draft (neither discarded nor confirmed")
        status.add_argument("-c", "--confirmed", action="store_true", help="Make added ballot sets confirmed")

        parser.add_argument("-m", "--min-score", type=float, help="Minimum speaker score (for substantive)", default=72)
        parser.add_argument("-M", "--max-score", type=float, help="Maximum speaker score (for substantive)", default=78)
        parser.add_argument("--reply-random", action="store_true", help="Choose reply speaker at random (rather than always use first speaker", default=False)

    @staticmethod
    def _get_user(options):
        try:
            return User.objects.get(username=options["user"])
        except User.DoesNotExist:
            if options["create_user"]:
                return User.objects.create_user(options["user"], "", options["user"])
            else:
                raise CommandError("There is no user called {user!r}. Use the --create-user option to create it.".format(user=options["user"]))

    @classmethod
    def ballotset_kwargs(cls, options):
        return {
            "submitter_type": SUBMITTER_TYPE_MAP[options["submitter_type"]],
            "user"          : cls._get_user(options),
            "discarded"     : options["discarded"],
            "confirmed"     : options["confirmed"],
            "min_score"     : options["min_score"],
            "max_score"     : options["max_score"],
            "reply_random"  : options["reply_random"],
        }


class Command(GenerateResultsCommandMixin, RoundCommand):

    help = "Adds randomly-generated results to the database"
    rounds_required = False

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument("--debates", type=int, nargs="+", help="IDs of specific debates to add feedback to. Done in addition to rounds, if any.", default=[])
        parser.add_argument("--clean", help="Remove all associated ballot sets first", action="store_true")
        parser.add_argument("-n", "--num-ballots", type=int, help="Number of ballot sets to add per round (default all) or debate (default 1)", default=None)

    def handle(self, *args, **options):
        if not self.get_rounds(options) and not options["debates"]:
            raise CommandError("No rounds or debates were given. (Use --help for more info.)")

        super(Command, self).handle(*args, **options) # handles rounds

        for tournament in self.get_tournaments(options):
            for debate_id in options["debates"]:
                try:
                    debate = Debate.objects.get(round__tournament=tournament, id=debate_id)
                except Debate.DoesNotExist:
                    self.stdout.write(self.style.WARNING("Warning: There is no debate with id {:d} for tournament {!r}, skipping".format(debate_id, tournament.slug)))
                self.handle_debate(debate, **options)

    def handle_round(self, round, **options):
        if options["clean"]:
            self.stdout.write(self.style.WARNING("Deleting all ballot sets for {}...".format(round.name)))
            delete_all_ballotsets_for_round(round)

        try:
            if options["num_ballots"] is not None:
                self.stdout.write(self.style.MIGRATE_HEADING("Generating ballot sets for {:d} randomly-chosen debates in {}...".format(options["num_ballots"], round.name)))
                add_ballotsets_to_round_partial(round, options["num_ballots"], **self.ballotset_kwargs(options))
            else:
                self.stdout.write(self.style.MIGRATE_HEADING("Generating ballot sets for all debates in {}...".format(round.name)))
                add_ballotsets_to_round(round, **self.ballotset_kwargs(options))

        except ValueError as e:
            raise CommandError(e)
        except DebateAdjudicator.DoesNotExist as e:
            raise CommandError(str(e) + " (Have you done adjudicator allocations for this round?)")

    def handle_debate(self, debate, **options):
        if options["clean"]:
            self.stdout.write(self.style.WARNING("Deleting all ballot sets for debate {}...".format(debate.matchup)))
            delete_ballotset(debate)

        self.stdout.write(self.style.MIGRATE_HEADING("Generating ballot set for debate {}...".format(debate.matchup)))
        try:
            for i in range(options["num_ballots"] if options["num_ballots"] is not None else 1):
                add_ballotset(debate, **self.ballotset_kwargs(options))
        except ValueError as e:
            raise CommandError(e)
        except DebateAdjudicator.DoesNotExist as e:
            raise CommandError(str(e) + " (Have you done adjudicator allocations for this debate?)")
