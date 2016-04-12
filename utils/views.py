"""NOTE: All of the functions in this module are being phased out. All new views
should use the Django class-based views framework, and use the mixins in
mixins.py (in this directory) instead.
"""

from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from django.conf import settings
from django.http import Http404, HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.template import RequestContext
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import cache_page
from django.core.cache import cache

from functools import wraps
from warnings import warn
from .misc import get_ip_address as misc_get_ip_address
from .misc import redirect_tournament as misc_redirect_tournament

def get_ip_address(request):
    warn("utils.views.get_ip_address is deprecated, import from utils.misc instead")
    return misc_get_ip_address(request)


def admin_required(view_fn):
    return user_passes_test(lambda u: u.is_superuser)(view_fn)


def tournament_view(view_fn):
    @wraps(view_fn)
    def foo(request, tournament_slug, *args, **kwargs):
        return view_fn(request, request.tournament, *args, **kwargs)

    return foo


def redirect_tournament(to, tournament, **kwargs):
    warn("utils.views.redirect_tournament is deprecated, import from utils.misc instead")
    return misc_redirect_tournament(to, tournament, **kwargs)


def public_optional_tournament_view(preferences_option):
    def bar(view_fn):
        @wraps(view_fn)
        @tournament_view
        def foo(request, tournament, *args, **kwargs):
            if tournament.pref(preferences_option):
                return view_fn(request, tournament, *args, **kwargs)
            else:
                return redirect_tournament('tournament-public-index',
                                           tournament)

        return foo

    return bar


def round_view(view_fn):
    @wraps(view_fn)
    @tournament_view
    def foo(request, tournament, round_seq, *args, **kwargs):
        return view_fn(request, request.round, *args, **kwargs)

    return foo


def redirect_round(to, round, **kwargs):
    return redirect(to,
                    tournament_slug=round.tournament.slug,
                    round_seq=round.seq,
                    *kwargs)


def public_optional_round_view(preference_option):
    def bar(view_fn):
        @wraps(view_fn)
        @round_view
        def foo(request, round, *args, **kwargs):
            if round.tournament.pref(preference_option):
                return view_fn(request, round, *args, **kwargs)
            else:
                return redirect_tournament('tournament-public-index',
                                           round.tournament)

        return foo

    return bar


def expect_post(view_fn):
    @wraps(view_fn)
    def foo(request, *args, **kwargs):
        if request.method != "POST":
            return HttpResponseBadRequest("Expected POST")
        return view_fn(request, *args, **kwargs)

    return foo

