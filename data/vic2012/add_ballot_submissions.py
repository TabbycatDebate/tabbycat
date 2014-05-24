import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
import sys
sys.path.append(".")
import debate.models as m
from django.contrib.auth.models import User

# Add a ballot submission to everything. Method:
#  1. Create a BallotSubmission for every debate.
#  2. Give it default submitted-by fields, etc.
#  3. Make it the confirmed_ballot of the Debate
#  4. Make it the confirmed_ballot of every SpeakerScoreByAdj, TeamScore and SpeakerScore for that debate

for debate in m.Debate.objects.all():
    bs = m.BallotSubmission(submitter_type=m.BallotSubmission.SUBMITTER_TABROOM, debate=debate)
    bs.user = User.objects.get(username='original')
    bs.confirmed = True
    bs.save()
    debate.confirmed_ballot = bs
    for ssba in m.SpeakerScoreByAdj.objects.filter(debate_team__debate = debate):
        ssba.ballot_submission = bs
        ssba.save()
    for ss in m.SpeakerScore.objects.filter(debate_team__debate = debate):
        ss.ballot_submission = bs
        ss.save()
    for ts in m.TeamScore.objects.filter(debate_team__debate = debate):
        ts.ballot_submission = bs
        ts.save()

for bs in m.BallotSubmission.objects.all():
    bs.confirmed = True
    bs.save()

# Add motions
import random
for round in m.Round.objects.all():
    motions = m.Motion.objects.filter(round=round)
    for ballots in m.BallotSubmission.objects.filter(debate__round=round):
        ballots.motion = random.choice(motions)
        print "Chose motion", ballots.motion.reference, "for ballot", ballots
        ballots.save()