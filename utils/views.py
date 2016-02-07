from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.conf import settings
from django.http import Http404, HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.template import RequestContext
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.views.generic import View
from django.views.generic.base import ContextMixin
from django.utils.decorators import method_decorator

from ipware.ip import get_real_ip
from functools import wraps

def get_ip_address(request):
    ip = get_real_ip(request)
    if ip is None:
        return "0.0.0.0"
    return ip

class SuperuserRequiredMixin(UserPassesTestMixin):
    """Class-based view mixin. Requires user to be a superuser."""
    def test_func(self):
        return self.request.user.is_superuser


class TournamentMixin:
    """Class-based view mixin. Provides access to the tournament specified in
    URL named arguments. View classes using this mixin should call
    self.get_tournament() to retrieve the tournament.
    """
    tournament_slug_kwarg = "tournament_slug"
    tournament_cache_key = "{slug}_object"

    def get_tournament(self):
        # First look in self,
        if hasattr(self, "_tournament_from_url"):
            return self._tournament_from_url

        # then look in cache,
        slug = self.kwargs[self.tournament_slug_kwarg]
        key = self.tournament_cache_key.format(slug=slug)
        cached_tournament = cache.get(key)
        if cached_tournament:
            self._tournament_from_url = cached_tournament
            return cached_tournament

        # and if it was in neither place, retrieve the object
        tournament = get_object_or_404(Tournament, slug=slug)
        cache.set(key, tournament, None)
        self._tournament_from_url = tournament
        return tournament


class RoundMixin(TournamentMixin):
    """Class-based view mixin. Provides access to the round specified in URL
    named arguments. View classes using this mixin should call self.get_round()
    to retrieve the round. This mixin includes TournamentMixin, so classes
    using this mixin do not need to explicitly inherit from both.
    """
    round_seq_kwarg = "round_seq"
    round_cache_key = "{slug}_{seq}_object"

    def get_round(self):
        # First look in self,
        if hasattr(self, "_round_from_url"):
            return self._round_from_url

        # then look in cache,
        tournament = self.get_tournament()
        seq = self.kwargs[self.round_seq_kwarg]
        key = self.round_cache_key.format(slug=tournament.slug, seq=seq)
        cached_round = cache.get(key)
        if cached_round:
            self._round_from_url = cached_round
            return cached_round

        # and if it was in neither place, retrieve the object
        round = get_object_or_404(Round, tournament=tournament, seq=seq)
        cache.set(key, round, None)
        self._round_from_url = round
        return round


class PublicCacheMixin:
    """Mixin to cache page."""

    cache_timeout = settings.PUBLIC_PAGE_CACHE_TIMEOUT

    @method_decorator(cache_page(cache_timeout))
    def dispatch(self, *args, **kwargs):
        return super(PublicCacheMixin, self).dispatch(*args, **kwargs)


class PublicTournamentPageMixin(PublicCacheMixin, TournamentMixin):
    """Mixin for public tournament pages that are controlled by a tournament
    preference.

    Important: This mixin is incompatible with any user authentication mixin."""

    pref_name = None

    def dispatch(self, request, *args, **kwargs):
        tournament = self.get_tournament()
        if tournament.pref(self.pref_name):
            return super(PublicTournamentPageMixin, self).dispatch(request, *args, **kwargs)
        else:
            return redirect_tournament('tournament-public-index', tournament)


def admin_required(view_fn):
    return user_passes_test(lambda u: u.is_superuser)(view_fn)


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
                return redirect_tournament('tournament-public-index', tournament)
        return foo
    return bar

def round_view(view_fn):
    @wraps(view_fn)
    @tournament_view
    def foo(request, tournament, round_seq, *args, **kwargs):
        return view_fn(request, request.round, *args, **kwargs)
    return foo

def redirect_round(to, round, **kwargs):
    return redirect(to, tournament_slug=round.tournament.slug,
                    round_seq=round.seq, *kwargs)

def public_optional_round_view(preference_option):
    def bar(view_fn):
        @wraps(view_fn)
        @round_view
        def foo(request, round, *args, **kwargs):
            if round.tournament.pref(preference_option):
                return view_fn(request, round, *args, **kwargs)
            else:
                return redirect_tournament('tournament-public-index', round.tournament)
        return foo
    return bar

def expect_post(view_fn):
    @wraps(view_fn)
    def foo(request, *args, **kwargs):
        if request.method != "POST":
            return HttpResponseBadRequest("Expected POST")
        return view_fn(request, *args, **kwargs)
    return foo
