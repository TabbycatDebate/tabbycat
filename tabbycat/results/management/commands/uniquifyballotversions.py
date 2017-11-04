from draw.models import Debate
from utils.management.base import TournamentCommand


class Command(TournamentCommand):

    help = "Makes BallotSubmission versions unique per debate. " \
           "See https://github.com/TabbycatDebate/tabbycat/issues/38#issuecomment-44149213 for more information."

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument("--dry-run", action="store_true", help="Show what it would change, but do not actually change")

    def handle_tournament(self, tournament, **options):
        for debate in Debate.objects.filter(round__tournament=tournament):
            bsubs = debate.ballotsubmission_set.order_by('timestamp')
            for i, bsub in enumerate(bsubs, start=1):
                if bsub.version != i:
                    self.stdout.write("{verb} from version {old:d} to {new:d}: {bsub:s}".format(
                        verb="Would change" if options["dry_run"] else "Changing",
                        old=bsub.version, new=i, bsub=str(bsub)))
                elif options["verbosity"] >= 3:
                    self.stdout.write("Stays version {:d}: {bsub:s}".format(bsub.version, bsub=str(bsub)))
                if not options["dry_run"]:
                    bsub.version = i
                    bsub.save()
