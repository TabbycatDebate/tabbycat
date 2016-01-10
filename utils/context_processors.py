from tournaments.models import Tournament

def debate_context(request):

    if hasattr(request, 'tournament'):
        d = {
            'tournament'              : request.tournament,
            'preferences'             : request.tournament.preferences,
            'current_round'           : request.tournament.get_current_round_cached,
        }
        if hasattr(request, 'round'):
            d['round'] = request.round
        d['all_tournaments'] = Tournament.objects.filter(active=True)
        return d

    return {}

def get_menu_highlight(request):
    if "side_allocations" in request.path:
        return {'sides_nav': True}
    elif "ballots" in request.path:
        return {'ballots_nav': True}
    elif "results" in request.path:
        return {'ballots_nav': True}
    elif "draw" in request.path:
        return {'draw_nav': True}
    elif "feedback" in request.path:
        return {'feedback_nav': True}
    elif "division_allocations" in request.path:
        return {'divisions_nav': True}
    elif "standings" in request.path:
        return {'standings_nav': True}
    elif "break" in request.path:
        return {'break_nav': True}
    else:
        return {'no_highlight': True} # Context processors must return a dict
