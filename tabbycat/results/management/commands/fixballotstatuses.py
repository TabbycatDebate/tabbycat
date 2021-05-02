from draw.models import Debate
from utils.management.base import TournamentCommand

from ...models import BallotSubmission


class Command(TournamentCommand):

    help = "Makes discarded/confirmed fields of BallotSubmissions consistent " \
        "with result_status field of Debates. Not guaranteed to be " \
        "minimalist with changes."

    def handle_tournament(self, tournament, **options):
        for bsub in BallotSubmission.objects.filter(debate__round__tournament=tournament):
            debate_status = bsub.debate.result_status
            original = (bsub.discarded, bsub.confirmed)
            if debate_status == Debate.STATUS_NONE:
                bsub.discarded = True
                bsub.confirmed = False
            elif debate_status == Debate.STATUS_DRAFT:
                bsub.confirmed = False
            elif debate_status == Debate.STATUS_CONFIRMED:
                if not bsub.discarded:
                    bsub.confirmed = True
            new = (bsub.discarded, bsub.confirmed)
            if original != new:
                self.stdout.write("{} changed from {} to {}".format(bsub, original, new))
                bsub.save()
