from debate.models import Tournament, Round
from debate.models import Config

def debate_context(request):

    if hasattr(request, 'tournament'):
        d = {
            'tournament'        : request.tournament,
            'current_round'     : request.tournament.current_round,
            'show_emoji'        : request.tournament.config.get('show_emoji'),
            'show_institutions' : request.tournament.config.get('show_institutions'),
            'public_draw'       : request.tournament.config.get('public_draw'),
            'public_ballots'    : request.tournament.config.get('public_ballots'),
            'public_feedback'   : request.tournament.config.get('public_feedback'),
            'feedback_progress' : request.tournament.config.get('feedback_progress'),
            'tab_released'      : request.tournament.config.get('tab_released'),
        }
        if hasattr(request, 'round'):
            d['round'] = request.round
        return d
    return {}

