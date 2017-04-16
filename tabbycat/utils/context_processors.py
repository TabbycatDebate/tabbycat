from django.conf import settings

from tournaments.models import Tournament


def debate_context(request):

    context = {
        'tabbycat_version': settings.TABBYCAT_VERSION or "",
        'tabbycat_codename': settings.TABBYCAT_CODENAME or "no codename",
        'all_tournaments': Tournament.objects.filter(active=True),
    }

    if hasattr(request, 'tournament'):
        context.update({
            'tournament': request.tournament,
            'pref': request.tournament.preferences.by_name(),
            'current_round': request.tournament.get_current_round_cached,
        })
        if hasattr(request, 'round'):
            context['round'] = request.round

    return context


def get_menu_highlight(request):
    if "overview" in request.path:
        return {"overview_nav": True}
    elif "option" in request.path:
        return {'options_nav': True} # Must be above feedback given fb options
    elif "sides" in request.path:
        return {'sides_nav': True}
    elif "availability" in request.path:
        return {'availability_nav': True}
    elif "ballots" in request.path:
        return {'ballots_nav': True}
    elif "break" in request.path:
        return {'break_nav': True}
    elif "division_allocations" in request.path:
        return {'divisions_nav': True}
    elif "display" in request.path:
        return {'display_nav': True}
    elif "draw" in request.path:
        return {'draw_nav': True}
    elif "motions" in request.path:
        return {'motions_nav': True}
    elif "diversity" in request.path:
        return {'diversity_nav': True}
    elif "feedback" in request.path and "add" in request.path:
        return {'enter_feedback_nav': True}
    elif "feedback_progress" in request.path:
        return {'feedback_progress_nav': True}
    elif "feedback" in request.path:
        return {'feedback_nav': True}
    elif "randomised" in request.path:
        return {'import_random': True}
    elif "import" in request.path:
        return {'import_nav': True}
    elif "motions" in request.path:
        return {'motions_nav': True}
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
