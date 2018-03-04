import json
import logging
from urllib.parse import urlparse, urlunparse

from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.urls import NoReverseMatch
from django.contrib import messages
from django.db.models import Prefetch, Q
from django.http import HttpResponseRedirect, QueryDict
from django.shortcuts import get_object_or_404, reverse
from django.template.response import TemplateResponse
from django.utils.functional import cached_property
from django.utils.translation import gettext as _
from django.views.generic.base import ContextMixin
from django.views.generic.detail import SingleObjectMixin

from adjallocation.models import DebateAdjudicator
from breakqual.utils import calculate_live_thresholds, determine_liveness
from draw.models import DebateTeam, MultipleDebateTeamsError, NoDebateTeamFoundError
from participants.models import Region, Speaker
from participants.prefetch import populate_feedback_scores, populate_win_counts

from utils.misc import redirect_tournament, reverse_round, reverse_tournament
from utils.mixins import AssistantMixin, TabbycatPageTitlesMixin


from .models import Round, Tournament

logger = logging.getLogger(__name__)


def add_query_parameter(url, name, value):
    parts = list(urlparse(url))
    query = QueryDict(parts[4], mutable=True)
    query[name] = value
    parts[4] = query.urlencode(parts)
    return urlunparse(parts)


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
                logger.warning("No Reverse Match for given tournament_slug_url_kwarg")
                pass

        return super().get_redirect_url(*args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        tournament = self.get_tournament()
        if tournament.current_round_id is None:
            full_path = self.request.get_full_path()
            if hasattr(self.request, 'user') and self.request.user.is_superuser:
                logger.warning("Current round wasn't set, redirecting to set-current-round page")
                set_current_round_url = reverse_tournament('tournament-set-current-round', self.get_tournament())
                redirect_url = add_query_parameter(set_current_round_url, 'next', full_path)
                return HttpResponseRedirect(redirect_url)
            else:
                logger.warning("Current round wasn't set, redirecting to site index")
                messages.warning(request, _("There's a problem with the data for the tournament "
                    "%(tournament_name)s. Please contact a tab director and ask them to set its "
                    "current round.") % {'tournament_name': tournament.name})
                home_url = reverse('tabbycat-index')
                redirect_url = add_query_parameter(home_url, 'redirect', 'false')
                return HttpResponseRedirect(redirect_url)

        try:
            return super().dispatch(request, *args, **kwargs)
        except (MultipleDebateTeamsError, NoDebateTeamFoundError) as e:
            if hasattr(self.request, 'user') and self.request.user.is_superuser:
                logger.warning("Debate team side assignment error, redirecting to tournament-fix-debate-teams")
                messages.warning(request, _("You've been redirected to this page because of a problem with "
                        "how teams are assigned to sides in a debate."))
                return redirect_tournament('tournament-fix-debate-teams', tournament)
            else:
                logger.warning("Debate team side assignment error, redirecting to tournament-public-index")
                messages.warning(request, _("There's a problem with how teams are assigned to sides "
                        "in a debate. The tab director will need to resolve this issue."))
                return redirect_tournament('tournament-public-index', tournament)


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
        if not getattr(self, "page_subtitle") and not getattr(self, "use_template_subtitle", False) \
                and self.get_round() is not None:
            return _("for %(round)s") % {'round': self.get_round().name}
        else:
            return super().get_page_subtitle()

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


class CurrentRoundMixin(RoundMixin, ContextMixin):
    """Mixin for views that relate to the current round (without URL reference)."""

    def get_round(self):
        # Override the round-grabbing mechanism of RoundMixin
        return self.get_tournament().current_round

    def get_context_data(self, **kwargs):
        # Middleware won't find this in the URL, so add it ourselves
        kwargs['round'] = self.get_round()
        return super().get_context_data(**kwargs)


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
            status=403
        )

    def dispatch(self, request, *args, **kwargs):
        tournament = self.get_tournament()
        if self.is_page_enabled(tournament):
            return super().dispatch(request, *args, **kwargs)
        else:
            logger.warning("Tried to access a disabled %s page" % (self._user_role,))
            return self.render_page_disabled_error_page()


class PublicTournamentPageMixin(TournamentAccessControlledPageMixin):
    """Mixin for views that show public tournament pages that can be enabled and
    disabled by a tournament preference.

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

    public_page_preference = None
    template_403_name = "errors/public_403.html"
    _user_role = "public"

    def is_page_enabled(self, tournament):
        if self.public_page_preference is None:
            raise ImproperlyConfigured("public_page_preference isn't set on this view.")
        return tournament.pref(self.public_page_preference)


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


class CrossTournamentPageMixin(PublicTournamentPageMixin):
    """Mixin for views that show pages with data drawn from multiple tournaments
    but are optionally viewed. They check the last available tournament object
    and check its preferences"""
    cross_tournament = True

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


class DrawForDragAndDropMixin(RoundMixin):
    """Provides the base set of constructors used to assemble a the
    drag and drop table used for editing matchups/adjs/venues with a
    drag and drop interface. Subclass annotate method to add extra view data """

    def annotate_break_classes(self, serialised_team, thresholds):
        """We can't style break categories in CSS because we need a defined range;
        this normalises IDs of the break categories so the CSS classes can work"""
        if serialised_team['break_categories']:
            breaks_seq = {}
            for i, r in enumerate(self.break_categories):
                breaks_seq[r.id] = i
            for bc in serialised_team['break_categories']:
                bc['class'] = breaks_seq[bc['id']]
                points = serialised_team['points']
                bc['will_break'] = determine_liveness(thresholds[bc['id']], points)

        return serialised_team

    def annotate_region_classes(self, adj_or_team):
        """Same as above, but for regions"""
        regions_seq = {}
        for i, r in enumerate(self.regions):
            regions_seq[r.id] = i
        if adj_or_team['region']:
            adj_or_team['region']['class'] = regions_seq[adj_or_team['region']['id']]

        return adj_or_team

    @cached_property
    def break_categories(self):
        return self.get_tournament().breakcategory_set.order_by('-is_general', 'name')

    @cached_property
    def break_thresholds(self):
        t = self.get_tournament()
        r = self.get_round()
        return {bc.id: calculate_live_thresholds(bc, t, r) for bc in self.break_categories}

    @cached_property
    def regions(self):
        return Region.objects.order_by('id')

    def annotate_draw(self, draw, serialised_draw):
        # Need to unique-ify/reorder break categories/regions for consistent CSS
        for debate in serialised_draw:
            break_thresholds = self.break_thresholds
            liveness = 0
            for dt in debate['debateTeams']:
                team = dt['team']
                if not team:
                    continue
                team = self.annotate_break_classes(team, break_thresholds)
                team = self.annotate_region_classes(team)
                if team['break_categories'] is not None:
                    for c in team['break_categories']:
                        if c['will_break'] == 'live' or c['will_break'] == '?':
                            liveness += 1

            for da in debate['debateAdjudicators']:
                da['adjudicator'] = self.annotate_region_classes(da['adjudicator'])

            debate['liveness'] = liveness

        return serialised_draw

    def annotate_round_info(self, round_info):
        return round_info

    def get_draw(self):
        round = self.get_round()

        # The use-case for prefetches here is so intense that we'll just implement
        # a separate one (as opposed to use Round.debate_set_with_prefetches())
        draw = round.debate_set.select_related('round__tournament').prefetch_related(
            Prefetch('debateadjudicator_set',
                queryset=DebateAdjudicator.objects.select_related('adjudicator__institution__region')),
            Prefetch('debateteam_set',
                queryset=DebateTeam.objects.select_related(
                    'team__institution__region'
                ).prefetch_related(
                    Prefetch('team__speaker_set', queryset=Speaker.objects.order_by('name')),
                )),
            'debateteam_set__team__break_categories',
        )
        populate_win_counts([dt.team for debate in draw for dt in debate.debateteam_set.all()])
        populate_feedback_scores([da.adjudicator for debate in draw for da in debate.debateadjudicator_set.all()])

        serialised_draw = [d.serialize() for d in draw]
        draw = self.annotate_draw(draw, serialised_draw)
        return json.dumps(serialised_draw)

    def get_round_info(self):
        round = self.get_round()
        t = self.get_tournament()
        adjudicator_positions = ["C"]
        if not t.pref('no_panellist_position'):
            adjudicator_positions += "P"
        if not t.pref('no_trainee_position'):
            adjudicator_positions += "T"

        round_info = {
            'adjudicatorPositions': adjudicator_positions, # Depends on prefs
            'adjudicatorDoubling': t.pref('duplicate_adjs'),
            'teamsInDebate': t.pref('teams_in_debate'),
            'teamPositions': t.sides,
            'backUrl': reverse_round('draw', round),
            'autoUrl': reverse_round(self.auto_url, round) if hasattr(self, 'auto_url') else None,
            'saveUrl': reverse_round(self.save_url, round) if hasattr(self, 'save_url') else None,
            'roundName' : round.abbreviation,
            'roundSeq' : round.seq,
            'roundIsPrelim' : not round.is_break_round,
        }
        round_info = self.annotate_round_info(round_info)
        return json.dumps(round_info)

    def get_context_data(self, **kwargs):
        kwargs['vueDebates'] = self.get_draw()
        kwargs['vueRoundInfo'] = self.get_round_info()
        return super().get_context_data(**kwargs)
