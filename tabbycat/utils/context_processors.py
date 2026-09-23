from django.conf import settings
from django.db.models import Case, Q, Value, When

from tournaments.models import Tournament


def debate_context(request):
    tournaments = Tournament.objects.filter(active=True)

    context = {
        'tabbycat_version': settings.TABBYCAT_VERSION or "",
        'tabbycat_codename': settings.TABBYCAT_CODENAME or "no codename",
        'all_tournaments': tournaments,
        'disable_sentry': getattr(settings, 'DISABLE_SENTRY', False),
        'on_local': getattr(settings, 'ON_LOCAL', False),
        'hmr': getattr(settings, 'USE_WEBPACK_SERVER', False),
    }

    if hasattr(request, 'tournament'):
        current_round = request.tournament.current_round

        # Put the current tournament first, include it even if inactive
        context['all_tournaments'] = Tournament.objects.filter(
            Q(active=True) | Q(pk=request.tournament.pk),
        ).annotate(
            is_current=Case(
                When(pk=request.tournament.pk, then=Value(0)),
                default=Value(1),
            ),
        ).order_by('is_current', 'seq')

        context.update({
            'tournament': request.tournament,
            'pref': request.tournament.preferences.by_name(),
            'current_round': current_round,
        })
        if hasattr(request, 'round'):
            context['round'] = request.round

    return context
