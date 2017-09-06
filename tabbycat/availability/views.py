import json
import logging

from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.views.generic.base import TemplateView, View
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy

from . import utils

from availability.models import RoundAvailability
from actionlog.mixins import LogActionMixin
from draw.generator.utils import partial_break_round_split
from draw.models import Debate
from participants.models import Adjudicator, Team
from actionlog.models import ActionLogEntry
from tournaments.mixins import RoundMixin
from utils.tables import TabbycatTableBuilder
from utils.mixins import PostOnlyRedirectView, SuperuserRequiredMixin, VueTableTemplateView
from utils.misc import reverse_round
from venues.models import Venue

logger = logging.getLogger(__name__)


# These need to be entire strings, for translations
CHECK_IN_TITLES = {
    Team: ugettext_lazy("Teams"),
    Adjudicator: ugettext_lazy("Adjudicators"),
    Venue: ugettext_lazy("Venues"),
}


class AvailabilityIndexView(RoundMixin, SuperuserRequiredMixin, TemplateView):
    template_name = 'availability_index.html'
    page_title = ugettext_lazy("Check-Ins")
    page_emoji = '📍'

    def get_context_data(self, **kwargs):
        r = self.get_round()
        tournament = self.get_tournament()

        if r.prev:
            kwargs['previous_unconfirmed'] = r.prev.debate_set.filter(
                result_status__in=[Debate.STATUS_NONE, Debate.STATUS_DRAFT]).count()

        if r.is_break_round:
            teams = self._get_breaking_teams_dict()
        else:
            teams = self._get_dict(tournament.team_set)

        # Basic check before enable the button to advance
        adjs = self._get_dict(tournament.relevant_adjudicators)
        venues = self._get_dict(tournament.relevant_venues)
        kwargs['can_advance'] = teams['in_now'] > 1 and adjs['in_now'] > 0 and venues['in_now'] > 0
        kwargs['checkin_types'] = [teams, adjs, venues]

        # Check the number of teams/adjudicators is sufficient
        if tournament.pref('teams_in_debate') == 'two':
            per_room_divisor = 2
        else:
            per_room_divisor = 4
        kwargs['min_adjudicators'] = teams['in_now'] // per_room_divisor
        kwargs['min_venues'] = teams['in_now'] // per_room_divisor

        kwargs['error_type'] = getattr(self, 'error_type', None)
        return super().get_context_data(**kwargs)

    def _get_breaking_teams_dict(self):
        r = self.get_round()
        if r.draw_type is r.DRAW_FIRSTBREAK:
            break_size = r.break_category.breakingteam_set_competing.count()
            teams_dict = {'title': CHECK_IN_TITLES[Team], 'total': break_size}
            if break_size < 2:
                teams_dict['in_now'] = 0
                teams_dict['message'] = "%d breaking team%s — no debates can happen" % (break_size, "" if break_size == 1 else "s")
            else:
                debates, bypassing = partial_break_round_split(break_size)
                teams_dict['in_now'] = 2 * debates
                teams_dict['message'] = "%s breaking teams are debating this round; %s team%s bypassing" % (
                    2 * debates, bypassing, " is" if bypassing == 1 else "s are")
            return teams_dict

        elif r.draw_type is r.DRAW_BREAK:
            if r.prev is None:
                self.error_type = 'no_last_round'
                advancing_teams = 0
            else:
                advancing_teams = r.prev.debate_set.count()

            return {
                'title'     : CHECK_IN_TITLES[Team],
                'total'     : advancing_teams,
                'in_now'    : advancing_teams,
                'message'   : '%s advancing teams are debating this round' % advancing_teams
            }

        else: # this should never happen, but it did once...
            self.error_type = 'bad_draw_type_for_break_round'
            return {
                'title'  : CHECK_IN_TITLES[Team],
                'total'  : 0,
                'in_now' : 0,
                'message': "status unclear — see message above"
            }

    def _get_dict(self, queryset_all):
        contenttype = ContentType.objects.get_for_model(queryset_all.model)
        availability_queryset = RoundAvailability.objects.filter(content_type=contenttype)
        round = self.get_round()
        result = {
            'title': CHECK_IN_TITLES[queryset_all.model],
            'total': queryset_all.count(),
            'in_now': availability_queryset.filter(round=round).count(),
        }
        if round.prev:
            result['in_before'] = availability_queryset.filter(round=round.prev).count()
        else:
            result['in_before'] = None
        return result


# ==============================================================================
# Specific Activation Pages
# ==============================================================================

class AvailabilityTypeBase(RoundMixin, SuperuserRequiredMixin, VueTableTemplateView):
    template_name = "base_availability.html"

    def get_page_title(self):
        return CHECK_IN_TITLES[self.model] + " Availability"

    def get_context_data(self, **kwargs):
        kwargs['model'] = self.model._meta.label  # does not get translated
        kwargs['saveURL'] = reverse_round(self.update_view, self.get_round())
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        return self.model.objects.filter(tournament=self.get_tournament())

    def get_table(self):
        round = self.get_round()
        table = TabbycatTableBuilder(view=self, sort_key=self.sort_key)
        queryset = utils.annotate_availability(self.get_queryset(), round)

        table.add_column(_("Active Now"), [{
                'component': 'availability-check-cell',
                'available': inst.available,
                'sort': inst.available,
                'id': inst.id,
                'prev': inst.prev_available if round.prev else False,
            } for inst in queryset])

        if round.prev:
            table.add_column(_("Active in %(prev_round)s") % {'prev_round': round.prev.abbreviation}, [{
                    'sort': inst.prev_available,
                    'icon': 'check' if inst.prev_available else ''
                } for inst in queryset])

        self.add_description_columns(table, queryset)
        return table


class AvailabilityTypeTeamView(AvailabilityTypeBase):
    page_emoji = '👂'
    model = Team
    sort_key = 'team'
    update_view = 'availability-update-teams'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('speaker_set')

    @staticmethod
    def add_description_columns(table, teams):
        table.add_team_columns(teams)


class AvailabilityTypeAdjudicatorView(AvailabilityTypeBase):
    page_emoji = '👂'
    model = Adjudicator
    sort_key = 'name'
    update_view = 'availability-update-adjudicators'

    @staticmethod
    def add_description_columns(table, adjudicators):
        table.add_adjudicator_columns(adjudicators)


class AvailabilityTypeVenueView(AvailabilityTypeBase):
    page_emoji = '🎪'
    model = Venue
    sort_key = 'venue'
    update_view = 'availability-update-venues'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('venuecategory_set')

    @staticmethod
    def add_description_columns(table, venues):
        for v in venues:
            v.cats = ", ".join([vc.name for vc in v.venuecategory_set.all()])

        table.add_column(_("Venue"), [v.name for v in venues])
        table.add_column(_("Display Name (for the draw)"), [v.display_name for v in venues])
        table.add_column(_("Categories"), [v.cats for v in venues])
        table.add_column(_("Priority"), [v.priority for v in venues])


# ==============================================================================
# Bulk Activations
# ==============================================================================

class BaseBulkActivationView(RoundMixin, SuperuserRequiredMixin, PostOnlyRedirectView):

    round_redirect_pattern_name = 'availability-index'

    def post(self, request, *args, **kwargs):
        self.activate_function()
        messages.success(self.request, self.activation_msg)
        return super().post(request, *args, **kwargs)


class CheckInAllInRoundView(BaseBulkActivationView):
    activation_msg = ugettext_lazy("Checked in all teams, adjudicators and venues.")

    def activate_function(self):
        utils.activate_all(self.get_round())


class CheckInAllBreakingAdjudicatorsView(BaseBulkActivationView):
    activation_msg = ugettext_lazy("Checked in all breaking adjudicators.")

    def activate_function(self):
        utils.set_availability(self.get_tournament().relevant_adjudicators.filter(breaking=True),
                self.get_round())


class CheckInAllFromPreviousRoundView(BaseBulkActivationView):
    activation_msg = ugettext_lazy("Checked in all teams, adjudicators and venues from previous round.")

    def activate_function(self):
        t = self.get_tournament()
        round = self.get_round()
        items = [(Team, t.team_set), (Adjudicator, t.relevant_adjudicators), (Venue, t.relevant_venues)]

        for model, relevant_instances in items:
            contenttype = ContentType.objects.get_for_model(model)
            previous_ids = set(a['object_id'] for a in
                RoundAvailability.objects.filter(content_type=contenttype, round=round.prev).values('object_id'))
            logger.debug("Previous IDs for %s: %s", model._meta.verbose_name_plural, previous_ids)
            relevant_ids = set(x['id'] for x in relevant_instances.values('id'))
            logger.debug("Relevant IDs for %s: %s", model._meta.verbose_name_plural, relevant_ids)
            previous_relevant_ids = previous_ids & relevant_ids
            logger.debug("Checking in %s: %s", model._meta.verbose_name_plural, previous_relevant_ids)
            utils.set_availability_by_id(model, previous_relevant_ids, round)


# ==============================================================================
# Specific Activation Actions
# ==============================================================================

class BaseAvailabilityUpdateView(RoundMixin, SuperuserRequiredMixin, LogActionMixin, View):

    def post(self, request, *args, **kwargs):

        body = self.request.body.decode('utf-8')
        posted_info = json.loads(body)

        try:
            utils.set_availability_by_id(self.model, posted_info, self.get_round())
            self.log_action()

        except:
            message = "Error handling availability updates"
            logger.exception(message)
            return JsonResponse({'status': 'false', 'message': message}, status=500)

        return JsonResponse(json.dumps(True), safe=False)


class UpdateAdjudicatorsAvailabilityView(BaseAvailabilityUpdateView):
    action_log_type = ActionLogEntry.ACTION_TYPE_AVAIL_ADJUDICATORS_SAVE
    model = Adjudicator


class UpdateTeamsAvailabilityView(BaseAvailabilityUpdateView):
    action_log_type = ActionLogEntry.ACTION_TYPE_AVAIL_TEAMS_SAVE
    model = Team


class UpdateVenuesAvailabilityView(BaseAvailabilityUpdateView):
    action_log_type = ActionLogEntry.ACTION_TYPE_AVAIL_VENUES_SAVE
    model = Venue
