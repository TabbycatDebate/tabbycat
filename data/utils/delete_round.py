"""Deletes all debates in a round."""

import header
from draws.models import Debate

import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("round", type=int, nargs='+', help="Round to reset")
args = parser.parse_args()

print("WARNING! You are about to delete ALL DEBATES from the following rounds:")
print("   " + ", ".join(map(str, args.round)))
response = raw_input("Are you sure? ")

if response != "yes":
    print("Cancelled.")
    exit()


for seq in args.round:
    round = m.Round.objects.get(seq=seq)
    print("Deleting everything in round " + str(round) + "...")
    Debate.objects.filter(round=round).delete()
    round.draw_status = m.Round.STATUS_NONE
    round.save()
print("Done.")