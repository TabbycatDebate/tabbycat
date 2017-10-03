from django.conf import settings

from tournaments.models import Tournament


def debate_context(request):

    context = {
        'tabbycat_version': settings.TABBYCAT_VERSION or "",
        'tabbycat_codename': settings.TABBYCAT_CODENAME or "no codename",
        'all_tournaments': Tournament.objects.filter(active=True),
        'disable_sentry': settings.DISABLE_SENTRY or False
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
    menu = {}
    path = request.path
    if "admin" in path:
        if "options" in path or "participants" in path or "import" in path:
            menu['options_nav'] = True
            if "options" in path:
                menu['configuration_nav'] = True
            elif "participants" in path:
                menu['participants_nav'] = True
            elif "simple" in path:
                menu['import_nav'] = True
            elif "private-urls" in path:
                menu['private_urls_nav'] = True

        elif "feedback" in path:
            menu['feedback_nav'] = True
            if "latest" in path:
                menu['feedback_latest_nav'] = True
            elif "source" in path:
                menu['feedback_source_nav'] = True
            elif "target" in path:
                menu['feedback_target_nav'] = True
            elif "progress" in path:
                menu['feedback_progress_nav'] = True
            elif "add" in path:
                pass # No highlights
            else:
                menu['feedback_overview_nav'] = True

        elif "standings" in path:
            menu['standings_nav'] = True
            if "team" in path:
                menu['standings_team_nav'] = True
            elif "division" in path:
                menu['standings_division_nav'] = True
            elif "speaker" in path:
                menu['standings_speaker_nav'] = True
            elif "reply" in path:
                menu['standings_reply_nav'] = True
            elif "motions" in path:
                menu['feedback_motions_nav'] = True
            elif "diversity" in path:
                menu['standings_diversity_nav'] = True
            else:
                menu['standings_overview_nav'] = True

        elif "round" in path:
            menu['round_nav'] = True
            if "availability" in path:
                menu['availability_nav'] = True
            elif "display" in path:
                menu['display_nav'] = True
            elif "draw" in path:
                menu['draw_nav'] = True # After display
            elif "motions" in path:
                menu['motions_nav'] = True
            elif "checkin" in path:
                menu['checkins_nav'] = True
            elif "results" in path:
                menu['results_nav'] = True

        elif "break" in path:
            menu['break_nav'] = True
            if "adjudicators" in path:
                menu['break_adjudicators_nav'] = True
            if "teams" in path:
                menu['break_teams_nav'] = True
            else:
                menu['break_overview_nav'] = True

        elif "overview" in path:
            return {"overview_nav": True} # Other sections have overviews; go after
        elif "sides" in request.path:
            return {'sides_nav': True}
        elif "division_allocations" in request.path:
            return {'divisions_nav': True}
    else: # PUBLIC
        if "display" in request.path:
            return {'display_nav': True}
        elif "break" in request.path:
            return {'break_nav': True}
        elif "draw" in request.path:
            return {'draw_nav': True}
        elif "motions" in request.path:
            return {'motions_nav': True}
        elif "diversity" in request.path:
            return {'diversity_nav': True}
        elif "motions" in request.path:
            return {'motions_nav': True}
        elif "overview" in request.path:
            return {'overview_nav': True}
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

    return menu  # Context processors must return a dict
