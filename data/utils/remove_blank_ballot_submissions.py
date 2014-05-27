"""Removes all incomplete ballot submissions, i.e. ones without any scores attached."""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
import sys
sys.path.append(os.path.abspath(os.path.join(os.environ.get("VIRTUAL_ENV"), "..")))
import debate.models as m

import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--dry-run", action="store_true")
args = parser.parse_args()

for bsub in m.BallotSubmission.objects.all():
    ssba = m.SpeakerScoreByAdj.objects.filter(ballot_submission=bsub).exists()
    if not ssba:
        print "Deleting", bsub
        if not args.dry_run:
            bsub.delete()