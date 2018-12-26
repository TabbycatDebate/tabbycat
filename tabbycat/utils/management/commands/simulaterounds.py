from django.contrib.auth import get_user_model

from adjallocation.allocators import legacy_allocate_adjudicators
from adjallocation.allocators.hungarian import ConsensusHungarianAllocator, VotingHungarianAllocator
from availability.utils import activate_all
from draw.models import Debate
from draw.manager import DrawManager
from results.dbutils import add_results_to_round
from results.management.commands.generateresults import GenerateResultsCommandMixin
from tournaments.models import Round
from utils.management.base import RoundCommand
from venues.allocator import allocate_venues

User = get_user_model()


class Command(GenerateResultsCommandMixin, RoundCommand):

    help = "Adds draws and results to the database"
    confirm_round_destruction = "delete ALL DEBATES"

    def handle_round(self, round, **options):
        self.stdout.write("Deleting all debates in round '{}'...".format(round.name))
        Debate.objects.filter(round=round).delete()
        round.draw_status = Round.STATUS_NONE
        round.save()

        self.stdout.write("Checking in all teams, adjudicators and venues for round '{}'...".format(round.name))
        activate_all(round)

        self.stdout.write("Generating a draw for round '{}'...".format(round.name))
        DrawManager(round).create()
        round.draw_status = Round.STATUS_CONFIRMED
        round.save()

        self.stdout.write("Auto-allocating adjudicators for round '{}'...".format(round.name))
        if round.ballots_per_debate == 'per-adj':
            allocator_class = VotingHungarianAllocator
        else:
            allocator_class = ConsensusHungarianAllocator
        legacy_allocate_adjudicators(round, allocator_class)

        allocate_venues(round)

        self.stdout.write("Generating results for round '{}'...".format(round.name))
        add_results_to_round(round, **self.result_kwargs(options))

        round.completed = True
        round.save()
