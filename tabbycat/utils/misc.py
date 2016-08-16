from ipware.ip import get_real_ip
from django.core.urlresolvers import reverse
from django.shortcuts import redirect


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
