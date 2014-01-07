import csv
import debate.models as m
import random

reader = csv.reader(open("motions.csv"))
for text, reference, round in reader:
    round = m.Round.objects.get(seq=int(round))
    motion = m.Motion(text=text, reference=reference, round=round)
    motion.save()
    print "Added motion", motion.reference, "for round", round.seq

for round in m.Round.objects.all():
    motions = m.Motion.objects.filter(round=round)
    for debate in m.Debate.objects.filter(round=round):
        debate.motion = random.choice(motions)
        print "Chose motion", debate.motion.reference, "for debate", debate
        debate.save()