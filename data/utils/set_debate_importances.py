"""Sets the importance of all debates to the given value.
Use this when migrating to a database that makes Debate.importance required.
You may need to run this before running ./manage.py migrate debate."""

import header
import debate.models as m

import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("rounds", type=int, nargs="+", help="Round to set.")
parser.add_argument("-v", "--value", type=int, help="Importance to set.", default=2)
args = parser.parse_args()

for round in args.rounds:

    for debate in m.Round.objects.get(seq=round).get_draw():
        debate.importance = args.value
        debate.save()