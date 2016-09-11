import logging

from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.generic.base import TemplateView, View

from . import utils

from availability.models import RoundAvailability
from actionlog.mixins import LogActionMixin
from draw.models import Debate
from draw.utils import partial_break_round_split
from participants.models import Adjudicator, Team
from actionlog.models import ActionLogEntry
from tournaments.mixins import RoundMixin
from utils.tables import TabbycatTableBuilder
from utils.mixins import PostOnlyRedirectView, SuperuserRequiredMixin, VueTableTemplateView
from utils.misc import reverse_round
from venues.models import Venue

logger = logging.getLogger(__name__)


class AvailabilityIndexView(RoundMixin, SuperuserRequiredMixin, TemplateView):
    template_name = 'availability_index.html'
    page_title = 'Check-Ins Overview'
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

        adjs = self._get_dict(tournament.relevant_adjudicators)
        venues = self._get_dict(tournament.relevant_venues)

        # Basic check before enable the button to advance
        kwargs['can_advance'] = teams['in_now'] > 1 and adjs['in_now'] > 0 and venues['in_now'] > 0
        kwargs['checkin_types'] = [teams, adjs, venues]
        kwargs['min_adjudicators'] = teams['in_now'] // 2
        kwargs['min_venues'] = teams['in_now'] // 2
        return super().get_context_data(**kwargs)

    def _get_breaking_teams_dict(self):
        r = self.get_round()
        if r.draw_type is r.DRAW_FIRSTBREAK:
            break_size = r.break_category.break_size
            break_details = partial_break_round_split(break_size)
            return {
                'type'      : 'Team',
                'total'     : break_size,
                'in_now'    : break_details[0] * 2,
                'message'   : '%s breaking teams are debating this round; %s teams are bypassing' % (break_details[0] * 2, break_details[1])
            }
        elif r.draw_type is r.DRAW_BREAK:
            last_round = r.break_category.round_set.filter(seq__lt=r.seq).order_by('-seq').first()
            advancing_teams = last_round.debate_set.count()
            return {
                'type'      : 'Team',
                'total'     : advancing_teams,
                'in_now'    : advancing_teams,
                'message'   : '%s advancing teams are debating this round' % advancing_teams
            }

    def _get_dict(self, queryset_all):
        contenttype = ContentType.objects.get_for_model(queryset_all.model)
        availability_queryset = RoundAvailability.objects.filter(content_type=contenttype)
        round = self.get_round()
        result = {
            'type': queryset_all.model._meta.verbose_name.title(),
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
        return self.model._meta.verbose_name.title() + " Check-Ins"

    def get_context_data(self, **kwargs):
        kwargs['update_url'] = reverse_round(self.update_view, self.get_round())
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        return self.model.objects.filter(tournament=self.get_tournament())

    def get_table(self):
        round = self.get_round()
        table = TabbycatTableBuilder(view=self, sort_key=self.sort_key)

        queryset = utils.annotate_availability(self.get_queryset(), round)

        table.add_checkbox_columns([inst.available for inst in queryset],
            [inst.id for inst in queryset], "Active Now")

        if round.prev:
            table.add_column("Active in %s" % round.prev.abbreviation, [{
                'sort': inst.prev_available,
                'icon': 'glyphicon-ok' if inst.prev_available else ''
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
        return super().get_queryset().select_related('group')

    @staticmethod
    def add_description_columns(table, venues):
        table.add_column("Venue", [v.name for v in venues])
        table.add_column("Group", [v.group.name if v.group else '' for v in venues])
        table.add_column("Priority", [v.priority for v in venues])


# ==============================================================================
# Bulk Activations
# ==============================================================================

class BaseBulkActivationView(RoundMixin, SuperuserRequiredMixin, PostOnlyRedirectView):

    round_redirect_pattern_name = 'availability-index'

    def post(self, request, *args, **kwargs):
        self.activate_function()
        messages.add_message(self.request, messages.SUCCESS, self.activation_msg)
        return super().post(request, *args, **kwargs)


class CheckInAllInRoundView(BaseBulkActivationView):
    activation_msg = 'Checked in all teams, adjudicators and venues.'

    def activate_function(self):
        utils.activate_all(self.get_round())


class CheckInAllBreakingAdjudicatorsView(BaseBulkActivationView):
    activation_msg = 'Checked in all breaking adjudicators.'

    def activate_function(self):
        utils.set_availability(self.get_tournament().relevant_adjudicators.filter(breaking=True),
                self.get_round())


class CheckInAllFromPreviousRoundView(BaseBulkActivationView):
    activation_msg = 'Checked in all teams, adjudicators and venues from previous round.'

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
        try:
            references = request.POST.getlist('references[]')
            utils.set_availability_by_id(self.model, references, self.get_round())
            self.log_action()
            return HttpResponse('ok')

        except:
            logger.critical("Error handling availability updates", exc_info=True)
            return HttpResponseBadRequest()


class UpdateAdjudicatorsAvailabilityView(BaseAvailabilityUpdateView):
    action_log_type = ActionLogEntry.ACTION_TYPE_AVAIL_ADJUDICATORS_SAVE
    model = Adjudicator


class UpdateTeamsAvailabilityView(BaseAvailabilityUpdateView):
    action_log_type = ActionLogEntry.ACTION_TYPE_AVAIL_TEAMS_SAVE
    model = Team


class UpdateVenuesAvailabilityView(BaseAvailabilityUpdateView):
    action_log_type = ActionLogEntry.ACTION_TYPE_AVAIL_VENUES_SAVE
    model = Venue
