"""Simulates a competition with a given number of teams and institutions, up to
a given number of rounds. Prints out the teams (identified by numbers),
institutions (letters), number of wins, history (team numbers) and aff counts.

This script does not interact with the database at all. It is used for
generating test cases for the tests in test_draw.py. It also does not have any
unit tests itself: it is used to generate test cases to insert into
test_draw.py.

This script must be run from the directory it is in."""

import argparse
import os.path
import random
import string
import sys

draw_dir = os.path.abspath(os.path.join("..", ".."))
if draw_dir not in sys.path:
    sys.path.append(draw_dir)
print(draw_dir)
del draw_dir

from draw.generator import DrawGenerator  # noqa: E402 (has to come after path modification above)
from draw.tests.utils import TestTeam     # noqa: E402 (has to come after path modification above)

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("rounds", type=int, help="Number of rounds")
parser.add_argument("teams", type=int, help="Number of teams")
parser.add_argument("insts", type=int, help="Number of institutions")
args = parser.parse_args()

R = args.rounds
T = args.teams
K = args.insts

assert(T % 2 == 0)

teams = list()
for i in range(1, T+1):
    team = TestTeam(i, random.choice(string.ascii_uppercase[:K]), 0, list(), side_history=[0, 0])
    teams.append(team)

brackets = dict()

for i in range(R):
    wins_set = set([team.points for team in teams])
    brackets.clear()
    for wins in wins_set:
        brackets[wins] = [t for t in teams if t.points == wins]
    ppdg = DrawGenerator("two", "power_paired", teams)
    ppdg._pullup_top(brackets)

    for wins, bracket_teams in brackets.items():
        random.shuffle(bracket_teams)
        N = len(bracket_teams) // 2
        winners = bracket_teams[:N]
        losers = bracket_teams[N:]
        for winner, loser in zip(winners, losers):
            winner.hist.append(loser)
            loser.hist.append(winner)
            winner_side_diff = winner.side_history[0] - winner.side_history[1]
            loser_side_diff = loser.side_history[0] - loser.side_history[1]
            if winner_side_diff > loser_side_diff:
                aff = loser
                neg = winner
            elif loser_side_diff > winner_side_diff:
                aff = winner
                neg = loser
            else:
                shuffled = [winner, loser]
                random.shuffle(shuffled)
                aff, neg = shuffled
            aff.side_history[0] += 1
            neg.side_history[1] += 1
        for team in winners:
            team.points += 1

for team in sorted(teams, key=lambda x: x.points, reverse=True):
    print("({id}, '{inst}', {points}, {hist}, {side_history}),".format(
        id=team.id, inst=team.institution, points=team.points,
        hist=[t.id for t in team.hist], side_history=team.side_history))

print("")

for team in sorted(teams, key=lambda x: x.points, reverse=True):
    print("{id}, {inst}, {points}, {hist}, {side_history}".format(
        id=team.id, inst=team.institution, points=team.points,
        hist=", ".join([str(t.id) for t in team.hist]), side_history=team.side_history))
