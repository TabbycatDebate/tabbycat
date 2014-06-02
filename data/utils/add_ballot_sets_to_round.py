"""Adds randomly generated ballots sets to the given round.
Use this to add random additional ballots to a round, to randomly selected
debates. Don't use this to generate good results for a round -- use
generate_random_results.py to do that."""

import header
import debate.models as m
from django.contrib.auth.models import User
import random

from add_ballot_set import SUBMITTER_TYPE_MAP, add_ballot_set

import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("round", type=int, help="Round(s) to add to")
parser.add_argument("no_ballots", type=int, help="Number of ballots to add")
parser.add_argument("-t", "--type", type=str, help="'tabroom' or 'public'", choices=SUBMITTER_TYPE_MAP.keys(), default="tabroom")
parser.add_argument("-u", "--user", type=str, help="User ID", default="original")
parser.add_argument("-d", "--discarded", action="store_true", help="Ballot set is discarded")
parser.add_argument("-c", "--confirmed", action="store_true", help="Ballot set is confirmed")
args = parser.parse_args()

submitter_type = SUBMITTER_TYPE_MAP[args.type]
if submitter_type == m.BallotSubmission.SUBMITTER_TABROOM:
    user = User.objects.get(username=args.user)
else:
    user = None

round = m.Round.objects.get(seq=args.round)
debates = round.debate_set.all()

for i in xrange(args.no_ballots):

    debate = random.choice(debates)

    print debate

    try:
        bset = add_ballot_set(debate, submitter_type, user, args.discarded, args.confirmed)
    except ValueError, e:
        print "Error:", e

    print "  Won by", bset.aff_win and "affirmative" or "negative"