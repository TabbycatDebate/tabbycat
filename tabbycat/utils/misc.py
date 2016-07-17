from ipware.ip import get_real_ip
from django.core.urlresolvers import reverse
from django.shortcuts import redirect


def get_ip_address(request):
    ip = get_real_ip(request)
    if ip is None:
        return "0.0.0.0"
    return ip


def redirect_tournament(to, tournament, **kwargs):
    return redirect(to, tournament_slug=tournament.slug, **kwargs)


def reverse_tournament(to, tournament, **kwargs):
    kwargs.setdefault('kwargs', {})
    kwargs['kwargs']['tournament_slug'] = tournament.slug
    return reverse(to, **kwargs)


def redirect_round(to, round, **kwargs):
    return redirect(to, tournament_slug=round.tournament.slug,
                    round_seq=round.seq, **kwargs)


def reverse_round(to, round, **kwargs):
    kwargs.setdefault('kwargs', {})
    kwargs['kwargs']['tournament_slug'] = round.tournament.slug
    kwargs['kwargs']['round_seq'] = round.seq
    return reverse(to, **kwargs)
