import json
import logging

from asgiref.sync import async_to_sync
from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import NoReverseMatch, reverse
from django.utils.encoding import force_str
from django.utils.translation import gettext as _
from django.views.generic.base import ContextMixin
from django.views.generic.detail import SingleObjectMixin

from adjallocation.models import DebateAdjudicator
from breakqual.utils import calculate_live_thresholds
from draw.models import DebateTeam, MultipleDebateTeamsError, NoDebateTeamFoundError
from participants.models import Institution, Speaker
from participants.prefetch import populate_win_counts
from participants.serializers import InstitutionSerializer
from tournaments.serializers import RoundSerializer, TournamentSerializer
from utils.misc import (add_query_string_parameter, redirect_tournament,
                        reverse_round, reverse_tournament)
from utils.mixins import AssistantMixin, CacheMixin, TabbycatPageTitlesMixin
from utils.serializers import django_rest_json_render

from .models import Round, Tournament

logger = logging.getLogger(__name__)


# ==============================================================================
# Mixins providing access to tournament and round from URL
# ==============================================================================

class TournamentFromUrlMixin:
    """Provides the `tournament` property, looking in the cache and URL path,
    and keeping its own local cache.

    This mixin shouldn't generally be used directly; it should instead typically
    be inherited via `TournamentMixin` (for views) or `TournamentWebsocketMixin`
    (for websocket consumers).
    """
    tournament_slug_url_kwarg = "tournament_slug"
    tournament_cache_key = "{slug}_object"
    tournament_redirect_pattern_name = None

    def get_url_kwargs(self):
        return self.kwargs

    @property
    def tournament(self):
        # First look in self,
        if hasattr(self, "_tournament_from_url"):
            return self._tournament_from_url

        # then look in cache,
        slug = self.get_url_kwargs()[self.tournament_slug_url_kwarg]
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


class TournamentMixin(TabbycatPageTitlesMixin, TournamentFromUrlMixin):
    """Mixin for views that relate to a tournament, and are specified as
    relating to a tournament in the URL.

    Views using this mixin should have a `tournament_slug` group in their URL's
    regular expression. They should then call `self.tournament` to
    retrieve the tournament.
    """
    def get_redirect_url(self, *args, **kwargs):
        # Override if self.tournament_redirect_pattern_name is specified,
        # otherwise just pass down the chain
        if self.tournament_redirect_pattern_name:
            try:
                return reverse_tournament(self.tournament_redirect_pattern_name,
                        self.tournament, args=args, kwargs=kwargs)
            except NoReverseMatch:
                logger.warning("No reverse match for %s", self.tournament_redirect_pattern_name)
                pass

        return super().get_redirect_url(*args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        t = self.tournament

        if not getattr(settings, 'DISABLE_SENTRY', False):
            from sentry_sdk import set_context
            set_context("Tabbycat debug info", {
                "Tab director email": getattr(settings, 'TAB_DIRECTOR_EMAIL', "not provided"),
                "Tournament preferences": self.tournament.preferences.all(),
            })

        # Lack of current_round caused by creating a tournament without rounds
        if t.current_round is None:
            if hasattr(self.request, 'user') and self.request.user.is_superuser:
                messages.warning(request, _("You've been redirected to this "
                    "page because tournament %(tournament)s has no rounds. "
                    "Please create some before returning to the admin site.") %
                    {'tournament': t.name})
                admin_url = reverse('admin:tournaments_round_changelist')
                return redirect(admin_url)
            else:
                logger.warning("Current round wasn't set, redirecting to site index")
                messages.warning(request, _("There's a problem with the data "
                    "for the tournament %(tournament)s. Please contact a "
                    "tab director and ask them to investigate.") %
                    {'tournament': t.name})
                url = add_query_string_parameter(reverse('tabbycat-index'), 'redirect', 'false')
                return redirect(url)

        try:
            return super().dispatch(request, *args, **kwargs)
        except (MultipleDebateTeamsError, NoDebateTeamFoundError):
            if hasattr(self.request, 'user') and self.request.user.is_superuser:
                logger.warning("Debate team side assignment error, redirecting "
                               "to tournament-fix-debate-teams")
                messages.warning(request, _("You've been redirected to this "
                    "page because of a problem with how teams are assigned to "
                    "sides in a debate."))
                return redirect_tournament('tournament-fix-debate-teams', t)
            else:
                logger.warning("Debate team side assignment error, redirecting "
                               "to tournament-public-index")
                messages.warning(request, _("There's a problem with how teams "
                    "are assigned to sides in a debate. The tab director will "
                    "need to resolve this issue."))
                return redirect_tournament('tournament-public-index', t)


class TournamentWebsocketMixin(TournamentFromUrlMixin):
    """Mixin for websocket consumers that listen for changes relating to a
    particular tournament, as specified in the URL.

    Subclasses must provide a `group_prefix` that serves as a name for the
    stream; the name of the group is a concatenation of this and the tournament
    slug.
    """
    group_prefix = None

    def get_url_kwargs(self):
        return self.scope["url_route"]["kwargs"]

    def group_name(self):
        if self.group_prefix is None:
            raise ImproperlyConfigured("group_prefix must be specified on subclasses of TournamentWebsocketMixin")
        return self.group_prefix + '_' + self.tournament.slug

    def send_error(self, error, message, original_content):
        # Need to forcibly decode the string (for translations)
        self.send_json({
            'error': force_str(error),
            'message': force_str(message),
            'original_content': original_content,
            'component_id': original_content['component_id'],
        })
        return super()

    def connect(self):
        async_to_sync(self.channel_layer.group_add)(
            self.group_name(), self.channel_name,
        )
        super().connect()

    def disconnect(self, message):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name(), self.channel_name,
        )
        super().disconnect(message)


class RoundFromUrlMixin(TournamentFromUrlMixin):
    """Provides the `round` property, looking in the cache and URL path,
    and keeping its own local cache.

    This mixin shouldn't generally be used directly; it should instead typically
    be inherited via `RoundMixin` (for views) or `RoundWebsocketMixin` (for
    websocket consumers).
    """
    round_seq_url_kwarg = "round_seq"
    round_cache_key = "{slug}_{seq}_object"
    round_redirect_pattern_name = None

    @property
    def round(self):
        # First look in self,
        if hasattr(self, "_round_from_url"):
            return self._round_from_url

        # then look in cache,
        seq = self.get_url_kwargs()[self.round_seq_url_kwarg]
        key = self.round_cache_key.format(slug=self.tournament.slug, seq=seq)
        cached_round = cache.get(key)
        if cached_round:
            self._round_from_url = cached_round
            return cached_round

        # and if it was in neither place, retrieve the object
        round = get_object_or_404(Round, tournament=self.tournament, seq=seq)
        cache.set(key, round, None)
        self._round_from_url = round
        return round


class RoundMixin(RoundFromUrlMixin, TournamentMixin):
    """Mixin for views that relate to a round, and are specified as relating
    to a round in the URL.

    Views using this mixin should have `tournament_slug` and `round_seq` groups
    in their URL's regular expression. They should then call `self.round`
    to retrieve the round.

    This mixin includes `TournamentMixin`, so classes using `RoundMixin` do not
    need to explicitly inherit from both.
    """

    def get_page_subtitle(self):
        if not getattr(self, "page_subtitle") and not getattr(self, "use_template_subtitle", False) \
                and self.round is not None:
            return _("for %(round)s") % {'round': self.round.name}
        else:
            return super().get_page_subtitle()

    def get_redirect_url(self, *args, **kwargs):
        # Override if self.round_redirect_pattern_name is specified,
        # otherwise just pass down the chain
        if self.round_redirect_pattern_name:
            try:
                return reverse_round(self.round_redirect_pattern_name,
                                     self.round, args=args, kwargs=kwargs)
            except NoReverseMatch:
                pass
        return super().get_redirect_url(*args, **kwargs)


class RoundWebsocketMixin(RoundFromUrlMixin, TournamentWebsocketMixin):
    """Mixin for websocket consumers that listen for changes relating to a
    particular round, as specified in the URL.

    Subclasses must provide a `group_prefix` that serves as a name for the
    stream; the name of the group is a concatenation of this, the tournament
    slug and the round sequence number.

    This mixin includes `TournamentWebsocketMixin`, so classes using it do not
    need to explicitly inherit from both.
    """
    def group_name(self):
        tournament_path = super().group_name()
        return tournament_path + '_' + str(self.round.seq)


class CurrentRoundMixin(RoundMixin, ContextMixin):
    """Mixin for views that relate to the current round (without URL reference)."""

    @property
    def round(self):
        # Override the round-grabbing mechanism of RoundMixin
        return self.tournament.current_round

    def get_context_data(self, **kwargs):
        # Middleware won't find this in the URL, so add it ourselves
        kwargs['round'] = self.round
        return super().get_context_data(**kwargs)


# ==============================================================================
# Mixins regulating public and assistant tournament views
# ==============================================================================

class TournamentAccessControlledPageMixin(TournamentMixin):
    """Base mixin for views that can be enabled and disabled by a tournament
    preference."""

    def is_page_enabled(self, tournament):
        raise NotImplementedError

    def render_page_disabled_error_page(self):
        return TemplateResponse(
            request=self.request,
            template=self.template_403_name,
            context={'user_role': self._user_role},
            status=403,
        )

    def dispatch(self, request, *args, **kwargs):
        tournament = self.tournament
        if self.is_page_enabled(tournament):
            return super().dispatch(request, *args, **kwargs)
        else:
            logger.warning("Tried to access a disabled %s page" % (self._user_role,))
            return self.render_page_disabled_error_page()


class PersonalizablePublicTournamentPageMixin(TournamentAccessControlledPageMixin):
    """Mixin for views that show personalizable public tournament pages which may be
    enabled for disabled by tournament preferences. Caching is inappropriate for these
    pages."""

    public_page_preference = None
    template_403_name = "errors/public_403.html"
    _user_role = "public"

    def is_page_enabled(self, tournament):
        if self.public_page_preference is None:
            raise ImproperlyConfigured("public_page_preference isn't set on this view.")
        return tournament.pref(self.public_page_preference)


class PublicTournamentPageMixin(PersonalizablePublicTournamentPageMixin, CacheMixin):
    """Mixin for views that show non-personalized public tournament pages that can
    be enabled and disabled by a tournament preference.

    Views using this mixin should set the `public_page_preference` class
    attribute to the name of the preference that controls whether the page is
    enabled.

    If someone tries to access the page while it is disabled in the tournament
    options, they will be redirected to the public index page for that
    tournament, and shown a generic message that the page isn't enabled. The
    message can be overridden through the `disabled_message` class attribute or,
    if it needs to be generated dynamically, by overriding the
    `get_disabled_message()` method.
    """

    pass


class OptionalAssistantTournamentPageMixin(AssistantMixin, TournamentAccessControlledPageMixin):
    """Mixin for pages that are intended for assistants, but can be enabled and
    disabled by a tournament preference. This preference sets of access tiers;
    if the page requires a certain tier to access it then only superusers can
    view it.

    Views using the mixins should set the `assistant_page_permissions` class to
    match one or more of the values defined in the AssistantAccess preference's
    available choices.

    If an anonymous user tries to access this page, they will be redirected to
    the login page. If an assistant user tries to access this page while
    assistant access is disabled, they will be shown an error message explaining
    that the page is disabled."""

    assistant_page_permissions = None
    template_403_name = "errors/assistant_403.html"
    _user_role = "assistant"

    def is_page_enabled(self, tournament):
        if tournament is None:
            return False
        if self.assistant_page_permissions is None:
            raise ImproperlyConfigured("assistant_page_permissions isn't set on this view.")
        return tournament.pref('assistant_access') in self.assistant_page_permissions


# ==============================================================================
# Mixins extending SingleObjectMixin for tournaments
# ==============================================================================

class SingleObjectFromTournamentMixin(SingleObjectMixin, TournamentMixin):
    """Mixin for views that relate to a single object that is part of a
    tournament. Like SingleObjectMixin, but restricts searches to the relevant
    tournament."""

    allow_null_tournament = False
    tournament_field_name = 'tournament'

    def get_queryset(self):
        # Filter for this tournament; if self.allow_null_tournament is True,
        # then also allow objects with no tournament.
        q = Q(**{self.tournament_field_name: self.tournament})
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

    def get_context_data(self, **kwargs):
        kwargs['private_url'] = True
        return super().get_context_data(**kwargs)


# ==============================================================================
# Drag-and-drop mixins
# ==============================================================================

class DragAndDropMixin(RoundMixin):

    def get_extra_info(self):
        """ Unlike meta_info everything under extra info is json serialised
        automatically. Designed for simple key/value pairs"""
        extra_info = {} # Set by view for top bar toggles
        extra_info['codeNames'] = self.tournament.pref('team_code_names')
        extra_info['highlights'] = {}

        bcs = self.tournament.breakcategory_set.all()
        serialised_bcs = []
        for bc in bcs:
            safe, dead = calculate_live_thresholds(bc, self.tournament, self.round)
            serialised_bc = {
                'pk': bc.id,
                'fields': {'name': bc.name, 'safe': safe, 'dead': dead},
            }
            serialised_bcs.append(serialised_bc)

        extra_info['highlights']['break'] = serialised_bcs

        extra_info['backUrl'] = reverse_round('draw', self.round)
        extra_info['backLabel'] = _("Return to Draw")
        return extra_info

    def get_meta_info(self):
        """ Data universal to all allocation views; these are accessed
        directly from the template so only the value & not the key are JSON. """
        serialized_round = RoundSerializer(self.round)
        serialized_tournament = TournamentSerializer(self.tournament)
        return {
            'round': self.json_render(serialized_round.data),
            'tournament': self.json_render(serialized_tournament.data),
            'extra': json.dumps(self.get_extra_info()),
        }

    def json_render(self, data):
        # For some reason JSONRenderer produces byte strings
        return django_rest_json_render(data)

    def get_serialised_institutions(self):
        institutions = Institution.objects.all()
        serialized_institutions = InstitutionSerializer(institutions, many=True)
        return self.json_render(serialized_institutions.data)

    def get_serialised_debates_or_panels(self):
        draw = self.get_draw_or_panels_objects()
        serialized_draw = self.debates_or_panels_factory(draw)
        return self.json_render(serialized_draw.data)

    def get_context_data(self, **kwargs):
        kwargs['vueDebatesOrPanels'] = self.get_serialised_debates_or_panels()
        kwargs['vueAllocatableItems'] = self.get_serialised_allocatable_items()
        kwargs['vueInstitutions'] = self.get_serialised_institutions()
        kwargs['vueMetaInfo'] = self.get_meta_info()
        return super().get_context_data(**kwargs)


class DebateDragAndDropMixin(DragAndDropMixin):
    prefetch_adjs = True
    prefetch_teams = True
    prefetch_venues = True

    def get_draw_or_panels_objects(self):
        selects = ('round__tournament', 'venue')
        prefetches = ()
        if self.prefetch_venues:
            prefetches += ('venue__venuecategory_set',)
        if self.prefetch_adjs:
            prefetches += (Prefetch('debateadjudicator_set',
                queryset=DebateAdjudicator.objects.select_related('adjudicator')),)
        if self.prefetch_teams:
            prefetches += (Prefetch('debateteam_set',
                queryset=DebateTeam.objects.select_related('team').prefetch_related(
                    Prefetch('team__speaker_set', queryset=Speaker.objects.order_by('name')),
                    'team__break_categories',
                )),
            )
        else:
            prefetches += (Prefetch('debateteam_set',
                queryset=DebateTeam.objects.select_related('team').prefetch_related(
                    'team__break_categories',
                )),
            )

        draw = self.round.debate_set.select_related(*selects).prefetch_related(*prefetches)

        if self.prefetch_teams:
            populate_win_counts([dt.team for debate in draw for dt in debate.debateteam_set.all()])
        return draw
