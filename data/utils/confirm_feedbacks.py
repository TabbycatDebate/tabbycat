"""Confirms all feedbacks.
Will confirm all non-unique ones, so only the last one will remain confirmed."""

import header
from feedbacks.models import AdjudicatorFeedback

import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.parse_args()

for feedback in AdjudicatorFeedback.objects.all():
    feedback.confirmed = True
    feedback.save()