"""Generates randomly generated results for a given round.
Requires a draw to exist."""

import header
import debate.models as m

# Script starts here

from django.contrib.auth.models import User
from add_ballot_set import add_ballot_set, SUBMITTER_TYPE_MAP

import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("round", type=int, help="Round to reset")
parser.add_argument("-t", "--type", type=str, help="'tabroom' or 'public'", choices=SUBMITTER_TYPE_MAP.keys(), default="tabroom")
parser.add_argument("-u", "--user", type=str, help="User ID", default="original")
parser.add_argument("--clean", help="Remove all ballots for the draw first", action="store_true")
status = parser.add_mutually_exclusive_group(required=True)
status.add_argument("-d", "--draft", help="Generate a draft draw", action="store_const", dest="status", const=m.Debate.STATUS_DRAFT)
status.add_argument("-c", "--confirmed", help="Generate a confirmed draw", action="store_const", dest="status", const=m.Debate.STATUS_CONFIRMED)
args = parser.parse_args()

submitter_type = SUBMITTER_TYPE_MAP[args.type]
user = User.objects.get(username=args.user)

if args.clean:
    print("Deleting all ballot submissions for round %d..." % args.round)
    m.BallotSubmission.objects.filter(debate__round__seq=args.round).delete()

for debate in m.Round.objects.get(seq=args.round).get_draw():
    bset = add_ballot_set(debate, submitter_type, user, False, args.status == m.Debate.STATUS_CONFIRMED)
    debate.result_status = args.status
    print debate, "won by", bset.aff_win and "affirmative" or "negative", "on", bset.motion.reference
    debate.save()