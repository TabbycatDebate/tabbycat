from utils.management.base import RoundCommand, CommandError
from ...models import Debate
from tournaments.models import Round

class Command(RoundCommand):

    help = "Deletes all debates in a round (or rounds)."
    confirm_round_destruction = "delete ALL DEBATES"

    def handle_round(self, round, **options):
        self.stdout.write("Deleting all debates in round '{}'...".format(round.name))
        Debate.objects.filter(round=round).delete()
        round.draw_status = Round.STATUS_NONE
        round.save()
