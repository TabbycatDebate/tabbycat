"""Simulates a competition with a given number of teams and institutions, up to
a given number of rounds. Prints out the teams (identified by numbers),
institutions (letters), number of wins, history (team numbers) and aff counts.

This script does not interact with the database at all. It is used for
generating test cases for the tests in test_draw.py. It also does not have any
unit tests itself: it is used to generate test cases to insert into
test_draw.py."""
from test_one_up_one_down import TestTeam
import os.path, sys
if os.path.abspath("..") not in sys.path: sys.path.append(os.path.abspath(".."))
from draw import DrawGenerator

import string
import random
import itertools

import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("rounds", type=int, help="Number of rounds")
parser.add_argument("teams", type=int, help="Number of teams")
parser.add_argument("insts", type=int, help="Number of institutions")
args = parser.parse_args()
R = args.rounds
T = args.teams
I = args.insts

assert(T % 2 == 0)

teams = list()
for i in range(1,T+1):
    team = TestTeam(i, random.choice(string.uppercase[:I]), 0, list(), aff_count=0)
    teams.append(team)

brackets = dict()

for i in range(R):
    wins_set = set([team.points for team in teams])
    brackets.clear()
    for wins in wins_set:
        brackets[wins] = [t for t in teams if t.points == wins]
    ppdg = DrawGenerator("power_paired", teams)
    ppdg._pullup_top(brackets)

    for wins, bracket_teams in brackets.iteritems():
        random.shuffle(bracket_teams)
        N = len(bracket_teams)/2
        winners = bracket_teams[:N]
        losers = bracket_teams[N:]
        for winner, loser in zip(winners, losers):
            winner.hist.append(loser)
            loser.hist.append(winner)
            if winner.aff_count > loser.aff_count:
                loser.aff_count += 1
            elif loser.aff_count > winner.aff_count:
                winner.aff_count += 1
            else:
                random.choice([winner, loser]).aff_count += 1
        for team in winners:
            team.points += 1

for team in sorted(teams, key=lambda x: x.points, reverse=True):
    print "({id}, '{inst}', {points}, {hist}, {aff_count}),".format(
        id=team.id, inst=team.institution, points=team.points,
            hist=[t.id for t in team.hist], aff_count=team.aff_count)
print
for team in sorted(teams, key=lambda x: x.points, reverse=True):
    print "{id}, {inst}, {points}, {hist}, {aff_count}".format(
        id=team.id, inst=team.institution, points=team.points,
            hist=", ".join([str(t.id) for t in team.hist]), aff_count=team.aff_count)
