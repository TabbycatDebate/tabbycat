from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.conf import settings
from django.http import Http404, HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.template import RequestContext
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import cache_page

from ipware.ip import get_real_ip
from functools import wraps
from standings.standings import PRECEDENCE_BY_RULE


def get_ip_address(request):
    ip = get_real_ip(request)
    if ip is None:
        return "0.0.0.0"
    return ip


def admin_required(view_fn):
    return user_passes_test(lambda u: u.is_superuser)(view_fn)


class SuperuserRequiredMixin(UserPassesTestMixin):
    """Class-based view mixin, requires user to be a superuser."""

    def test_func(self):
        return self.request.user.is_superuser


def tournament_view(view_fn):
    @wraps(view_fn)
    def foo(request, tournament_slug, *args, **kwargs):
        return view_fn(request, request.tournament, *args, **kwargs)

    return foo


def redirect_tournament(to, tournament, **kwargs):
    return redirect(to, tournament_slug=tournament.slug, **kwargs)


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


def relevant_team_standings_metrics(tournament):
    rule = tournament.pref('team_standings_rule')
    precedence = PRECEDENCE_BY_RULE[rule]
    metrics = dict()
    metrics["draw_strength"] = "draw_strength" in precedence
    metrics["sum_of_margins"] = "margins" in precedence
    metrics["who_beat_whom"] = "wbw" in precedence
    return metrics
