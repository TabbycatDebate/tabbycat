"""Adds randomly generated side allocations to teams."""

import header
import tournaments.models as tm
import draw.models as dm
import participants.models as pm
import random
import argparse

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("rounds", type=int, nargs="+", help="Round to generate for.")
parser.add_argument("-d", "--delete", action="store_true", help="Delete allocations, don't create any.")
parser.add_argument("-q", "--quiet", action="store_true", help="Don't print the allocations.")
args = parser.parse_args()

for seq in args.rounds:
    round = tm.Round.objects.get(seq=seq)
    teams = list(pm.Team.objects.all())
    assert len(teams) % 2 == 0, "There aren't an even number of teams ({0})".format(len(teams))
    random.shuffle(teams)
    affs = teams[:len(teams)/2]
    negs = teams[len(teams)/2:]
    dm.TeamPositionAllocation.objects.filter(round=round).delete()
    if not args.quiet:
        print((str(round)))
        print("Affirmative:                   Negative:")
        for aff, neg in zip(sorted(affs), sorted(negs)):
            print(("{0:30} {1:30}".format(aff.short_name, neg.short_name)))
    if args.delete:
        continue
    for team in affs:
        dm.TeamPositionAllocation(round=round, team=team, position=dm.TeamPositionAllocation.POSITION_AFFIRMATIVE).save()
    for team in negs:
        dm.TeamPositionAllocation(round=round, team=team, position=dm.TeamPositionAllocation.POSITION_NEGATIVE).save()
