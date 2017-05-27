"""Generates random testdata for test_result.py, and prints the dict for copy
and paste into test_result.py."""

import random
import pprint

SPEAKERS_PER_TEAM = 3
ADJS_PER_DEBATE = 2
TEAMS_PER_DEBATE = 2

testdata = dict()

testdata['scores'] = [[[float(random.randint(70, 80)) for pos in range(SPEAKERS_PER_TEAM)] +
                      [float(random.randint(70, 80))/2] for team in range(TEAMS_PER_DEBATE)] for adj in range(ADJS_PER_DEBATE)]

testdata['totals_by_adj'] = [[sum(team) for team in adj] for adj in testdata['scores']]

testdata['winner_by_adj'] = ['aff' if (adj[0] > adj[1]) else 'neg' for adj in testdata['totals_by_adj']]

testdata['winner'] = 'aff' if (testdata['winner_by_adj'].count('aff') > testdata['winner_by_adj'].count('neg')) else 'neg'

majority = [adj for i, adj in enumerate(testdata['scores']) if testdata['winner_by_adj'][i] == testdata['winner']]

testdata['majority_scores'] = [[sum(adj[team][pos]for adj in majority)/len(majority) for pos in range(SPEAKERS_PER_TEAM+1)]
                               for team in range(TEAMS_PER_DEBATE)]

testdata['majority_totals'] = [sum(team) for team in testdata['majority_scores']]

aff_margin = testdata['majority_totals'][0] - testdata['majority_totals'][1]
testdata['majority_margins'] = [aff_margin, -aff_margin]

testdata['num_adjs_for_team'] = [testdata['winner_by_adj'].count('aff'), testdata['winner_by_adj'].count('neg')]
testdata['num_adjs'] = ADJS_PER_DEBATE
testdata['num_speakers_per_team'] = SPEAKERS_PER_TEAM

pprint.pprint(testdata)
