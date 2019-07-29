from utils.management.base import TournamentCommand

from ...models import BallotSubmission


class Command(TournamentCommand):

    help = "Resaves all ballots, thereby updating all TeamScore objects."

    def handle_tournament(self, tournament, **options):
        ballotsubs = BallotSubmission.objects.filter(debate__round__tournament=tournament)

        self.stdout.write("Resaving {:d} ballots in tournament \"{:s}\"...".format(
                ballotsubs.count(), tournament.name))

        for bsub in ballotsubs:
            self.stdout.write("Saving: {}".format(bsub))
            bsub.result.save()
