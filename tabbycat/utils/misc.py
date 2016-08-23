from django.core.exceptions import SuspiciousFileOperation
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from ipware.ip import get_real_ip
from whitenoise.storage import CompressedManifestStaticFilesStorage


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


class SquashedWhitenoiseStorage(CompressedManifestStaticFilesStorage):
    '''Hack to get around dependencies throwing collectstatic errors'''

    def url(self, name, **kwargs):
        try:
            return super(SquashedWhitenoiseStorage, self).url(name, **kwargs)
        except SuspiciousFileOperation:
            # Triggers within jet CSS files link to images outside path
            return name
