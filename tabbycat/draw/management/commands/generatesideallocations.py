from operator import attrgetter
from random import shuffle

from utils.management.base import CommandError, RoundCommand

from ...models import DebateTeam


class Command(RoundCommand):

    help = "Adds randomly generated side allocations to teams for all preliminary rounds."

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument("--delete", action="store_true", help="Delete allocations, don't create any.")
        parser.add_argument("-q", "--quiet", action="store_true", help="Don't print the allocations.")

    def handle_round(self, round, **options):
        teams = list(round.tournament.team_set.all())
        if len(teams) % 2 != 0:
            raise CommandError("There aren't an even number of teams ({0})".format(len(teams)))

        shuffle(teams)
        affs = teams[:len(teams)//2]
        negs = teams[len(teams)//2:]

        round.teamsideallocation_set.all().delete()
        if options["delete"]:
            return

        if not options["quiet"]:
            self.stdout.write(self.style.MIGRATE_HEADING(round.name))
            self.stdout.write("Affirmative:                   Negative:")
            for aff, neg in zip(sorted(affs, key=attrgetter('short_name')), sorted(negs, key=attrgetter('short_name'))):
                self.stdout.write("{0:30} {1:30}".format(aff.short_name, neg.short_name))

        for team in affs:
            team.teamsideallocation_set.create(round=round, side=DebateTeam.SIDE_AFF)
        for team in negs:
            team.teamsideallocation_set.create(round=round, side=DebateTeam.SIDE_NEG)
