"""Generates randomly generated feedback for a given round.
Requires a draw to exist."""

import header
import debate.models as m

from django.contrib.auth.models import User
from add_feedback import add_feedback, SUBMITTER_TYPE_MAP

import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("rounds", type=int, nargs="+", help="Round to generate for.")
parser.add_argument("-p", "--probability", type=float, help="Probability with which to add feedback", default=1.0)
parser.add_argument("-t", "--type", type=str, help="'tabroom' or 'public'", choices=SUBMITTER_TYPE_MAP.keys(), default="tabroom")
parser.add_argument("-u", "--user", type=str, help="User ID", default="original")
parser.add_argument("--clean", help="Remove all ballots for the draw first", action="store_true")
parser.add_argument("-c", "--confirmed", action="store_true", help="Ballot set is confirmed")
args = parser.parse_args()

submitter_type = SUBMITTER_TYPE_MAP[args.type]
user = User.objects.get(username=args.user)

for round in args.rounds:
    if args.clean:
        print("Deleting all feedback for round %d..." % round)
        m.AdjudicatorFeedback.objects.filter(source_adjudicator__adjudicator__debate__round__seq=round).delete()
        m.AdjudicatorFeedback.objects.filter(source_team__adjudicator__debate__round__seq=round).delete()

    for debate in m.Round.objects.get(seq=round).get_draw():
        fbs = add_feedback(debate, submitter_type, user, args.probability, False, args.confirmed)