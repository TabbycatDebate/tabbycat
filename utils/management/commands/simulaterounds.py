from django.contrib.auth import get_user_model

from adjallocation.hungarian import HungarianAllocator
from adjallocation.allocator import allocate_adjudicators
from draw.models import Debate
from draw.manager import DrawManager
from utils.management.base import RoundCommand
from venues.allocator import allocate_venues
from results.dbutils import add_ballotsets_to_round
from results.management.commands.generateresults import GenerateResultsCommandMixin
from tournaments.models import Round

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
        round.activate_all()

        self.stdout.write("Generating a draw for round '{}'...".format(round.name))
        DrawManager(round).create()
        allocate_venues(round)
        round.draw_status = Round.STATUS_CONFIRMED
        round.save()

        self.stdout.write("Auto-allocating adjudicators for round '{}'...".format(round.name))
        allocate_adjudicators(round, HungarianAllocator)

        self.stdout.write("Generating results for round '{}'...".format(round.name))
        add_ballotsets_to_round(round, **self.ballotset_kwargs(options))

        round.tournament.current_round = round
        round.tournament.save()
