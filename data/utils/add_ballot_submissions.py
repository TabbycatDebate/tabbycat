"""Add a ballot submission to everything. Method:
 1. Create a BallotSubmission for every debate.
 2. Give it default submitted-by fields, etc.
 3. Make it the confirmed_ballot of the Debate
 4. Make it the confirmed_ballot of every SpeakerScoreByAdj, TeamScore and SpeakerScore for that debate

Use this when migrating from a database that has no BallotSubmissions.

This requires a user called "original" to exist. You need to set this up
before running the script if you don't have one.
"""
import header
import tournaments.models as m
import draws.models as dm
import motions.models as mm
import debate.results as rm
from django.contrib.auth.models import User

import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.parse_args()

for debate in dm.Debate.objects.all():
    bs = rm.BallotSubmission(submitter_type=rm.BallotSubmission.SUBMITTER_TABROOM, debate=debate)
    bs.user = User.objects.get(username='original')
    bs.confirmed = True
    bs.save()
    debate.confirmed_ballot = bs
    for ssba in rm.SpeakerScoreByAdj.objects.filter(debate_team__debate = debate):
        ssba.ballot_submission = bs
        ssba.save()
    for ss in rm.SpeakerScore.objects.filter(debate_team__debate = debate):
        ss.ballot_submission = bs
        ss.save()
    for ts in rm.TeamScore.objects.filter(debate_team__debate = debate):
        ts.ballot_submission = bs
        ts.save()

for bs in rm.BallotSubmission.objects.all():
    bs.confirmed = True
    bs.save()

# Add motions
import random
for round in tm.Round.objects.all():
    motions = mm.Motion.objects.filter(round=round)
    for ballots in rm.BallotSubmission.objects.filter(debate__round=round):
        ballots.motion = random.choice(motions)
        print "Chose motion", ballots.motion.reference, "for ballot", ballots
        ballots.save()