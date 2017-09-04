import json
import logging
from urllib.parse import urlparse, urlunparse

from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import NoReverseMatch
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q
from django.http import HttpResponseRedirect, QueryDict
from django.shortcuts import get_object_or_404, redirect, reverse
from django.utils.functional import cached_property
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from django.views.generic.detail import SingleObjectMixin

from actionlog.mixins import LogActionMixin
from breakqual.utils import calculate_live_thresholds, determine_liveness
from draw.models import Debate, MultipleDebateTeamsError, NoDebateTeamFoundError
from participants.models import Region

from utils.misc import redirect_tournament, reverse_round, reverse_tournament
from utils.mixins import JsonDataResponsePostView, SuperuserRequiredMixin, TabbycatPageTitlesMixin


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
                pass
        return super().get_redirect_url(*args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        tournament = self.get_tournament()
        if tournament.current_round_id is None:
            full_path = self.request.get_full_path()
            if hasattr(self.request, 'user') and self.request.user.is_authenticated:
                logger.error("Current round wasn't set, redirecting to set-current-round page, was looking for %s" % full_path)
                set_current_round_url = reverse_tournament('tournament-set-current-round', self.get_tournament())
                redirect_url = add_query_parameter(set_current_round_url, 'next', full_path)
                return HttpResponseRedirect(redirect_url)
            else:
                logger.error("Current round wasn't set, redirecting to site index, was looking for %s" % full_path)
                messages.error(request, _("There's a problem with the data for the tournament "
                    "%(tournament_name)s. Please contact a tab director and ask them to set its "
                    "current round.") % {'tournament_name': tournament.name})
                home_url = reverse('tabbycat-index')
                redirect_url = add_query_parameter(home_url, 'redirect', 'false')
                return HttpResponseRedirect(redirect_url)

        try:
            return super().dispatch(request, *args, **kwargs)
        except (MultipleDebateTeamsError, NoDebateTeamFoundError) as e:
            if hasattr(self.request, 'user') and self.request.user.is_superuser:
                logger.exception("Debate team side assignment error, redirecting to admin:draw_debate_changelist")
                messages.warning(request, _("Teams don't appear to be correctly assigned to sides "
                        "in a debate. Please resolve this problem before continuing: "
                        "%(error)s") % {'error': e})
                return redirect('admin:draw_debate_changelist')
            else:
                logger.exception("Debate team side assignment error, redirecting to tournament-public-index")
                messages.error(request, _("There's a problem with how teams are assigned to sides "
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
        if not getattr(self, "page_subtitle") and not getattr(self, "use_template_subtitle", False):
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


class PublicTournamentPageMixin(TournamentMixin):
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
    disabled_message = ugettext_lazy("That page isn't enabled for this tournament.")

    def get_disabled_message(self):
        return self.disabled_message

    def dispatch(self, request, *args, **kwargs):
        tournament = self.get_tournament()
        if tournament is None:
            messages.info(self.request, _("That tournament no longer exists."))
            return redirect('tabbycat-index')
        if self.public_page_preference is None:
            raise ImproperlyConfigured("public_page_preference isn't set on this view.")
        if tournament.pref(self.public_page_preference):
            return super().dispatch(request, *args, **kwargs)
        else:
            logger.warning("Tried to access a disabled public page")
            messages.error(self.request, self.get_disabled_message())
            return redirect_tournament('tournament-public-index', tournament)


class OptionalAssistantTournamentPageMixin(TournamentMixin, UserPassesTestMixin):
    """Mixin for pages that are intended for assistants, but can be enabled and
    disabled by a tournament preference. This preference sets of access tiers;
    if the page requires a certain tier to acess it then only superusers can
    view it.

    Views using the mixins should set the `assistant_page_permissions` class to
    match one or more of the values defined in the AssistantAccess preference's
    available choices.

    If an anonymous user tries to access this page, they will be redirected to
    the login page. If an assistant user tries to access this page while
    assistant access is disabled, they will be redirected to the login page."""

    assistant_page_permissions = None

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        if not self.request.user.is_authenticated:
            return False

        # if we got this far, it's an assistant user
        tournament = self.get_tournament()
        if tournament is None:
            return False
        if self.assistant_page_permissions is None:
            raise ImproperlyConfigured("assistant_page_permissions isn't set on this view.")
        if tournament.pref('assistant_access') in self.assistant_page_permissions:
            return True
        else:
            return False


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
                wins = serialised_team['wins']
                bc['will_break'] = determine_liveness(thresholds[bc['id']], wins)

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
                    liveness += len([bc for bc in team['break_categories']
                                     if bc['will_break'] == 'live'])
            for da in debate['debateAdjudicators']:
                da['adjudicator'] = self.annotate_region_classes(da['adjudicator'])

            debate['liveness'] = liveness

        return serialised_draw

    def annotate_round_info(self, round_info):
        return round_info

    def get_draw(self):
        round = self.get_round()
        draw = round.debate_set_with_prefetches(ordering=('-importance', 'room_rank',),
                                                speakers=True, divisions=False,
                                                institutions=True, wins=True)
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
            'backUrl': reverse_round('draw', round),
            'autoUrl': reverse_round(self.auto_url, round) if hasattr(self, 'auto_url') else None,
            'saveUrl': reverse_round(self.save_url, round) if hasattr(self, 'save_url') else None,
            'roundName' : round.abbreviation,
            'roundIsPrelim' : not round.is_break_round,
        }
        round_info = self.annotate_round_info(round_info)
        return json.dumps(round_info)

    def get_context_data(self, **kwargs):
        kwargs['vueDebates'] = self.get_draw()
        kwargs['vueRoundInfo'] = self.get_round_info()
        return super().get_context_data(**kwargs)


class SaveDragAndDropDebateMixin(JsonDataResponsePostView, SuperuserRequiredMixin, RoundMixin, LogActionMixin):
    """For AJAX issued updates which post a Debate dictionary; which is then
    modified and return back via a JSON response"""
    allows_creation = False

    def modify_debate(self):
        # Children must modify the debate object and return it
        raise NotImplementedError

    def get_debate(self, id):
        if Debate.objects.filter(pk=id).exists():
            debate = Debate.objects.get(pk=id)
            return debate
        elif self.allow_creation:
            print('Creating debate')
            debate = Debate.objects.create(round=self.get_round())
            debate.save()
            return debate
        else:
            raise ValueError('SaveDragAndDropDebateMixin posted a debate ID that doesnt exist')

    def post_data(self):
        body = self.request.body.decode('utf-8')
        posted_debate = json.loads(body)
        debate = self.get_debate(posted_debate['id'])
        debate = self.modify_debate(debate, posted_debate)
        self.log_action()
        return json.dumps(debate.serialize())
