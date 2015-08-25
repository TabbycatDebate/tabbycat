from ..base import TournamentCommand
from ..generatedata.feedback import add_feedback, SUBMITTER_TYPE_MAP

from django.contrib.auth.models import User
from tournaments.models import Round
from adjfeedback.models import AdjudicatorFeedback

OBJECT_TYPE_CHOICES = ["round", "debate"]

class Command(TournamentCommand):

    help = "Generates random feedback"

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument("type", type=str, choices=OBJECT_TYPE_CHOICES)
        parser.add_argument("specifiers", type=int, nargs="+", help="What to add feedback to. For rounds: seq numbers. For debates: database IDs.")
        parser.add_argument("-p", "--probability", type=float, help="Probability with which to add feedback", default=1.0)
        parser.add_argument("-T", "--submitter-type", type=str, help="Submitter type, either 'tabroom' or 'public'", choices=list(SUBMITTER_TYPE_MAP.keys()), default="tabroom")
        parser.add_argument("-u", "--user", type=str, help="Username of submitter", default="random")
        parser.add_argument("-d", "--discarded", action="store_true", help="Make feedback discarded")
        parser.add_argument("-c", "--confirmed", action="store_true", help="Make feedback confirmed")
        parser.add_argument("--clean", help="Remove all associated feedback first", action="store_true")


    def handle_tournament(self, tournament, **options):
        submitter_type = SUBMITTER_TYPE_MAP[options["submitter_type"]]
        user = User.objects.get(username=options["user"])
        feedback_kwargs = {
            "submitter_type": SUBMITTER_TYPE_MAP[options["submitter_type"]],
            "user"          : User.objects.get(username=options["user"]) if submitter_type == 'tabroom' else None,
            "probability"   : options["probability"],
            "discarded"     : options["discarded"],
            "confirmed"     : options["confirmed"],
        }

        if options["type"] == "round":
            for seq in options["specifiers"]:
                round = Round.objects.get(seq=seq)

                if args.clean:
                    print(("Deleting all feedback for round {}...".format(round.name)))
                    AdjudicatorFeedback.objects.filter(source_adjudicator__debate__round__seq=seq).delete()
                    AdjudicatorFeedback.objects.filter(source_team__debate__round__seq=seq).delete()

                for debate in round.get_draw():
                    fbs = add_feedback(debate, **feedback_kwargs)

        elif options["type"] == "debate":
            for debate_id in options["specifiers"]:
                debate = Debate.objects.get(id=debate_id)
                fbs = add_feedback(debate, **feedback_kwargs)