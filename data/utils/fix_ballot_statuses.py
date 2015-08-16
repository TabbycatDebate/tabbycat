"""Makes BallotSubmission status consistent with debate statuses."""

import header
import results.models as rm
from draw.models import Debate

import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.parse_args()

for bsub in rm.BallotSubmission.objects.all():
    debate_status = bsub.debate.result_status
    original = (bsub.discarded, bsub.confirmed)
    if debate_status == Debate.STATUS_NONE:
        bsub.discarded = True
        bsub.confirmed = False
    elif debate_status == Debate.STATUS_DRAFT:
        bsub.confirmed = False
    elif debate_status == Debate.STATUS_CONFIRMED:
        if not bsub.discarded:
            bsub.confirmed = True
    new = (bsub.discarded, bsub.confirmed)
    if original != new:
        print "%s changed from %s to %s" % (bsub, original, new)
        bsub.save()