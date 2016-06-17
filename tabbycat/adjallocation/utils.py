import json

from utils.tables import TabbycatTableBuilder
from utils.misc import reverse_tournament


def adjsToJson(adj):
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
