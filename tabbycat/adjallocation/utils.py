import json
import math

from .models import AdjudicatorAdjudicatorConflict, AdjudicatorConflict, AdjudicatorInstitutionConflict, DebateAdjudicator

from availability.models import ActiveAdjudicator
from breakqual.utils import determine_liveness
from draw.models import DebateTeam
from participants.models import Adjudicator


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


def get_adjs(r):

    active = ActiveAdjudicator.objects.filter(
        round=r).values_list(
        'adjudicator')
    active = [(a[0], None) for a in active]

    allocated_adjs = DebateAdjudicator.objects.select_related(
        'debate__round', 'adjudicator').filter(
        debate__round=r).values_list(
        'adjudicator', 'debate')
    allocated_ids = [a[0] for a in allocated_adjs]

    # Remove active adjs that have been assigned to debates
    unallocated_adjs = [a for a in active if a[0] not in allocated_ids]
    all_ids = list(allocated_adjs) + list(unallocated_adjs)

    # Grab all the actual adjudicator objects
    active_adjs = Adjudicator.objects.select_related(
        'institution', 'tournament', 'tournament__current_round').in_bulk(
        [a[0] for a in all_ids])

    # Build a list of adjudicator objects (after setting their debate property)
    round_adjs = []
    for round_id, round_adj in zip(all_ids, list(active_adjs.values())):
        round_adj.debate = round_id[1]
        round_adjs.append(round_adj)

    return round_adjs


def populate_conflicts(adjs, teams):
    # Grab all conflicts data and assign it
    teamconflicts = AdjudicatorConflict.objects.filter(
        adjudicator__in=adjs).values_list(
        'adjudicator', 'team')
    institutionconflicts = AdjudicatorInstitutionConflict.objects.filter(
        adjudicator__in=adjs).values_list(
        'adjudicator', 'institution')
    adjconflicts = AdjudicatorAdjudicatorConflict.objects.filter(
        adjudicator__in=adjs).values_list(
        'adjudicator', 'conflict_adjudicator')

    for a in adjs:
        a.personal_teams = [c[1] for c in teamconflicts if c[0] is a.id]
        a.institutional_institutions = [a.institution.id]
        a.institutional_institutions.extend(
            [c[1] for c in institutionconflicts if c[0] is a.id and c[1] is not a.institution.id])

        # Adj-adj conflicts should be symmetric
        a.personal_adjudicators = [c[1] for c in adjconflicts if c[0] is a.id]
        a.personal_adjudicators += [c[0] for c in adjconflicts if c[1] is a.id]

    for t in teams:
        t.personal_adjudicators = [c[0] for c in teamconflicts if c[1] is t.id]
        # For teams conflicted_institutions is a list of adjs due to the asymetric
        # nature of adjs having multiple instutitonal conflicts
        t.institutional_institutions = [t.institution.id]

    return adjs, teams


def populate_histories(adjs, teams, t, r):

    da_histories = DebateAdjudicator.objects.filter(
        debate__round__tournament=t, debate__round__seq__lt=r.seq, adjudicator__in=adjs).select_related(
        'debate__round').values_list(
        'adjudicator', 'debate', 'debate__round__seq', 'debate__round__name').order_by('-debate__round__seq')
    dt_histories = DebateTeam.objects.filter(
        debate__in=[c[1] for c in da_histories]).select_related(
        'debate__round').values_list(
        'team', 'debate').order_by('-debate__round__seq')

    for a in adjs:
        hists = []
        # Iterate over all DebateAdjudications from this adj
        for dah in [dah for dah in da_histories if dah[0] is a.id]:
            # Find the relevant DebateTeams from the matching debates
            hists.extend([{
                'team': dat[0],
                'ago': r.seq - dah[2],
                'name': dah[3]
            } for dat in dt_histories if dat[1] is dah[1]])
        a.histories = hists

    for t in teams:
        hists = []
        # Iterate over the DebateTeams for the matching teams
        for dat in [dat for dat in dt_histories if dat[0] is t.id]:
            # Iterate over the DebateAdjudicators to find the matching debates
            hists.extend([{
                'adj': dah[0],
                'ago': r.seq - dah[2],
                'name': dah[3]
            } for dah in da_histories if dah[1] is dat[1]])
        t.histories = hists

    return adjs, teams


def debates_to_json(draw, t, r):

    data = [{
        'id': debate.id,
        'bracket': debate.bracket,
        'importance': debate.importance,
        'aff_team': debate.aff_team.id,
        'neg_team': debate.neg_team.id,
        'panel': [{
            'id': a[1].id,
            'position': a[0]
        } for a in debate.adjudicators],

    } for debate in draw]
    return json.dumps(data)


def adjs_to_json(adjs, regions):
    """Converts to a standard JSON object for Vue components to use"""

    absolute_scores = [adj.score for adj in adjs]
    absolute_scores.sort()
    percentile_cutoffs = [(100 - i, percentile(absolute_scores, i/100)) for i in range(0,100,10)]
    percentile_cutoffs.reverse()

    data = {}
    for adj in adjs:
        data[adj.id] = {
            'id': adj.id,
            'name': adj.name,
            'allocated': True if adj.debate else False,
            'gender': adj.gender,
            'region': [r for r in regions if r['id'] is adj.institution.region.id][0] if adj.institution.region else '',
            'institution': {
                'id': adj.institution.id,
                'name': adj.institution.code,
                'code' : adj.institution.code,
                'abbreviation' : adj.institution.abbreviation
            },
            'score': "%.1f" % adj.score,
            'ranking': next(pc[0] for pc in percentile_cutoffs if pc[1] <= adj.score),
            'conflicts': {
                'personal_teams': adj.personal_teams,
                'institutional_conflicts': adj.institutional_institutions,
                'personal_adjudicators': adj.personal_adjudicators,
            },
            'hasPersonalConflict': False,
            'hasInstitutionalConflict': False,
            'histories': adj.histories,
        }

    return json.dumps(data)


def teams_to_json(teams, regions, categories, t, r):
    data = {}
    for team in teams:
        team_categories = team.break_categories.all().values_list('id', flat=True)
        break_categories = [{
            'id': bc['id'],
            'name': bc['name'],
            'seq': bc['seq'],
            'will_break': determine_liveness(bc, t, r, team.wins_count)
        } for bc in categories if bc['id'] in team_categories]

        data[team.id] = {
            'id': team.id,
            'name': team.short_name,
            'long_name': team.long_name,
            'uses_prefix': team.use_institution_prefix,
            'speakers': [{
                'name': s.name,
                'gender': s.gender
            } for s in team.speakers],
            'wins': team.wins_count,
            'region': [r for r in regions if r['id'] is team.institution.region.id][0] if team.institution.region else '',
            # TODO: Searching for break cats here incurs extra queries; should be done earlier
            'categories': break_categories,
            'institution': {
                'id': team.institution.id,
                'name': team.institution.code,
                'code' : team.institution.code,
                'abbreviation' : team.institution.abbreviation
            },
            'conflicts': {
                'personal_teams': [], # No team-team conflicts
                'institutional_conflicts': team.institutional_institutions,
                'personal_adjudicators': team.personal_adjudicators
            },
            'hasPersonalConflict': False,
            'hasInstitutionalConflict': False,
            'histories': team.histories,
        }
    return json.dumps(data)

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
