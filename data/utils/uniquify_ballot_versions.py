"""Makes BallotSubmission versions unique per debate as required.
See https://github.com/czlee/tabbycat/issues/38#issuecomment-44149213 for more
information."""

import header
import debate.models as m
import results.models as rm

import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.parse_args()

versions_so_far = dict.fromkeys(m.Debate.objects.all(), 1) # keys: Debates, values: version numbers

for bsub in rm.BallotSubmission.objects.all():
    bsub.version = versions_so_far[bsub.debate]
    versions_so_far[bsub.debate] += 1
    if bsub.version > 1:
        print "On version %d, %s" % (bsub.version, bsub)
    bsub.save()