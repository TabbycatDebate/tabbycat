"""Sandbox for figuring out how to do team standings with more complicated rules."""

import header
import debate.models as m
import results.models as m
from django.db import models
import random

import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("round", type=int, help="Round to look at")
parser.add_argument("--who-beat-whom", action="store_true", help="Print who-beat-whom results")
args = parser.parse_args()

round = m.Round.objects.get(seq=args.round)

teams = m.Team.objects

teams = teams.filter(
    institution__tournament = round.tournament,
    debateteam__debate__round__seq__lte = round.seq,
)

EXTRA_QUERY = """
    SELECT DISTINCT SUM({field:s})
    FROM "results_teamscore"
    JOIN "results_ballotsubmission" ON "results_teamscore"."ballot_submission_id" = "results_ballotsubmission"."id"
    JOIN "draws_debateteam" ON "results_teamscore"."debate_team_id" = "draws_debateteam"."id"
    JOIN "draws_debate" ON "draws_debateteam"."debate_id" = "draws_debate"."id"
    JOIN "debate_round" ON "draws_debate"."round_id" = "debate_round"."id"
    WHERE "results_ballotsubmission"."confirmed" = True
    AND "draws_debateteam"."team_id" = "debate_team"."id"
    AND "debate_round"."seq" <= {round:d}
"""
teams = teams.extra({
    "points": EXTRA_QUERY.format(field="points", round=round.seq),
    "speaker_score": EXTRA_QUERY.format(field="score", round=round.seq)}
).distinct()

print teams.query
print teams.count()

# Add draw strength annotation.
for team in teams:
    draw_strength = 0
    # Find all teams that they've faced.
    for dt in team.debateteam_set.all():
        # Can't just use dt.opposition.team.points, as dt.opposition.team isn't annotated.
        draw_strength += teams.get(id=dt.opposition.team.id).points
    team.draw_strength = draw_strength

for team in teams:
    print "{0:<20} {1:>10} {2:>7.2f} {3:>3}".format(team.short_name, team.points, team.speaker_score, team.draw_strength)

print "=" * 50

def who_beat_whom(team1, team2):
    """Returns a positive value if team1 won more debates, a negative value
    if team2 won more, 0 if the teams won the same number against each other
    or haven't faced each other."""
    # Find all debates between these two teams
    def get_wins(team, other):
        ts = rm.TeamScore.objects.filter(
            ballot_submission__confirmed=True,
            debate_team__team=team,
            debate_team__debate__debateteam__team=other).aggregate(models.Sum('points'))
        return ts["points__sum"]
    wins1 = get_wins(team1, team2)
    wins2 = get_wins(team2, team1)
    # Print this to the logs, just so we know it happened
    print "who beat whom, {0} vs {1}: {2} wins against {3}".format(team1, team2, wins1, wins2)
    return cmp(wins1, wins2)

def cmp_teams(team1, team2):
    """Returns 1 if team1 ranks ahead of team2, -1 if team2 ranks ahead of team1,
    and 0 if they rank the same. Requires access to teams, so that it knows whether
    it can apply who-beat-whom."""
    # If there are only two teams on this number of points, or points/speakers,
    # or points/speaks/draw-strength, then use who-beat-whom.
    def two_teams_left(key):
        return key(team1) == key(team2) and len(filter(lambda x: key(x) == key(team1), teams)) == 2
    if two_teams_left(lambda x: x.points) or two_teams_left(lambda x: (x.points, x.speaker_score)) \
            or two_teams_left(lambda x: (x.points, x.speaker_score, x.draw_strength)):
        winner = who_beat_whom(team1, team2)
        if winner != 0: # if this doesn't help, keep going
            return winner
    key = lambda x: (x.points, x.speaker_score, x.draw_strength)
    return cmp(key(team1), key(team2))

if args.who_beat_whom:

    import itertools
    total = 0
    for team1, team2 in itertools.combinations(teams, 2):
        result = who_beat_whom(team1, team2)
        if result:
            print str(team1).ljust(20), str(team2).ljust(20), result
            total += 1

    print "total:", total
    print "=" * 50

sorted_teams = list(teams)
random.shuffle(sorted_teams) # shuffle first, so that if teams are truly equal, they'll be in random order
sorted_teams.sort(cmp=cmp_teams, reverse=True)

for team in sorted_teams:
    print "{0:<20} {1:>10} {2:>7.2f} {3:>3}".format(team.short_name, team.points, team.speaker_score, team.draw_strength)
