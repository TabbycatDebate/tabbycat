from utils.management.base import RoundCommand

from ...dbutils import delete_round_draw


class Command(RoundCommand):

    help = "Deletes all debates in a round (or rounds)."
    confirm_round_destruction = "delete ALL DEBATES"

    def handle_round(self, round, **options):
        self.stdout.write("Deleting all debates in round '{}'...".format(round.name))
        delete_round_draw(round)
