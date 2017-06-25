import math
from itertools import permutations

from django.db.models import Q

from .models import AdjudicatorAdjudicatorConflict, AdjudicatorConflict, AdjudicatorInstitutionConflict, DebateAdjudicator

from draw.models import DebateTeam


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
                conflict_messages[debate].append(("danger",
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


def populate_clashes(conflicts, conflict, type, for_type):
    if for_type == 'for_adjs':
        adj_or_team_id = conflict[0]
        conflictee_id = conflict[1]
    else:
        adj_or_team_id = conflict[1]
        conflictee_id = conflict[0]

    # Make the base dictionary structure for each adj if it doesn't exist already
    if adj_or_team_id not in conflicts[for_type]:
        conflicts[for_type][adj_or_team_id] = {'team': [], 'institution': [], 'adjudicator': []}
        conflicts[for_type][adj_or_team_id][type].append(conflictee_id)
    return conflicts


def get_clashes(t, r):
    # Grab all clashes data as value lists of conflict-er and conflict-ee
    filter = Q(adjudicator__tournament=t) | Q(adjudicator__tournament=None)
    team_clashes = AdjudicatorConflict.objects.filter(
        filter).values_list('adjudicator', 'team')
    institution_clashes = AdjudicatorInstitutionConflict.objects.filter(
        filter).values_list('adjudicator', 'institution')
    adj_clashes_a = AdjudicatorAdjudicatorConflict.objects.filter(
        filter).values_list('adjudicator', 'conflict_adjudicator')
    # Adj-adj clashes need to be symmetric; so reverse the order
    adj_clashes_b = AdjudicatorAdjudicatorConflict.objects.filter(
        filter).values_list('conflict_adjudicator', 'adjudicator')

    # Make a dictionary of clashes with team or adj ID as key
    clashes = {'for_teams': {}, 'for_adjs': {}}
    for clash in team_clashes:
        clashes = populate_clashes(clashes, clash, 'team', 'for_adjs')
    for clash in institution_clashes:
        clashes = populate_clashes(clashes, clash, 'institution', 'for_adjs')
    for clash in adj_clashes_a:
        clashes = populate_clashes(clashes, clash, 'adjudicator', 'for_adjs')
    for clash in adj_clashes_b:
        clashes = populate_clashes(clashes, clash, 'adjudicator', 'for_adjs')
    for clash in team_clashes:
        clashes = populate_clashes(clashes, clash, 'adjudicator', 'for_teams')

    return clashes


def populate_histories(histories, seen_adj_or_team, seen_adj_or_team_histories,
                       type, for_type, current_round):
    adj_or_team_id = seen_adj_or_team[0]

    # Make the base dictionary structure for each adj if it doesn't exist already
    if adj_or_team_id not in histories[for_type]:
        histories[for_type][adj_or_team_id] = {'team': [], 'adjudicator': []}

    seen_round_debate_id = seen_adj_or_team[1]
    seen_round_seq = seen_adj_or_team[2]

    # We don't know who they saw just based on a DebateAdjudicator/Team; so we need
    # to match things upagainst the other objects
    for history in seen_adj_or_team_histories:
        debate_id = history[1]
        check_team_or_adj_id = history[0]

        if type is 'adjudicator' and adj_or_team_id == check_team_or_adj_id:
            # Don't match conflicts to self
            continue
        if seen_round_debate_id == debate_id:
            # If the root DA/DT saw this DT/DA
            histories[for_type][adj_or_team_id][type].append(
                {'ago': current_round.seq - seen_round_seq, 'id': history[0]})

    return histories


def get_histories(t, r):

    adj_histories = DebateAdjudicator.objects.filter(
        debate__round__tournament=t, debate__round__seq__lt=r.seq).select_related(
            'debate__round').values_list('adjudicator', 'debate', 'debate__round__seq').order_by('-debate__round__seq')
    team_histories = DebateTeam.objects.filter(
        debate__round__tournament=t, debate__round__seq__lt=r.seq).select_related(
            'debate__round').values_list('team', 'debate', 'debate__round__seq').order_by('-debate__round__seq')

    # Make a dictionary of conflicts with adj or team ID as key
    histories = {'for_teams': {}, 'for_adjs': {}}
    for seen_adj in adj_histories:
        histories = populate_histories(histories, seen_adj, adj_histories,
                                       'adjudicator', 'for_adjs', r)
        histories = populate_histories(histories, seen_adj, team_histories,
                                       'team', 'for_adjs', r)
    for seen_team in team_histories:
        histories = populate_histories(histories, seen_team, adj_histories,
                                       'adjudicator', 'for_teams', r)

    return histories
