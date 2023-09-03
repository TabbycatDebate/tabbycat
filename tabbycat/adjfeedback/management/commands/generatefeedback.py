from operator import attrgetter

from django.contrib.auth import get_user_model
from django.core.management.base import CommandError

from adjfeedback.models import AdjudicatorFeedback
from draw.models import Debate
from utils.management.base import RoundCommand

from ...dbutils import add_feedback, add_feedback_to_round, delete_all_feedback_for_round, delete_feedback

OBJECT_TYPE_CHOICES = ["round", "debate"]
SUBMITTER_TYPE_MAP = {
    'tabroom': AdjudicatorFeedback.Submitter.TABROOM,
    'public':  AdjudicatorFeedback.Submitter.PUBLIC,
}
User = get_user_model()


class Command(RoundCommand):

    help = "Adds randomly-generated feedback to the database"
    rounds_required = False

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument("--debates", type=int, nargs="+",
                            help="IDs of specific debates to add feedback to. "
                            "Done in addition to rounds, if any.",
                            default=[])
        parser.add_argument("-p", "--probability", type=float,
                            help="Probability with which to add feedback",
                            default=1.0)
        parser.add_argument("-T", "--submitter-type", type=str,
                            help="Submitter type, either 'tabroom' or 'public'",
                            choices=list(SUBMITTER_TYPE_MAP.keys()),
                            default="tabroom")
        parser.add_argument("-u", "--user", type=str,
                            help="Username of submitter", default="random")

        status = parser.add_mutually_exclusive_group()
        status.add_argument("-D", "--discarded", action="store_true",
                            help="Make feedback discarded")
        status.add_argument("-c", "--confirmed", action="store_true",
                            help="Make feedback confirmed")

        parser.add_argument("--clean",
                            help="Remove all associated feedback first",
                            action="store_true")
        parser.add_argument("--create-user",
                            help="Create user if it doesn't exist",
                            action="store_true")

    @staticmethod
    def _get_user(options):
        if options["submitter_type"] == "public":
            return None
        try:
            return User.objects.get(username=options["user"])
        except User.DoesNotExist:
            if options["create_user"]:
                return User.objects.create_user(options["user"], "", options["user"])
            else:
                raise CommandError("There is no user called {user!r}. Use the --create-user option to create it.".format(user=options["user"]))

    @classmethod
    def feedback_kwargs(cls, options):
        return {
            "submitter_type": SUBMITTER_TYPE_MAP[options["submitter_type"]],
            "user"          : cls._get_user(options),
            "probability"   : options["probability"],
            "discarded"     : options["discarded"],
            "confirmed"     : options["confirmed"],
        }

    def handle(self, *args, **options):
        if not self.get_rounds(options) and not options["debates"]:
            raise CommandError("No rounds or debates were given. (Use --help for more info.)")

        super(Command, self).handle(*args, **options)  # Handles rounds

        for tournament in self.get_tournaments(options):
            for debate_id in options["debates"]:
                try:
                    debate = Debate.objects.get(round__tournament=tournament, id=debate_id)
                except Debate.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING("Warning: There is no debate with "
                                           "id {:d} for tournament {!r}, "
                                           "skipping".format(debate_id, tournament.slug)))
                self.handle_debate(debate, **options)

    def handle_object(self, obj, name_field, delete_func, add_func, **options):
        if options["clean"]:
            self.stdout.write(self.style.WARNING("Deleting all feedback for {}...".format(name_field(obj))))
            delete_func(obj)

        self.stdout.write(self.style.MIGRATE_HEADING("Generating feedback for {}...".format(name_field(obj))))
        try:
            add_func(obj, **self.feedback_kwargs(options))
        except ValueError as e:
            raise CommandError(e)

    def handle_round(self, round, **options):
        return self.handle_object(round, attrgetter('name'), delete_all_feedback_for_round, add_feedback_to_round, **options)

    def handle_debate(self, debate, **options):
        return self.handle_object(debate, attrgetter('matchup'), delete_feedback, add_feedback, **options)
