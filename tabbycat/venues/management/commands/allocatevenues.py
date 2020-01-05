from utils.management.base import RoundCommand

from ...allocator import allocate_venues


class Command(RoundCommand):

    help = "Assigns rooms for all debates in a round (or rounds)."

    def handle_round(self, round, **options):
        self.stdout.write("Assigning rooms for all debates in round '{}'...".format(round.name))
        allocate_venues(round)
