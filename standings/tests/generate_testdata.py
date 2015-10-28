"""Generates random testdata for test_result.py, and prints the dict for copy
and paste into test_result.py."""

import random
import pprint

TEAMS = 'ABCD'
DRAW_FOR_WHOLE_TOURNAMENT = [['AB', 'CD'], ['AC', 'BD'], ['AB', 'CD']]
SPEAKERS_PER_TEAM = 3
ADJS_PER_DEBATE = 3
TOTAL_SCORE_MEAN  = 75 * 3.5
TOTAL_SCORE_STDEV = 10

teamscores_by_team = {t: [] for t in TEAMS}

# Comment out this line and add a new line setting up results to use doctored
# scores.
results = [{debate: {team: {"score": round(random.normalvariate(75*3.5, 10)*2)/2}
        for team in debate} for debate in rd} for rd in DRAW_FOR_WHOLE_TOURNAMENT]

# For example:
# results = [{'AB': {'A': {'score': 260.5}, 'B': {'score': 254.0}},
#             'CD': {'C': {'score': 257.0}, 'D': {'score': 260.0}}},
#            {'AC': {'A': {'score': 256.5}, 'C': {'score': 261.0}},
#             'BD': {'B': {'score': 260.5}, 'D': {'score': 267.0}}},
#            {'AB': {'A': {'score': 259.5}, 'B': {'score': 271.5}},
#             'CD': {'C': {'score': 253.0}, 'D': {'score': 265.0}}}]

print("Scores, i.e. initial 'results' before it gets populated with everything else:")
print("------------------------------------------------------------------------------")
pprint.pprint(results)
print("")

for rd in results:
    for debate in rd.values():
        teamscores = debate.values()
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
        "score": sum(teamscore["score"] for teamscore in teamscores),
        "margin": sum(teamscore["margin"] for teamscore in teamscores),
        "points": sum(teamscore["points"] for teamscore in teamscores),
        "against": dict.fromkeys([t for t in TEAMS if t is not team], "n/a"), # initialize
        "draw_strength": 0, # initialize
    }

# Build up standings metrics that require reference to opponents
for rd in results:
    for debate in rd.values():
        teamscores = debate.items()
        for a, b in ((0, 1), (1, 0)):
            team, score = teamscores[a]
            opponent, _ = teamscores[b]
            if standings[team]["against"][opponent] is "n/a":
                standings[team]["against"][opponent] = score["points"]
            else:
                standings[team]["against"][opponent] += score["points"]
            standings[team]["draw_strength"] += standings[opponent]["points"]

testdata = {
    "teamscores": results,
    "teams": TEAMS,
    "standings": standings,
}

print("Test data, to be copied to test:")
print("--------------------------------")
pprint.pprint(testdata, width=100)
print("")