from utils.management.base import RoundCommand, CommandError
from ...allocator import VenueAllocator

class Command(RoundCommand):

    help = "Assigns venues for all debates in a round (or rounds)."

    def handle_round(self, round, **options):
        self.stdout.write("Assigning venues for all debates in round '{}'...".format(round.name))
        draw = round.get_draw()
        allocator = VenueAllocator()
        allocator.allocate(round, draw)
