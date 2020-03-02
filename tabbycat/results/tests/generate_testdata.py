"""Generates random testdata for test_result.py, and prints the dict for copy
and paste into test_result.py."""

import pprint
import random
from statistics import mean

SPEAKERS_PER_TEAM = 3
ADJS_PER_DEBATE = 3
TEAMS_PER_DEBATE = 2

# Generate data
# Replace with fixed data if you want fixed data
scores = [[[float(random.randint(70, 80)) for pos in range(SPEAKERS_PER_TEAM)] +
          [float(random.randint(70, 80))/2] for team in range(TEAMS_PER_DEBATE)]
          for adj in range(ADJS_PER_DEBATE)]
declared_winners = [random.choice(['aff', 'neg']) for adj in range(ADJS_PER_DEBATE)]

testdata = dict()

# Metadata
testdata['num_adjs'] = ADJS_PER_DEBATE
testdata['num_speakers_per_team'] = SPEAKERS_PER_TEAM

# Generate scores
testdata['input'] = input_data = dict()
input_data['scores'] = scores
input_data['declared_winners'] = declared_winners

# Fields that don't depend on scoresheet type
testdata['common'] = common_fields = dict()
common_fields['totals_by_adj'] = totals_by_adj = [[sum(team) for team in adj] for adj in scores]

common_fields['everyone_scores'] = [[mean(adj[team][pos] for adj in scores) for pos in range(SPEAKERS_PER_TEAM+1)]
                               for team in range(TEAMS_PER_DEBATE)]
common_fields['everyone_totals'] = [sum(team) for team in common_fields['everyone_scores']]
aff_margin = common_fields['everyone_totals'][0] - common_fields['everyone_totals'][1]
common_fields['everyone_margins'] = [aff_margin, -aff_margin]

# Winners, according to scoresheet type
testdata['high-required'] = {
    'winner_by_adj': ['aff' if (adj[0] > adj[1]) else
                      'neg' if (adj[1] > adj[0]) else None
                      for adj in totals_by_adj],
}
testdata['low-allowed'] = {
    'winner_by_adj': declared_winners,
}
testdata['tied-allowed'] = {
    'winner_by_adj': ['aff' if (adj[0] >= adj[1]) and declared == 'aff' else
                      'neg' if (adj[1] >= adj[0]) and declared == 'neg' else
                      None for adj, declared in zip(totals_by_adj, declared_winners)],
}

for scoresheet_type in ['high-required', 'low-allowed', 'tied-allowed']:

    fields = testdata[scoresheet_type]
    winner_by_adj = fields['winner_by_adj']

    fields['sheets_valid'] = [winner is not None for winner in winner_by_adj]
    fields['valid'] = all(fields['sheets_valid'])

    if not fields['valid']:
        continue

    # Decision
    fields['num_adjs_for_team'] = [winner_by_adj.count('aff'), winner_by_adj.count('neg')]
    fields['winner'] = winner = 'aff' if (winner_by_adj.count('aff') > winner_by_adj.count('neg')) else 'neg'

    # Scores excluding dissenters
    majority = [adj for winner_by_adj, adj in zip(winner_by_adj, scores) if winner_by_adj == winner]
    fields['majority_adjs'] = [i for i, winner_by_adj in enumerate(winner_by_adj) if winner_by_adj == winner]
    fields['majority_scores'] = [[mean(adj[team][pos] for adj in majority) for pos in range(SPEAKERS_PER_TEAM+1)]
                                   for team in range(TEAMS_PER_DEBATE)]
    fields['majority_totals'] = [sum(team) for team in fields['majority_scores']]
    aff_margin = fields['majority_totals'][0] - fields['majority_totals'][1]
    fields['majority_margins'] = [aff_margin, -aff_margin]

pprint.pprint(testdata, width=110)
