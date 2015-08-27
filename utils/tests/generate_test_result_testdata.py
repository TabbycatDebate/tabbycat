"""Generates random testdata for test_result.py, and prints the dict for copy
and paste into test_result.py."""

import random
testdata = dict()
testdata['scores'] = [[[float(random.randint(70,80)) for pos in range(3)] +
        [float(random.randint(70,80))/2] for team in range(2)] for adj in range(3)]
testdata['totals_by_adj'] = [[sum(team) for team in adj] for adj in testdata['scores']]
testdata['winner_by_adj'] = [int(adj[0] < adj[1]) for adj in testdata['totals_by_adj']]
testdata['winner'] = int(testdata['winner_by_adj'].count(0) < testdata['winner_by_adj'].count(1))
majority = [adj for i, adj in enumerate(testdata['scores']) if testdata['winner_by_adj'][i] == testdata['winner']]
testdata['majority_scores'] = [[sum(adj[team][pos]for adj in majority)/len(majority) for pos in range(4)] for team in range(2)]
testdata['majority_totals'] = [sum(team) for team in testdata['majority_scores']]

print(testdata)