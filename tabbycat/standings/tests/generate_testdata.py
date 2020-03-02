"""Generates random testdata for test_result.py, and prints the dict for copy
and paste into test_result.py."""

import pprint
import random
from operator import itemgetter

TEAMS = ['A', 'B', 'C', 'D']
DRAW_FOR_WHOLE_TOURNAMENT = [['AB', 'CD'], ['AC', 'BD'], ['AB', 'CD']]
SPEAKERS_PER_TEAM = 3
ADJS_PER_DEBATE = 3
TOTAL_SCORE_MEAN  = 75 * 3.5
TOTAL_SCORE_STDEV = 10

METRICS = [
    ("points", "speaks_sum", "draw_strength", "margin_sum"),
    # ("points", "wbw", "speaks_sum", "wbw"),
    ("points", "speaks_sum"),
]

teamscores_by_team = {t: [] for t in TEAMS}

# Comment out this line and add a new line setting up results to use doctored
# scores.
results = [{debate: {team: {"score": round(
    random.normalvariate(75*3.5, 10)*2)/2} for team in debate} for debate in rd}
    for rd in DRAW_FOR_WHOLE_TOURNAMENT]

# For example:
# results = [{'AB': {'A': {'score': 269.5}, 'B': {'score': 254.0}},
#             'CD': {'C': {'score': 262.5}, 'D': {'score': 260.0}}},
#            {'AC': {'A': {'score': 249.0}, 'C': {'score': 261.0}},
#             'BD': {'B': {'score': 260.5}, 'D': {'score': 267.0}}},
#            {'AB': {'A': {'score': 259.5}, 'B': {'score': 271.5}},
#             'CD': {'C': {'score': 253.0}, 'D': {'score': 265.0}}}]

print("Scores, i.e. initial 'results' before it gets populated with everything else:")
print("------------------------------------------------------------------------------")
pprint.pprint(results)
print("")

for rd in results:
    for debate in rd.values():
        teamscores = list(debate.values())
        assert teamscores[0]["score"] != teamscores[1]["score"], "There was a draw, please try again."
        for this, other in ((0, 1), (1, 0)):
            teamscores[this]["margin"] = teamscores[this]["score"] - teamscores[other]["score"]
            teamscores[this]["win"] = teamscores[this]["score"] > teamscores[other]["score"]
            teamscores[this]["points"] = int(teamscores[this]["win"])
        for team, teamscore in debate.items():
            teamscores_by_team[team].append(teamscore)

# Populate standings metrics that are just sums of teamscore fields, and
# initialize metrics that aren't.
standings = {}
for team, teamscores in teamscores_by_team.items():
    standings[team] = {
        "speaks_sum": sum(teamscore["score"] for teamscore in teamscores),
        "margin_sum": sum(teamscore["margin"] for teamscore in teamscores),
        "points": sum(teamscore["points"] for teamscore in teamscores),
        "draw_strength": 0,  # Initialize
        "against": dict.fromkeys([t for t in TEAMS if t is not team], "n/a"),  # Initialize,
    }

# Build up standings metrics that require reference to opponents
for rd in results:
    for debate in rd.values():
        teamscores = list(debate.items())
        for a, b in ((0, 1), (1, 0)):
            team, score = teamscores[a]
            opponent, _ = teamscores[b]
            if standings[team]["against"][opponent] == "n/a":
                standings[team]["against"][opponent] = score["points"]
            else:
                standings[team]["against"][opponent] += score["points"]
            standings[team]["draw_strength"] += standings[opponent]["points"]

# Generate rankings and who-beat-whom tables
rankings = dict()
for metrics in METRICS:
    ranking = sorted(TEAMS, key=lambda t: itemgetter(*metrics)(standings[t]), reverse=True)
    rankings[metrics] = ranking

testdata = {
    "teamscores": results,
    "teams": TEAMS,
    "standings": standings,
    "rankings": rankings,
}

print("Test data, to be copied to test:")
print("--------------------------------")
pprint.pprint(testdata, width=100)
print("")
