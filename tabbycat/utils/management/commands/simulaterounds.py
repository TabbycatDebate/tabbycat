from django.contrib.auth import get_user_model

from adjallocation.allocators.hungarian import ConsensusHungarianAllocator, VotingHungarianAllocator
from availability.utils import activate_all, set_availability
from draw.manager import DrawManager
from draw.models import Debate
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

        self.stdout.write("Checking in all teams, adjudicators and rooms for round '{}'...".format(round.name))
        activate_all(round)

        self.stdout.write("Generating a draw for round '{}'...".format(round.name))
        DrawManager(round).create()
        round.draw_status = Round.STATUS_CONFIRMED
        round.save()

        # Limit to 7 adjudicators per debate (just to avoid panel sizes getting too out of hand)
        max_nadjudicators = round.debate_set.count() * 7
        if round.active_adjudicators.count() > max_nadjudicators:
            adjs = round.tournament.relevant_adjudicators.order_by('?')[:max_nadjudicators]
            set_availability(adjs, round)

        self.stdout.write("Auto-allocating adjudicators for round '{}'...".format(round.name))
        debates = round.debate_set.all()
        adjs = round.active_adjudicators.all()
        if round.ballots_per_debate == 'per-adj':
            allocator = VotingHungarianAllocator(debates, adjs, round)
        else:
            allocator = ConsensusHungarianAllocator(debates, adjs, round)

        allocation, extra_msgs = allocator.allocate()
        for alloc in allocation:
            alloc.save()

        allocate_venues(round)

        self.stdout.write("Generating results for round '{}'...".format(round.name))
        add_results_to_round(round, **self.result_kwargs(options))

        round.completed = True
        round.save()
