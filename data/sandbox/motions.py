"""Sandbox for figuring out how to do motion aggregations."""

import header
import tournaments.models as tm
import draws.models as dm
import motions.models as mm

from django.db import models

import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("round", type=int, help="Round to look at")
args = parser.parse_args()

round = tm.Round.objects.get(seq=args.round)

motions = mm.Motion.objects.filter(round__seq=round.seq)

TEAM_SCORE_QUERY = """
    SELECT COUNT ("results_teamscore"."score")
    FROM "results_teamscore"
    JOIN "results_ballotsubmission" ON "results_teamscore"."ballot_submission_id" = "results_ballotsubmission"."id"
    JOIN "draws_debateteam" ON "results_teamscore"."debate_team_id" = "draws_debateteam"."id"
    WHERE "results_ballotsubmission"."confirmed" = True
    AND "results_ballotsubmission"."motion_id" = "debate_motion"."id"
    AND "draws_debateteam"."position" = '{pos:s}'
"""



motions = motions.extra({"chosen_in": """
        SELECT COUNT (*)
        FROM "results_ballotsubmission"
        WHERE "results_ballotsubmission"."confirmed" = True
        AND "results_ballotsubmission"."motion_id" = "debate_motion"."id"
    """,
    "aff_score": TEAM_SCORE_QUERY.format(pos=dm.DebateTeam.POSITION_AFFIRMATIVE),
    "neg_score": TEAM_SCORE_QUERY.format(pos=dm.DebateTeam.POSITION_NEGATIVE),
})

for motion in motions:
    print "{0:30} {1:5} {2:5} {3:5}".format(motion.reference, motion.chosen_in, motion.aff_score, motion.neg_score)
