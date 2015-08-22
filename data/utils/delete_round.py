"""Deletes all debates in a round."""

import header
from draw.models import Debate
from tournaments.models import Round

import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("round", type=int, nargs='+', help="Round to reset")
args = parser.parse_args()

print("WARNING! You are about to delete ALL DEBATES from the following rounds:")
print(("   " + ", ".join(map(str, args.round))))
response = input("Are you sure? ")

if response != "yes":
    print("Cancelled.")
    exit()


for seq in args.round:
    round = Round.objects.get(seq=seq)
    print(("Deleting everything in round " + str(round) + "..."))
    Debate.objects.filter(round=round).delete()
    round.draw_status = Round.STATUS_NONE
    round.save()
print("Done.")