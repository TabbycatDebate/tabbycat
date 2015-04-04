"""Adds a randomly generated ballot set to the given debates."""

import header
import debate.models as m
from django.contrib.auth.models import User
from debate.result import BallotSet
import random

SUBMITTER_TYPE_MAP = {
    'tabroom': m.BallotSubmission.SUBMITTER_TABROOM,
    'public':  m.BallotSubmission.SUBMITTER_PUBLIC
}

def add_ballot_set(debate, submitter_type, user, discarded=False, confirmed=False, min_score=72, max_score=78):

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
            s = [random.randint(min_score, max_score) for i in range(debate.round.tournament.LAST_SUBSTANTIVE_POSITION)]
            s.append(random.randint(min_score, max_score)/2.0)
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
        for i in range(1, debate.round.tournament.LAST_SUBSTANTIVE_POSITION+1):
            bset.set_speaker(
                team = side,
                position = i,
                speaker = speakers[i - 1],
            )
        bset.set_speaker(
            team = side,
            position = debate.round.tournament.REPLY_POSITION,
            speaker = speakers[0]
        )

        for adj in debate.adjudicators.list:
            for pos in debate.round.tournament.POSITIONS:
                bset.set_score(adj, side, pos, rr[adj][side][pos-1])

    # Pick a motion
    motions = debate.round.motion_set.all()
    if motions:
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
    parser.add_argument("debate", type=int, nargs='+', help="Debate ID(s) to add to")
    parser.add_argument("-t", "--type", type=str, help="'tabroom' or 'public'", choices=SUBMITTER_TYPE_MAP.keys(), default="tabroom")
    parser.add_argument("-u", "--user", type=str, help="User ID", default="original")
    status = parser.add_mutually_exclusive_group(required=True)
    status.add_argument("-d", "--discarded", action="store_true", help="Ballot set is discarded")
    status.add_argument("-c", "--confirmed", action="store_true", help="Ballot set is confirmed")
    parser.add_argument("-m", "--min-score", type=float, help="Minimum speaker score (for substantive)", default=72)
    parser.add_argument("-M", "--max-score", type=float, help="Maximum speaker score (for substantive)", default=78)
    args = parser.parse_args()

    submitter_type = SUBMITTER_TYPE_MAP[args.type]
    if submitter_type == m.BallotSubmission.SUBMITTER_TABROOM:
        user = User.objects.get(username=args.user)
    else:
        user = None

    for debate_id in args.debate:
        debate = m.Debate.objects.get(id=debate_id)

        print debate

        try:
            bset = add_ballot_set(debate, submitter_type, user, args.discarded, args.confirmed, args.min_score, args.max_score)
        except ValueError, e:
            print "Error:", e

        print "  Won by", bset.aff_win and "affirmative" or "negative"