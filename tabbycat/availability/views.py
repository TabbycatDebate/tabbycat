import json
import logging
from collections import OrderedDict

from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError
from django.db.models import Min
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy, ngettext
from django.views.generic.base import TemplateView, View

from actionlog.mixins import LogActionMixin
from actionlog.models import ActionLogEntry
from availability.models import RoundAvailability
from checkins.utils import get_checkins
from draw.generator.utils import partial_break_round_split
from draw.models import Debate
from participants.models import Adjudicator, Team
from tournaments.mixins import RoundMixin
from utils.misc import reverse_round
from utils.mixins import AdministratorMixin
from utils.tables import TabbycatTableBuilder
from utils.views import PostOnlyRedirectView, VueTableTemplateView
from venues.models import Venue

from . import utils

logger = logging.getLogger(__name__)


class AvailabilityIndexView(RoundMixin, AdministratorMixin, TemplateView):
    template_name = 'availability_index.html'
    page_title = gettext_lazy("Availability")
    page_emoji = '📍'

    def get_context_data(self, **kwargs):
        if self.round.prev:
            kwargs['previous_unconfirmed'] = self.round.prev.debate_set.filter(
                result_status__in=[Debate.STATUS_NONE, Debate.STATUS_DRAFT]).count()

            kwargs['new_adjs'] = Adjudicator.objects.filter(
                round_availabilities__round=self.round,
            ).exclude(
                round_availabilities__round=self.round.prev,
            )
            kwargs['new_venues'] = Venue.objects.filter(
                round_availabilities__round=self.round,
            ).exclude(
                round_availabilities__round=self.round.prev,
            )
            kwargs['lost_adjs'] = Adjudicator.objects.filter(
                round_availabilities__round=self.round.prev,
            ).exclude(
                round_availabilities__round=self.round,
            )
            kwargs['lost_venues'] = Venue.objects.filter(
                round_availabilities__round=self.round.prev,
            ).exclude(
                round_availabilities__round=self.round,
            )

        if self.round.is_break_round:
            teams = self._get_breaking_teams_dict()
        else:
            teams = self._get_dict(self.tournament.team_set)

        # Basic check before enable the button to advance
        adjs = self._get_dict(self.tournament.relevant_adjudicators)
        venues = self._get_dict(self.tournament.relevant_venues)
        kwargs['can_advance'] = teams['in_now'] > 1 and adjs['in_now'] > 0 and venues['in_now'] > 0

        # Order needs to be predictable when iterating through values
        kwargs['availability_info'] = OrderedDict([('teams', teams), ('adjs', adjs), ('venues', venues)])

        # Check the number of teams/adjudicators is sufficient
        if self.tournament.pref('teams_in_debate') == 'two':
            per_room_divisor = 2
        else:
            per_room_divisor = 4
        kwargs['min_adjudicators'] = teams['in_now'] // per_room_divisor
        kwargs['min_venues'] = teams['in_now'] // per_room_divisor

        kwargs['error_type'] = getattr(self, 'error_type', None)
        return super().get_context_data(**kwargs)

    def _get_breaking_teams_dict(self):
        if self.round.break_category is None:
            self.error_type = 'no_break_category'
            return {
                'total': 0,
                'in_now': 0,
                'message': _("no teams are debating"),
            }

        if self.round.prev is None or not self.round.prev.is_break_round:
            break_size = self.round.break_category.breakingteam_set_competing.count()
            teams_dict = {'total': break_size}
            if break_size < 2:
                teams_dict['in_now'] = 0
                teams_dict['message'] = ngettext(
                    # Translators: nteams in this string can only be 0 or 1
                    "%(nteams)d breaking team — no debates can happen",
                    "%(nteams)d breaking teams — no debates can happen",  # in English, used when break_size == 0
                    break_size) % {'nteams': break_size}
            else:
                debates, bypassing = partial_break_round_split(break_size)
                teams_dict['in_now'] = 2 * debates
                teams_dict['message'] = ngettext(
                    # Translators: ndebating in this string is always at least 2
                    "%(ndebating)d breaking team is debating this round",  # never used in English, but needed for i18n
                    "%(ndebating)d breaking teams are debating this round",
                    2 * debates) % {'ndebating': 2 * debates}
                if bypassing > 0:
                    teams_dict['message'] += ngettext(
                        # Translators: This gets appended to the previous string (the one with
                        # ndebating in it) if (and only if) nbypassing is greater than 0.
                        # "It" refers to this round.
                        "; %(nbypassing)d team is bypassing it",
                        "; %(nbypassing)d teams are bypassing it",
                        bypassing) % {'nbypassing': bypassing}
            return teams_dict

        else:
            nadvancing = self.round.prev.debate_set.count()
            if self.tournament.pref('teams_in_debate') == 'bp':
                nadvancing *= 2

            # add teams that bypassed the last round
            nadvancing += self.round.prev.debate_set.all().aggregate(
                    lowest_room=Coalesce(Min('room_rank') - 1, 0))['lowest_room']

            return {
                'total'     : nadvancing,
                'in_now'    : nadvancing,
                'message'   : ngettext(
                    # Translators: nadvancing in this string is always at least 2
                    "%(nadvancing)s advancing team is debating this round",  # never used, but needed for i18n
                    "%(nadvancing)s advancing teams are debating this round",
                    nadvancing) % {'nadvancing': nadvancing},
            }

    def _get_dict(self, queryset_all):
        contenttype = ContentType.objects.get_for_model(queryset_all.model)
        availability_queryset = RoundAvailability.objects.filter(content_type=contenttype)
        round = self.round
        result = {
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

class AvailabilityTypeBase(RoundMixin, AdministratorMixin, VueTableTemplateView):
    template_name = "base_availability.html"

    def get_context_data(self, **kwargs):
        kwargs['model'] = self.model._meta.label  # does not get translated
        kwargs['saveURL'] = reverse_round(self.update_view, self.round)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        return self.model.objects.filter(tournament=self.tournament)

    def get_table(self):
        table = TabbycatTableBuilder(view=self, sort_key=self.sort_key)
        queryset = utils.annotate_availability(self.get_queryset(), self.round)
        self.annotate_checkins(queryset, self.tournament)

        table.add_column({'key': 'active', 'title': _("Active Now")}, [{
            'component': 'check-cell',
            'checked': inst.available,
            'sort': inst.available,
            'id': inst.id,
            'prev': inst.prev_available if self.round.prev else False,
            'checked_in': inst.checked_in,
            'type': 0,
        } for inst in queryset])

        if self.round.prev:
            title = _("Active in %(prev_round)s") % {'prev_round': self.round.prev.abbreviation}
            table.add_column({'key': 'active-prev', 'title': title}, [{
                'sort': inst.prev_available,
                'icon': 'check' if inst.prev_available else '',
            } for inst in queryset])

        checked_in_header = {'key': "tournament", 'title': _('Checked-In')}
        checked_in_data = [{
            'sort': inst.checked_in, 'icon': inst.checked_icon, 'tooltip': inst.checked_tooltip,
        } for inst in queryset]
        table.add_column(checked_in_header, checked_in_data)

        self.add_description_columns(table, queryset)
        return table


class AvailabilityTypeTeamView(AvailabilityTypeBase):
    page_title = gettext_lazy("Team Availability")
    page_emoji = '👂'
    model = Team
    sort_key = 'team'
    update_view = 'availability-update-teams'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('speaker_set').prefetch_related('speaker_set__checkin_identifier')

    @staticmethod
    def add_description_columns(table, teams):
        table.add_team_columns(teams)

    @staticmethod
    def annotate_checkins(queryset, t):
        return get_checkins(queryset, t, 'checkin_window_people')


class AvailabilityTypeAdjudicatorView(AvailabilityTypeBase):
    page_title = gettext_lazy("Adjudicator Availability")
    page_emoji = '👂'
    model = Adjudicator
    sort_key = 'name'
    update_view = 'availability-update-adjudicators'

    def get_queryset(self):
        return super().get_queryset().select_related('checkin_identifier')

    @staticmethod
    def add_description_columns(table, adjudicators):
        table.add_adjudicator_columns(adjudicators)

    @staticmethod
    def annotate_checkins(queryset, t):
        return get_checkins(queryset, t, 'checkin_window_people')


class AvailabilityTypeVenueView(AvailabilityTypeBase):
    page_title = gettext_lazy("Room Availability")
    page_emoji = '🎪'
    model = Venue
    sort_key = 'venue'
    update_view = 'availability-update-venues'

    def get_queryset(self):
        return super().get_queryset().select_related('checkin_identifier').prefetch_related('venuecategory_set')

    @staticmethod
    def add_description_columns(table, venues):
        for v in venues:
            v.cats = ", ".join([vc.name for vc in v.venuecategory_set.all()])

        table.add_column({'key': 'venue', 'title': _("Room")}, [v.name for v in venues])
        table.add_column(
            {'key': 'display', 'title': _("Display Name (for the draw)")},
            [v.display_name for v in venues],
        )
        table.add_column({'key': 'categories', 'title': _("Categories")}, [v.cats for v in venues])
        table.add_column({'key': 'priority', 'title': _("Priority")}, [v.priority for v in venues])

    @staticmethod
    def annotate_checkins(queryset, t):
        return get_checkins(queryset, t, 'checkin_window_venues')


# ==============================================================================
# Bulk Activations
# ==============================================================================

class BaseBulkActivationView(RoundMixin, AdministratorMixin, PostOnlyRedirectView):

    round_redirect_pattern_name = 'availability-index'

    def post(self, request, *args, **kwargs):
        try:
            self.activate_function()
            messages.success(self.request, self.activation_msg)
        except IntegrityError:
            messages.error(self.request, _("Failed to update some or all "
                                           "availabilities due to an integrity"
                                           "error. You should retry this "
                                           "action or make individual updates."))
        return super().post(request, *args, **kwargs)


class CheckInAllInRoundView(BaseBulkActivationView):
    activation_msg = gettext_lazy("Checked in all teams, adjudicators and rooms.")

    def activate_function(self):
        utils.activate_all(self.round)


class CheckInAllBreakingAdjudicatorsView(BaseBulkActivationView):
    activation_msg = gettext_lazy("Checked in all breaking adjudicators.")

    def activate_function(self):
        utils.set_availability(self.tournament.relevant_adjudicators.filter(breaking=True),
                self.round)


class CheckInAllFromPreviousRoundView(BaseBulkActivationView):
    activation_msg = gettext_lazy("Checked in all teams, adjudicators and rooms from previous round.")

    def activate_function(self):
        t = self.tournament
        items = [(Team, t.team_set), (Adjudicator, t.relevant_adjudicators), (Venue, t.relevant_venues)]

        for model, relevant_instances in items:
            contenttype = ContentType.objects.get_for_model(model)
            previous_ids = set(a['object_id'] for a in
                RoundAvailability.objects.filter(content_type=contenttype, round=self.round.prev).values('object_id'))
            logger.debug("Previous IDs for %s: %s", model._meta.verbose_name_plural, previous_ids)
            relevant_ids = set(x['id'] for x in relevant_instances.values('id'))
            logger.debug("Relevant IDs for %s: %s", model._meta.verbose_name_plural, relevant_ids)
            previous_relevant_ids = previous_ids & relevant_ids
            logger.debug("Checking in %s: %s", model._meta.verbose_name_plural, previous_relevant_ids)
            utils.set_availability_by_id(model, previous_relevant_ids, self.round)


# ==============================================================================
# Specific Activation Actions
# ==============================================================================

class BaseAvailabilityUpdateView(RoundMixin, AdministratorMixin, LogActionMixin, View):

    def post(self, request, *args, **kwargs):
        body = self.request.body.decode('utf-8')
        posted_info = json.loads(body)

        active_ids = [] # Unlike other checks; we just pass IDs on not the bool
        for key, value in posted_info.items():
            if value['checked']:
                active_ids.append(key)

        try:
            utils.set_availability_by_id(self.model, active_ids, self.round)
            self.log_action()
        except IntegrityError:
            message = """ of an integrity error when issuing the availability
                update — this typically means that the availability for an
                adjudicator has already been set to be what was saved"""
            return JsonResponse({'status': 'false', 'message': message}, status=500)
        except Exception:
            message = " an error handling availability updates"
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
