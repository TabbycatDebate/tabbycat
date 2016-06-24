import json

from .models import DebateAdjudicator, AdjudicatorConflict, AdjudicatorInstitutionConflict, AdjudicatorAdjudicatorConflict

from availability.models import ActiveAdjudicator
from draw.models import DebateTeam
from participants.models import Adjudicator
from utils.tables import TabbycatTableBuilder
from utils.misc import reverse_tournament

def populate_adjs_data(r):
    t = r.tournament

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

    # Grab all conflicts data and assign it
    teamconflicts = AdjudicatorConflict.objects.filter(
        adjudicator__in=round_adjs).values_list(
        'adjudicator', 'team')
    institutionconflicts = AdjudicatorInstitutionConflict.objects.filter(
        adjudicator__in=round_adjs).values_list(
        'adjudicator', 'institution')
    adjconflicts = AdjudicatorAdjudicatorConflict.objects.filter(
        adjudicator__in=round_adjs).values_list(
        'adjudicator', 'adjudicator')
    for a in round_adjs:
        a.adjteam = [c[1] for c in teamconflicts if c[0] is a.id]
        a.adjinstitution = [c[1] for c in institutionconflicts if c[0] is a.id]
        a.adjadj = [c[1] for c in adjconflicts if c[0] is a.id]

    da_histories = DebateAdjudicator.objects.filter(
        debate__round__tournament=t, debate__round__seq__lte=r.seq, adjudicator__in=round_adjs).select_related(
        'debate__round').values_list(
        'adjudicator', 'debate', 'debate__round__seq', 'debate__round__name')
    dt_histories = DebateTeam.objects.filter(
        debate__in=[c[1] for c in da_histories]).values_list(
        'team', 'debate')

    for a in round_adjs:
        hists = []
        # Iterate over all DebateAdjudications from this adj
        for dah in [dah for dah in da_histories if dah[0] is a.id]:
            # Find the relevant DebateTeams from the matching debates
            for dat in [dat for dat in dt_histories if dat[1] is dah[1]]:
                hists.append({
                    'team': dat[0],
                    'round_seq': dah[2],
                    'round_name': dah[3]
                })
        a.histories = hists

    for ra in round_adjs:
        ra.rating = ra.score,

    return round_adjs


def adjs_to_json(adjs):
    """Converts to a standard JSON object for Vue components to use"""
    data = [{
        'id': adj.id,
        'name': adj.name,
        'debate': adj.debate,
        'gender': adj.gender,
        'institution': {
            'id': adj.institution.id,
            'name': adj.institution.code,
            'code' : adj.institution.code,
            'abbreviation' : adj.institution.abbreviation
        },
        'score': adj.rating,
        'conflicts': {
            'adjteam': adj.adjteam,
            'adjinstitution': adj.adjinstitution,
            'adjadj': adj.adjadj,
        },
        'histories': adj.histories

    } for adj in adjs]
    return json.dumps(data)


class AllocationTableBuilder(TabbycatTableBuilder):

    def liveness(self, team, teams_count, prelims, current_round):
        live_info = {'text': team.wins_count, 'tooltip': ''}

        # The actual calculation should be shifed to be a cached method on
        # the relevant break category
        # print("teams count", teams_count)
        # print("prelims", prelims)
        # print("current_round", current_round)

        highest_liveness = 3
        for bc in team.break_categories.all():
            # print(bc.name, bc.break_size)
            import random
            status = random.choice([1,2,3])
            highest_liveness = 3
            if status is 1:
                live_info['tooltip'] += 'Definitely in for the %s break<br>test' % bc.name
                if highest_liveness != 2:
                    highest_liveness = 1  # Live not ins are the most important highlight
            elif status is 2:
                live_info['tooltip'] += 'Still live for the %s break<br>test' % bc.name
                highest_liveness = 2
            elif status is 3:
                live_info['tooltip'] += 'Cannot break in %s break<br>test' % bc.name

        if highest_liveness is 1:
            live_info['class'] = 'bg-success'
        elif highest_liveness is 2:
            live_info['class'] = 'bg-warning'

        return live_info

    def add_team_wins(self, draw, round, key):
        prelims = self.tournament.prelim_rounds(until=round).count()
        teams_count = self.tournament.team_set.count()

        wins_head = {
            'key': key,
            'tooltip': "Number of wins a team is on; "
        }
        wins_data = []
        for d in draw:
            team = d.aff_team if key is "AW" else d.neg_team
            wins_data.append(self.liveness(team, teams_count, prelims, round.seq))

        self.add_column(wins_head, wins_data)

    def add_debate_importances(self, draw, round):
        importance_head = {
            'key': 'importance',
            'icon': 'glyphicon-fire',
            'tooltip': "Set a debate's importance (higher receives better adjs)"
        }
        importance_data = [{
            'component': 'debate-importance',
            'id': d.id,
            'sort': d.importance,
            'importance': d.importance,
            'url': reverse_tournament(
                'set_debate_importance',
                self.tournament,
                kwargs={'round_seq': round.seq})
        } for d in draw]

        self.add_column(importance_head, importance_data)
