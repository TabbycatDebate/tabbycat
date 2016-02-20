from django.views.generic import View
from django.views.generic.base import ContextMixin
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from actionlog.models import ActionLogEntry

from .misc import get_ip_address

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
        return super().dispatch(*args, **kwargs)


class PublicTournamentPageMixin(TournamentMixin):
    """Mixin for public tournament pages that are controlled by a tournament
    preference."""

    public_page_preference = None

    def dispatch(self, request, *args, **kwargs):
        tournament = self.get_tournament()
        if tournament.pref(self.public_page_preference):
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect_tournament('tournament-public-index', tournament)


class SingleObjectByRandomisedUrlMixin(SingleObjectMixin):
    """Mixin for URLs that reference teams/adjudicators by randomised URL."""
    slug_field = 'url_key'
    slug_url_kwarg = 'url_key'
    query_pk_and_slug = True


class LogActionMixin:
    """Mixin for views that should log an action in the action log when a form
    is successfully submitted."""

    action_log_type = None

    def get_action_log_type(self):
        """Returns the value that should go in the type field of the
        ActionLogEntry instance. The default implementation returns
        self.action_log_type. Subclasses may override this method."""
        return self.action_log_type

    def get_action_log_fields(self, **kwargs):
        """Returns a dict that should be passed as keyword arguments to the
        ActionLogEntry instance. Subclasses should implement this method by
        adding to the dictionary `kwargs` and calling the super() method.

        The default implementation checks if there is a valid user and
        tournament, and if so, adds those keyword arguments if they're not
        already there."""

        if hasattr(self, 'get_tournament'):
            kwargs.setdefault('tournament', self.get_tournament())
        if hasattr(self.request, 'user'):
            kwargs.setdefault('user', self.request.user)
        return kwargs

    def form_valid(self, form):
        ip_address = get_ip_address(self.request)
        ActionLogEntry.objects.log(type=self.get_action_log_type(),
                ip_address=ip_address, **self.get_action_log_fields())
        return super().form_valid(form)
