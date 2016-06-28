import json

from .models import AdjudicatorAdjudicatorConflict, AdjudicatorConflict, AdjudicatorInstitutionConflict, DebateAdjudicator

from availability.models import ActiveAdjudicator
from draw.models import DebateTeam
from participants.models import Adjudicator
from utils.tables import TabbycatTableBuilder
from utils.misc import reverse_tournament


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

    for ra in round_adjs:
        ra.rating = ra.score,

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
        a.institutional_institutions = [c[1] for c in institutionconflicts if c[0] is a.id]
        # Adj-adj conflicts should be symmetric
        a.personal_adjudicators = [c[1] for c in adjconflicts if c[0] is a.id]
        a.personal_adjudicators += [c[0] for c in adjconflicts if c[1] is a.id]

    for t in teams:
        t.personal_adjudicators = [c[0] for c in teamconflicts if c[1] is t.id]
        # For teams conflicted_institutions is a list of adjs due to the asymetric
        # nature of adjs having multiple instutitonal conflicts
        t.institutional_adjudicators = [c[0] for c in institutionconflicts if c[1] is t.institution.id]

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


def adjs_to_json(adjs):
    """Converts to a standard JSON object for Vue components to use"""

    data = [{
        'id': adj.id,
        'name': adj.name,
        'debate': adj.debate,
        'gender': adj.gender,
        'gender_name': adj.get_gender_display(),
        'region': adj.institution.region.id if adj.institution.region else '',
        'region_name': adj.institution.region.name if adj.institution.region else '',
        'institution': {
            'id': adj.institution.id,
            'name': adj.institution.code,
            'code' : adj.institution.code,
            'abbreviation' : adj.institution.abbreviation
        },
        'score': adj.rating,
        'conflicts': {
            'personal_teams': adj.personal_teams,
            'institutional_institutions': adj.institutional_institutions,
            'institutional_adjudicators': None,
            'personal_adjudicators': adj.personal_adjudicators,
        },
        'histories': adj.histories



    } for adj in adjs]
    return json.dumps(data)


def teams_to_json(teams):

    # TODO: histories and conflicts should be populated in a combined function along with adjs

    data = [{
        'id': team.id,
        'name': team.short_name,
        'long_name': team.long_name,
        'uses_prefix': team.use_institution_prefix,
        'speakers': [" " + s.name for s in team.speakers],
        # 'gender': adj.gender,
        'gender_name': team.gender_names,
        'region': team.institution.region.id if team.institution.region else '',
        'region_name': team.institution.region.name if team.institution.region else '',
        'institution': {
            'id': team.institution.id,
            'name': team.institution.code,
            'code' : team.institution.code,
            'abbreviation' : team.institution.abbreviation
        },
        'conflicts': {
            'personal_teams': [],
            'institutional_institutions': None,
            'institutional_adjudicators': team.institutional_adjudicators,
            'personal_adjudicators': team.personal_adjudicators
        },
        'histories': team.histories

    } for team in teams]
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
