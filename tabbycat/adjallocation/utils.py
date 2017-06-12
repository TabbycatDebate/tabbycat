import json
import math
from itertools import permutations

from django.db.models import Q

from .models import AdjudicatorAdjudicatorConflict, AdjudicatorConflict, AdjudicatorInstitutionConflict, DebateAdjudicator

# from breakqual.utils import calculate_live_thresholds, determine_liveness
from draw.models import DebateTeam
# from participants.models import Adjudicator, Team
# from participants.prefetch import populate_feedback_scores, populate_win_counts


def adjudicator_conflicts_display(debates):
    """Returns a dict mapping elements (debates) in `debates` to a list of
    strings of explaining conflicts between adjudicators and teams, and
    conflicts between adjudicators and each other."""

    adjteamconflicts = {}
    for conflict in AdjudicatorConflict.objects.filter(adjudicator__debateadjudicator__debate__in=debates).distinct():
        adjteamconflicts.setdefault(conflict.adjudicator_id, []).append(conflict.team_id)
    adjinstconflicts = {}
    for conflict in AdjudicatorInstitutionConflict.objects.filter(adjudicator__debateadjudicator__debate__in=debates).distinct():
        adjinstconflicts.setdefault(conflict.adjudicator_id, []).append(conflict.institution_id)
    adjadjconflicts = {}
    for conflict in AdjudicatorAdjudicatorConflict.objects.filter(adjudicator__debateadjudicator__debate__in=debates).distinct():
        adjadjconflicts.setdefault(conflict.adjudicator_id, []).append(conflict.conflict_adjudicator_id)

    conflict_messages = {debate: [] for debate in debates}
    for debate in debates:
        for adjudicator in debate.adjudicators.all():
            for team in debate.teams:
                if team.id in adjteamconflicts.get(adjudicator.id, []):
                    conflict_messages[debate].append(("danger",
                        "Conflict between <strong>{adj}</strong> & <strong>{team}</strong>".format(
                            adj=adjudicator.name, team=team.short_name)
                    ))
                if team.institution_id in adjinstconflicts.get(adjudicator.id, []):
                    conflict_messages[debate].append(("danger",
                        "Conflict between <strong>{adj}</strong> & institution <strong>{inst}</strong> ({team})".format(
                            adj=adjudicator.name, team=team.short_name, inst=team.institution.code)
                    ))

        for adj1, adj2 in permutations(debate.adjudicators.all(), 2):
            if adj2.id in adjadjconflicts.get(adj1.id, []):
                conflict_messages[debate].append(("danger"
                    "Conflict between <strong>{adj}</strong> & <strong>{other}</strong>".format(
                        adj=adj1.name, other=adj2.name)
                ))

            if adj2.institution_id in adjinstconflicts.get(adj1.id, []):
                conflict_messages[debate].append(("danger",
                    "Conflict between <strong>{adj}</strong> & institution <strong>{inst}</strong> ({other})".format(
                        adj=adj1.name, other=adj2.name, inst=adj2.institution.code)
                ))

    return conflict_messages


def percentile(n, percent, key=lambda x:x):
    """
    Find the percentile of a list of values.

    @parameter N - is a list of values. Note N MUST BE already sorted.
    @parameter percent - a float value from 0.0 to 1.0.
    @parameter key - optional key function to compute value from each element of N.

    @return - the percentile of the values
    """
    if not n:
        return None
    k = (len(n)-1) * percent
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return key(n[int(k)])
    d0 = key(n[int(f)]) * (c-k)
    d1 = key(n[int(c)]) * (k-f)
    return d0+d1


def populate_conflicts(conflicts, conflict, type):
    adj_id = conflict[0]
    # Make the base dictionary structure for each adj if it doesn't exist already
    if adj_id not in conflicts:
        conflicts[adj_id] = {'team': [], 'institution': [], 'adjudicator': []}
    conflictee_id = conflict[1]
    conflicts[adj_id][type].append(conflictee_id)
    return conflicts


def get_conflicts(t, r):
    # Grab all conflicts data as value lists of conflict-er and conflict-ee
    filter = Q(adjudicator__tournament=t) | Q(adjudicator__tournament=None)
    team_conflicts = AdjudicatorConflict.objects.filter(
        filter).values_list('adjudicator', 'team')
    institution_conflicts = AdjudicatorInstitutionConflict.objects.filter(
        filter).values_list('adjudicator', 'institution')
    adj_conflicts_a = AdjudicatorAdjudicatorConflict.objects.filter(
        filter).values_list('adjudicator', 'conflict_adjudicator')
    # Adj-adj conflicts need to be symmetric; so reverse the order
    adj_conflicts_b = AdjudicatorAdjudicatorConflict.objects.filter(
        filter).values_list('conflict_adjudicator', 'adjudicator')

    conflicts = {} # Make a dictionary of conflicts with adj ID as key
    for conflict in team_conflicts:
        conflicts = populate_conflicts(conflicts, conflict, 'team')
    for conflict in institution_conflicts:
        conflicts = populate_conflicts(conflicts, conflict, 'institution')
    for conflict in adj_conflicts_a:
        conflicts = populate_conflicts(conflicts, conflict, 'adjudicator')
    for conflict in adj_conflicts_b:
        conflicts = populate_conflicts(conflicts, conflict, 'adjudicator')

    return json.dumps(conflicts)


def populate_histories(histories, seen, all_histories, type, current_round):
    adj_id = seen[0]
    # Make the base dictionary structure for each adj if it doesn't exist already
    if adj_id not in histories:
        histories[adj_id] = {'team': [], 'adjudicator': []}

    seen_round_debate_id = seen[1]
    seen_round_seq = seen[2]
    # We don't know who they saw just based on a DebateAdjudicator; so we need
    # to match things upagainst the other objcects
    for history in all_histories:
        check_debate_id = history[1]
        check_adj_id = history[0]
        if seen_round_debate_id == check_debate_id and adj_id != check_adj_id:
            histories[adj_id][type].append(
                {'ago': current_round.seq - seen_round_seq, type: history[0]})

    return histories


def get_histories(t, r):

    seen_adjudicators = DebateAdjudicator.objects.filter(
        debate__round__tournament=t, debate__round__seq__lt=r.seq).select_related(
            'debate__round').values_list('adjudicator', 'debate', 'debate__round__seq')
    seen_teams = DebateTeam.objects.filter(
        debate__round__tournament=t, debate__round__seq__lt=r.seq).select_related(
            'debate__round').values_list('team', 'debate', 'debate__round__seq')

    histories = {} # Make a dictionary of conflicts with adj ID as key
    for seen in seen_adjudicators:
        histories = populate_histories(histories, seen, seen_adjudicators, 'adjudicator', r)
    for seen in seen_teams:
        histories = populate_histories(histories, seen, seen_teams, 'team', r)

    return json.dumps(histories)


# REDUNDANT; although parts worth translating
# class AllocationTableBuilder(TabbycatTableBuilder):

#     def liveness(self, team, teams_count, prelims, current_round):
#         live_info = {'text': team.wins_count, 'tooltip': ''}

#         # The actual calculation should be shifed to be a cached method on
#         # the relevant break category
#         # print("teams count", teams_count)
#         # print("prelims", prelims)
#         # print("current_round", current_round)

#         highest_liveness = 3
#         for bc in team.break_categories.all():
#             # print(bc.name, bc.break_size)
#             import random
#             status = random.choice([1,2,3])
#             highest_liveness = 3
#             if status is 1:
#                 live_info['tooltip'] += 'Definitely in for the %s break<br>test' % bc.name
#                 if highest_liveness != 2:
#                     highest_liveness = 1  # Live not ins are the most important highlight
#             elif status is 2:
#                 live_info['tooltip'] += 'Still live for the %s break<br>test' % bc.name
#                 highest_liveness = 2
#             elif status is 3:
#                 live_info['tooltip'] += 'Cannot break in %s break<br>test' % bc.name

#         if highest_liveness is 1:
#             live_info['class'] = 'bg-success'
#         elif highest_liveness is 2:
#             live_info['class'] = 'bg-warning'

#         return live_info

#     def add_team_wins(self, draw, round, key):
#         prelims = self.tournament.prelim_rounds(until=round).count()
#         teams_count = self.tournament.team_set.count()

#         wins_head = {
#             'key': key,
#             'tooltip': "Number of wins a team is on; "
#         }
#         wins_data = []
#         for d in draw:
#             team = d.aff_team if key is "AW" else d.neg_team
#             wins_data.append(self.liveness(team, teams_count, prelims, round.seq))

#         self.add_column(wins_head, wins_data)

#     def add_debate_importances(self, draw, round):
#         importance_head = {
#             'key': 'importance',
#             'icon': 'glyphicon-fire',
#             'tooltip': "Set a debate's importance (higher receives better adjs)"
#         }
#         importance_data = [{
#             'component': 'debate-importance',
#             'id': d.id,
#             'sort': d.importance,
#             'importance': d.importance,
#             'url': reverse_tournament(
#                 'set_debate_importance',
#                 self.tournament,
#                 kwargs={'round_seq': round.seq})
#         } for d in draw]

#         self.add_column(importance_head, importance_data)
