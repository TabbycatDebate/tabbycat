import json

from utils.tables import TabbycatTableBuilder
from utils.misc import reverse_tournament


def adjs_to_json(adj):
    """Converts to a standard JSON object for Vue components to use"""
    data = {
        'id': adj.id,
        'name': adj.name,
        'gender': adj.gender,
        'institution': {
            'id': adj.institution.id,
            'name': adj.institution.code,
        },
        'score': 4,
        'conflicts': [],
        'seen': [],
    }
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
