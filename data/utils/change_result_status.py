"""Changes all debates in a round to STATUS_NONE."""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
import sys
sys.path.append(os.path.abspath(os.path.join(os.environ.get("VIRTUAL_ENV"), "..")))
import debate.models as m

import csv

import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("round", type=int, help="Round to change")
args = parser.parse_args()
round = args.round

for debate in m.Debate.objects.filter(round__seq=round):
    print debate
    debate.result_status = m.Debate.STATUS_NONE
    debate.save()