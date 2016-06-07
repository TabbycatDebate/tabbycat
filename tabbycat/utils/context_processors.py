from django.conf import settings

from tournaments.models import Tournament


def debate_context(request):

    if hasattr(request, 'tournament'):
        d = {
            'tournament': request.tournament,
            'pref': request.tournament.preferences.by_name(),
            'current_round': request.tournament.get_current_round_cached,
            'tabbycat_version': settings.TABBYCAT_VERSION,
            'tabbycat_codename': settings.TABBYCAT_CODENAME,
        }
        if hasattr(request, 'round'):
            d['round'] = request.round
            if request.round.prev:
                d['previous_round'] = request.round.prev
            else:
                d['previous_round'] = False

        d['all_tournaments'] = Tournament.objects.filter(active=True)

        return d

    return {}


def get_menu_highlight(request):
    if "side_allocations" in request.path:
        return {'sides_nav': True}
    elif "availability" in request.path:
        return {'availability_nav': True}
    elif "ballots" in request.path:
        return {'ballots_nav': True}
    elif "break" in request.path:
        return {'break_nav': True}
    elif "division_allocations" in request.path:
        return {'divisions_nav': True}
    elif "draw" in request.path:
        return {'draw_nav': True}
    elif "feedback" in request.path and "add" in request.path:
        return {'enter_feedback_nav': True}
    elif "feedback_progress" in request.path:
        return {'feedback_progress_nav': True}
    elif "feedback" in request.path:
        return {'feedback_nav': True}
    elif "import" in request.path:
        return {'import_nav': True}
    elif "motions" in request.path:
        return {'motions_nav': True}
    elif "option" in request.path:
        return {'options_nav': True}
    elif "overview" in request.path:
        return {'overview_nav': True}
    elif "participants" in request.path:
        return {'participants_nav': True}
    elif "results" in request.path and "add" in request.path:
        return {'enter_ballots_nav': True}
    elif "results" in request.path and "admin" in request.path:
        return {'ballots_nav': True}
    elif "results" in request.path:
        return {'results_nav': True}
    elif "standings" in request.path:
        return {'standings_nav': True}
    elif "tab" in request.path and "team" in request.path:
        return {'tab_team_nav': True}
    elif "tab" in request.path and "speaker" in request.path:
        return {'tab_speaker_nav': True}
    elif "tab" in request.path and "pros" in request.path:
        return {'tab_pros_nav': True}
    elif "tab" in request.path and "novices" in request.path:
        return {'tab_novices_nav': True}
    elif "tab" in request.path and "replies" in request.path:
        return {'tab_replies_nav': True}
    else:
        return {}  # Context processors must return a dict
