"""Checks for feedbacks with more than one version."""

import header

from participants.models import Adjudicator
from feedbacks.models import AdjudicatorFeedback

import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.parse_args()

for adj in Adjudicator.objects.all():
    seen = list()
    for feedback in AdjudicatorFeedback.objects.filter(adjudicator=adj):
        if feedback.source in seen:
            continue
        seen.append(feedback.source)
        others = AdjudicatorFeedback.objects.filter(adjudicator=adj,
            source_adjudicator=feedback.source_adjudicator,
            source_team=feedback.source_team).order_by('version')
        num = others.count()
        if num > 1:
            print " *** Adjudicator: {0}, from: {1}, {2:d} versions".format(adj, feedback.source, num)
            for other in others:
                #print other.timestamp.isoformat()
                print "   {4:>3} {3:<12} {2} {5} {1} {0:.1f}".format(other.score, other.version, other.round, other.user, other.id, other.confirmed and "c" or "-")
