import logging
from secrets import SystemRandom
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from django.shortcuts import redirect
from django.urls import reverse
from django.utils import formats, timezone, translation
from ipware.ip import get_real_ip

logger = logging.getLogger(__name__)


def get_ip_address(request):
    ip = get_real_ip(request)
    if ip is None:
        return "0.0.0.0"
    return ip


def redirect_tournament(to, tournament, *args, **kwargs):
    return redirect(to, tournament_slug=tournament.slug, *args, **kwargs)


def reverse_tournament(to, tournament, *args, **kwargs):
    kwargs.setdefault('kwargs', {})
    kwargs['kwargs']['tournament_slug'] = tournament.slug
    return reverse(to, *args, **kwargs)


def redirect_round(to, round, *args, **kwargs):
    return redirect(to, tournament_slug=round.tournament.slug,
                    round_seq=round.seq, *args, **kwargs)


def reverse_round(to, round, *args, **kwargs):
    kwargs.setdefault('kwargs', {})
    kwargs['kwargs']['tournament_slug'] = round.tournament.slug
    kwargs['kwargs']['round_seq'] = round.seq
    return reverse(to, *args, **kwargs)


def badge_datetime_format(timestamp):
    lang = translation.get_language()
    for module in formats.get_format_modules(lang):
        fmt = getattr(module, "BADGE_DATETIME_FORMAT", None)
        if fmt is not None:
            break
    else:
        logger.error("No BADGE_DATETIME_FORMAT found for language: %s", lang)
        fmt = "d/m H:i"   # 18/02 16:33, as fallback in case nothing is defined

    localized_time = timezone.localtime(timestamp)
    return formats.date_format(localized_time, format=fmt)


def ranks_dictionary(tournament, score_min, score_max):
    """ Used for both adjudicator ranks and venue priorities """
    score_range = score_max - score_min
    return [
        {'pk': 'a+', 'fields': {'name': 'A+', 'cutoff': (score_range * 0.9) + score_min}},
        {'pk': 'a',  'fields': {'name': 'A', 'cutoff': (score_range * 0.8) + score_min}},
        {'pk': 'a-', 'fields': {'name': 'A-', 'cutoff': (score_range * 0.7) + score_min}},
        {'pk': 'b+', 'fields': {'name': 'B+', 'cutoff': (score_range * 0.6) + score_min}},
        {'pk': 'b',  'fields': {'name': 'B', 'cutoff': (score_range * 0.5) + score_min}},
        {'pk': 'b-', 'fields': {'name': 'B-', 'cutoff': (score_range * 0.4) + score_min}},
        {'pk': 'c+', 'fields': {'name': 'C+', 'cutoff': (score_range * 0.3) + score_min}},
        {'pk': 'c',  'fields': {'name': 'C', 'cutoff': (score_range * 0.2) + score_min}},
        {'pk': 'f',  'fields': {'name': 'F', 'cutoff': score_min}},
    ]


def generate_identifier_string(charset, length):
    """Used in privateurl/checkin identifier generation"""
    return ''.join(SystemRandom().choice(charset) for _ in range(length))


def add_query_string_parameter(url, key, value):
    scheme, netloc, path, params, query, fragment = urlparse(url)
    query_parts = parse_qs(query)
    query_parts[key] = value
    query = urlencode(query_parts, safe='/')
    return urlunparse((scheme, netloc, path, params, query, fragment))
