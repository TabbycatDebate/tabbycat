"""Sandbox for figuring out how to do motion aggregations."""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
import sys
sys.path.append(os.path.abspath(os.path.join(os.environ.get("VIRTUAL_ENV"), "..")))
import debate.models as m
from django.db import models

import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("round", type=int, help="Round to look at")
args = parser.parse_args()

round = m.Round.objects.get(seq=args.round)

motions = m.Motion.objects.filter(round__seq=round.seq)

TEAM_SCORE_QUERY = """
    SELECT COUNT ("debate_teamscore"."score")
    FROM "debate_teamscore"
    JOIN "debate_ballotsubmission" ON "debate_teamscore"."ballot_submission_id" = "debate_ballotsubmission"."id"
    JOIN "debate_debateteam" ON "debate_teamscore"."debate_team_id" = "debate_debateteam"."id"
    WHERE "debate_ballotsubmission"."confirmed" = True
    AND "debate_ballotsubmission"."motion_id" = "debate_motion"."id"
    AND "debate_debateteam"."position" = '{pos:s}'
"""



motions = motions.extra({"chosen_in": """
        SELECT COUNT (*)
        FROM "debate_ballotsubmission"
        WHERE "debate_ballotsubmission"."confirmed" = True
        AND "debate_ballotsubmission"."motion_id" = "debate_motion"."id"
    """,
    "aff_score": TEAM_SCORE_QUERY.format(pos=m.DebateTeam.POSITION_AFFIRMATIVE),
    "neg_score": TEAM_SCORE_QUERY.format(pos=m.DebateTeam.POSITION_NEGATIVE),
})

for motion in motions:
    print "{0:30} {1:5} {2:5} {3:5}".format(motion.reference, motion.chosen_in, motion.aff_score, motion.neg_score)
