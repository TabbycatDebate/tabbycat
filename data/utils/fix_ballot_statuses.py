"""Makes BallotSubmission status consistent with debate statuses."""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
import sys
sys.path.append(os.path.abspath(os.path.join(os.environ.get("VIRTUAL_ENV"), "..")))

import debate.models as m

import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.parse_args()

for bsub in m.BallotSubmission.objects.all():
    debate_status = bsub.debate.result_status
    original = (bsub.discarded, bsub.confirmed)
    if debate_status == m.Debate.STATUS_NONE:
        bsub.discarded = True
        bsub.confirmed = False
    elif debate_status == m.Debate.STATUS_DRAFT:
        bsub.confirmed = False
    elif debate_status == m.Debate.STATUS_CONFIRMED:
        if not bsub.discarded:
            bsub.confirmed = True
    new = (bsub.discarded, bsub.confirmed)
    if original != new:
        print "%s changed from %s to %s" % (bsub, original, new)
        bsub.save()