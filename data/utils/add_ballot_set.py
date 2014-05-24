import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
import sys
sys.path.append(".")
import debate.models as m
from django.contrib.auth.models import User
from debate.result import BallotSet
import random

submitter_type_map = {
    'tabroom': m.BallotSubmission.SUBMITTER_TABROOM,
    'public':  m.BallotSubmission.SUBMITTER_PUBLIC
}

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("debate", type=int, help="Debate ID to add to")
parser.add_argument("-t", "--type", type=str, help="'tabroom' or 'public'", choices=submitter_type_map.keys(), default="tabroom")
parser.add_argument("-u", "--user", type=str, help="User ID", default="original")
args = parser.parse_args()

submitter_type = submitter_type_map[args.type]
debate = m.Debate.objects.get(id=args.debate)

# Create a new BallotSubmission
bsub = m.BallotSubmission(submitter_type=submitter_type, debate=debate)
bsub.user = User.objects.get(username=args.user)

# Pick a motion
motions = debate.round.motion_set.all()
motion = random.choice(motions)
bsub.motion = motion

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

bset.save()