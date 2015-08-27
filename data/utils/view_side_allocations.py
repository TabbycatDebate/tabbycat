import header
import random
import argparse

from tournaments.models import Round
from draw.models import TeamPositionAllocation

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("rounds", type=int, nargs="+", help="Round to generate for.")
parser.add_argument("-d", "--delete", action="store_true", help="Delete allocations, don't create any.")
parser.add_argument("-q", "--quiet", action="store_true", help="Don't print the allocations.")
args = parser.parse_args()

for seq in args.rounds:
    round = Round.objects.get(seq=seq)
    affs = [x.team for x in TeamPositionAllocation.objects.filter(round=round, position=TeamPositionAllocation.POSITION_AFFIRMATIVE).select_related('team')]
    negs = [x.team for x in TeamPositionAllocation.objects.filter(round=round, position=TeamPositionAllocation.POSITION_NEGATIVE).select_related('team')]
    print((str(round)))
    print("Affirmative                    Negative")
    for aff, neg in zip(sorted(affs), sorted(negs)):
        print(("{0:30} {1:30}".format(aff.short_name, neg.short_name)))
