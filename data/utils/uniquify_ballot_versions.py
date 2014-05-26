# Use this to make BallotSubmission versions unique per debate as required.
# See https://github.com/czlee/tabbycat/issues/38#issuecomment-44149213 for more
# information.

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
import sys
sys.path.append(".")
import debate.models as m

versions_so_far = dict.fromkeys(m.Debate.objects.all(), 1) # keys: Debates, values: version numbers

for bsub in m.BallotSubmission.objects.all():
    bsub.version = versions_so_far[bsub.debate]
    versions_so_far[bsub.debate] += 1
    if bsub.version > 1:
        print "On version %d, %s" % (bsub.version, bsub)
    bsub.save()