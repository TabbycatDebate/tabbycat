"""Removes all incomplete ballot submissions, i.e. ones without any scores attached."""

import header
import results.models as rm

import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--dry-run", action="store_true")
args = parser.parse_args()

for bsub in rm.BallotSubmission.objects.all():
    ssba = rm.SpeakerScoreByAdj.objects.filter(ballot_submission=bsub).exists()
    if not ssba:
        print("Deleting", bsub)
        if not args.dry_run:
            bsub.delete()