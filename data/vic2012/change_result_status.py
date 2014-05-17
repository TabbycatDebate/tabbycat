import csv
import debate.models as m

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("round", type=int, help="Round to change")
args = parser.parse_args()
round = args.round

for debate in m.Debate.objects.filter(round__seq=round):
    print debate
    debate.result_status = m.Debate.STATUS_NONE
    debate.save()