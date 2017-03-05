import logging

from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import NoReverseMatch
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.detail import SingleObjectMixin

from utils.misc import redirect_tournament, reverse_round, reverse_tournament
from utils.mixins import TabbycatPageTitlesMixin

from .models import Round, Tournament

logger = logging.getLogger(__name__)


class TournamentMixin(TabbycatPageTitlesMixin):
    """Mixin for views that relate to a tournament, and are specified as
    relating to a tournament in the URL.

    Views using this mixin should have a `tournament_slug` group in their URL's
    regular expression. They should then call `self.get_tournament()` to
    retrieve the tournament.
    """
    tournament_slug_url_kwarg = "tournament_slug"
    tournament_cache_key = "{slug}_object"
    tournament_redirect_pattern_name = None

    def get_tournament(self):
        # First look in self,
        if hasattr(self, "_tournament_from_url"):
            return self._tournament_from_url

        # then look in cache,
        slug = self.kwargs[self.tournament_slug_url_kwarg]
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

    def get_redirect_url(self, *args, **kwargs):
        # Override if self.tournament_redirect_pattern_name is specified,
        # otherwise just pass down the chain
        if self.tournament_redirect_pattern_name:
            try:
                return reverse_tournament(self.tournament_redirect_pattern_name,
                        self.get_tournament(), args=args, kwargs=kwargs)
            except NoReverseMatch:
                pass
        return super().get_redirect_url(*args, **kwargs)


class RoundMixin(TournamentMixin):
    """Mixin for views that relate to a round, and are specified as relating
    to a round in the URL.

    Views using this mixin should have `tournament_slug` and `round_seq` groups
    in their URL's regular expression. They should then call `self.get_round()`
    to retrieve the round.

    This mixin includes `TournamentMixin`, so classes using `RoundMixin` do not
    need to explicitly inherit from both.
    """
    round_seq_url_kwarg = "round_seq"
    round_cache_key = "{slug}_{seq}_object"
    round_redirect_pattern_name = None

    def get_page_subtitle(self):
        return 'as of %s' % self.get_round().name

    def get_round(self):
        # First look in self,
        if hasattr(self, "_round_from_url"):
            return self._round_from_url

        # then look in cache,
        tournament = self.get_tournament()
        seq = self.kwargs[self.round_seq_url_kwarg]
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

    def get_redirect_url(self, *args, **kwargs):
        # Override if self.round_redirect_pattern_name is specified,
        # otherwise just pass down the chain
        if self.round_redirect_pattern_name:
            try:
                return reverse_round(self.round_redirect_pattern_name,
                        self.get_round(), args=args, kwargs=kwargs)
            except NoReverseMatch:
                pass
        return super().get_redirect_url(*args, **kwargs)


class PublicTournamentPageMixin(TournamentMixin):
    """Mixin for views that show public tournament pages that can be enabled and
    disabled by a tournament preference.

    Views using this mixin should set the `public_page_preference` class
    attribute to the name of the preference that controls whether the page is
    enabled.

    If a public user tries to access the page while it is disabled in the
    tournament options, they will be redirected to the public index page for
    that tournament, and shown a generic message that the page isn't enabled.
    The message can be overridden through the `disabled_message` class attribute
    or, if it needs to be generated dynamically, by overriding the
    `get_disabled_message()` method.
    """

    public_page_preference = None
    disabled_message = "That page isn't enabled for this tournament."

    def get_disabled_message(self):
        return self.disabled_message

    def dispatch(self, request, *args, **kwargs):
        tournament = self.get_tournament()
        if tournament is None:
            messages.info(self.request, "That tournament no longer exists")
            return redirect('tabbycat-index')
        if self.public_page_preference is None:
            raise ImproperlyConfigured("public_page_preference isn't set on this view.")
        if tournament.pref(self.public_page_preference):
            return super().dispatch(request, *args, **kwargs)
        else:
            logger.error("Tried to access a disabled public page")
            messages.error(self.request, self.get_disabled_message())
            return redirect_tournament('tournament-public-index', tournament)


class CrossTournamentPageMixin(PublicTournamentPageMixin):
    """Mixin for views that show pages with data drawn from multiple tournaments
    but are optionally viewed. They check the last available tournament object
    and check its preferences"""

    def get_round(self):
        return None  # Override Parent

    def get_tournament(self):
        tournament = Tournament.objects.order_by('id').last()
        return tournament

    def get_context_data(self, **kwargs):
        kwargs['tournament'] = self.get_tournament()
        return super().get_context_data(**kwargs)


class SingleObjectFromTournamentMixin(SingleObjectMixin, TournamentMixin):
    """Mixin for views that relate to a single object that is part of a
    tournament. Like SingleObjectMixin, but restricts searches to the relevant
    tournament."""

    allow_null_tournament = False
    tournament_field_name = 'tournament'

    def get_queryset(self):
        # Filter for this tournament; if self.allow_null_tournament is True,
        # then also allow objects with no tournament.
        q = Q(**{self.tournament_field_name: self.get_tournament()})
        if self.allow_null_tournament:
            q |= Q(**{self.tournament_field_name + "__isnull": True})
        return super().get_queryset().filter(q)


class SingleObjectByRandomisedUrlMixin(SingleObjectFromTournamentMixin):
    """Mixin for views that use URLs referencing objects by a randomised key.
    This is just a `SingleObjectFromTournamentMixin` with some options set.

    Views using this mixin should have both a `url_key` group in their URL's
    regular expression, and a primary key group (by default `pk`, inherited from
    `SingleObjectMixin`, but this can be overridden). They should set the
    `model` field of the class as they would for `SingleObjectMixin`. This model
    should have a slug field called `url_key`.
    """
    slug_field = 'url_key'
    slug_url_kwarg = 'url_key'
