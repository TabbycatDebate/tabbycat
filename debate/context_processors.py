from debate.models import Tournament, Round 

def debate_context(request):

    if hasattr(request, 'tournament'):
        d = {
            'tournament': request.tournament,
            'current_round': request.tournament.current_round,
        }
        if hasattr(request, 'round'):
            d['round'] = request.round
        return d
    return {}

