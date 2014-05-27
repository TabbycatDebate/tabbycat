"""Adds a randomly generated ballot set to the given debate."""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
import sys
sys.path.append(os.path.abspath(os.path.join(os.environ.get("VIRTUAL_ENV"), "..")))
import debate.models as m
from django.contrib.auth.models import User
from debate.result import BallotSet
import random

SUBMITTER_TYPE_MAP = {
    'tabroom': m.BallotSubmission.SUBMITTER_TABROOM,
    'public':  m.BallotSubmission.SUBMITTER_PUBLIC
}

def add_ballot_set(debate, submitter_type, user, discarded=False, confirmed=False):

    if discarded and confirmed:
        raise ValueError("Ballot can't be both discarded and confirmed!")

    # Create a new BallotSubmission
    bsub = m.BallotSubmission(submitter_type=submitter_type, debate=debate)
    if submitter_type == m.BallotSubmission.SUBMITTER_TABROOM:
        bsub.user = user
    bsub.save()

    def gen_results():
        r = {'aff': (0,), 'neg': (0,)}
        def do():
            s = [random.randint(72, 78) for i in range(3)]
            s.append(random.randint(72,78)/2.0)
            return s
        while sum(r['aff']) == sum(r['neg']):
            r['aff'] = do()
            r['neg'] = do()
        return r

    rr = dict()
    for adj in debate.adjudicators.list:
        rr[adj] = gen_results()

    # Create relevant scores
    bset = BallotSet(bsub)

    for side in ('aff', 'neg'):
        speakers = getattr(debate, '%s_team' % side).speakers
        for i in range(1, 4):
            bset.set_speaker(
                side = side,
                pos = i,
                speaker = speakers[i - 1],
            )
        bset.set_speaker(
            side = side,
            pos = 4,
            speaker = speakers[0]
        )

        for adj in debate.adjudicators.list:
            for pos in range(1, 5):
                bset.set_score(adj, side, pos, rr[adj][side][pos-1])

    # Pick a motion
    motions = debate.round.motion_set.all()
    motion = random.choice(motions)
    bset.motion = motion

    bset.discarded = discarded
    bset.confirmed = confirmed

    bset.save()

    # If the ballot is confirmed, the debate should be too.
    if confirmed:
        debate.result_status = m.Debate.STATUS_CONFIRMED
        debate.save()

    return bset

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("debate", type=int, help="Debate ID to add to")
    parser.add_argument("-t", "--type", type=str, help="'tabroom' or 'public'", choices=SUBMITTER_TYPE_MAP.keys(), default="tabroom")
    parser.add_argument("-u", "--user", type=str, help="User ID", default="original")
    parser.add_argument("-d", "--discarded", action="store_true", help="Ballot set is discarded")
    parser.add_argument("-c", "--confirmed", action="store_true", help="Ballot set is confirmed")
    args = parser.parse_args()

    submitter_type = SUBMITTER_TYPE_MAP[args.type]
    debate = m.Debate.objects.get(id=args.debate)
    user = User.objects.get(username=args.user)

    print debate

    try:
        bset = add_ballot_set(debate, submitter_type, user, args.discarded, args.confirmed)
    except ValueError, e:
        print "Error:", e

    print "Won by", bset.aff_win and "affirmative" or "negative"