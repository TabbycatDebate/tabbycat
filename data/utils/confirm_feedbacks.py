"""Confirms all feedbacks.
Will confirm all non-unique ones, so only the last one will remain confirmed."""

import header
import debate.models as m

import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.parse_args()

for feedback in m.AdjudicatorFeedback.objects.all():
    feedback.confirmed = True
    feedback.save()