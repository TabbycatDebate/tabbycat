import logging

from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.contrib import messages
from django.shortcuts import get_object_or_404

from utils.misc import redirect_tournament

from .models import Round, Tournament

logger = logging.getLogger(__name__)


class TabbycatBaseMixin:
    """Allows all views to set header information in their subclassess obviating
    the need for page template boilerplate and/or page specific templates"""

    page_title = ''
    page_subtitle = ''
    page_emoji = ''

    def get_page_title(self):
        return self.page_title

    def get_page_emoji(self):
        return self.page_emoji

    def get_page_subtitle(self):
        return self.page_subtitle

    def get_context_data(self, **kwargs):
        kwargs["page_title"] = self.get_page_title()
        kwargs["page_subtitle"] = self.get_page_subtitle()
        kwargs["page_emoji"] = self.get_page_emoji()

        return super().get_context_data(**kwargs)


class TournamentMixin(TabbycatBaseMixin):
    """Mixin for views that relate to a tournament, and are specified as
    relating to a tournament in the URL.

    Views using this mixin should have a `tournament_slug` group in their URL's
    regular expression. They should then call `self.get_tournament()` to
    retrieve the tournament.
    """
    tournament_slug_url_kwarg = "tournament_slug"
    tournament_cache_key = "{slug}_object"

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
        if self.public_page_preference is None:
            raise ImproperlyConfigured("public_page_preference isn't set on this view.")
        if tournament.pref(self.public_page_preference):
            return super().dispatch(request, *args, **kwargs)
        else:
            logger.error("Tried to access a disabled public page")
            messages.error(self.request, self.get_disabled_message())
            return redirect_tournament('tournament-public-index', tournament)
