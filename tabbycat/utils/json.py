import json

from django.forms.models import model_to_dict


def debates_to_json(draw, r):

    def debate_to_dictionary(debate):
        return {
            'id': debate.id,
            'bracket': debate.bracket,
            'importance': debate.importance,
            'venue': model_to_dict(debate.venue),
            'teams': [team.serialize() for team in debate.teams],
            'positions': ['Aff', 'Neg'],
            'panel': [{
                'adjudicator': adj.serialize(),
                'position': position,
            } for adj, position in debate.adjudicators.with_debateadj_types()],
        }

    data = [debate_to_dictionary(debate) for debate in draw]
    return json.dumps(data)
