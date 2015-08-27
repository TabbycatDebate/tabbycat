"""Confirms all feedbacks.
Will confirm all non-unique ones, so only the last one will remain confirmed.

TODO Implement as a Django admin action. Remove from management scripts.
"""

import header
from adjfeedback.models import AdjudicatorFeedback

import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.parse_args()

for feedback in AdjudicatorFeedback.objects.all():
    feedback.confirmed = True
    feedback.save()