# Use this to make BallotSubmission status consistent with debate statuses.

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
import sys
sys.path.append(".")
import debate.models as m

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