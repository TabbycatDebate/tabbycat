import traceback

from django.contrib import messages
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.generic.base import RedirectView, TemplateView, View

from .models import ActiveAdjudicator, ActiveTeam, ActiveVenue

from actionlog.mixins import LogActionMixin
from draw.models import Debate
from draw.utils import partial_break_round_split
from participants.models import Adjudicator
from actionlog.models import ActionLogEntry
from tournaments.mixins import RoundMixin
from utils.tables import TabbycatTableBuilder
from utils.mixins import SuperuserRequiredMixin, VueTableMixin
from utils.misc import reverse_round
from venues.models import Venue


class AvailabilityIndexView(RoundMixin, SuperuserRequiredMixin, TemplateView):
    template_name = 'availability_index.html'
    page_title = 'Checkins Overview'
    page_emoji = '📍'

    def get_context_data(self, **kwargs):
        r = self.get_round()
        t = self.get_tournament()
        total_adjs = r.tournament.adjudicator_set.count()
        total_venues = r.tournament.venue_set.count()

        if r.prev:
            kwargs['previous_unconfirmed'] = r.prev.get_draw().filter(
                result_status__in=[Debate.STATUS_NONE, Debate.STATUS_DRAFT]).count()
        if t.pref('share_adjs'):
            total_adjs += Adjudicator.objects.filter(tournament=None).count()
        if t.pref('share_venues'):
            total_venues += Venue.objects.filter(tournament=None).count()

        checks = []
        if r.draw_type is r.DRAW_FIRSTBREAK:
            break_size = r.break_category.break_size
            break_details = partial_break_round_split(break_size)
            checks.append({
                'type'      : 'Team',
                'total'     : break_size,
                'in_now'    : break_details[0] * 2,
                'message'   : '%s breaking teams are debating this round; %s teams are bypassing' % (break_details[0] * 2, break_details[1])
            })
        elif r.draw_type is r.DRAW_BREAK:
            last_round = r.break_category.round_set.filter(seq__lt=r.seq).order_by('-seq').first()
            advancing_teams = last_round.debate_set.count()
            checks.append({
                'type'      : 'Team',
                'total'     : advancing_teams,
                'in_now'    : advancing_teams,
                'message'   : '%s advancing teams are debating this round' % advancing_teams
            })
        else:
            checks.append({
                'type'      : 'Team',
                'total'     : t.teams.count(),
                'in_now'    : ActiveTeam.objects.filter(round=r).count(),
                'in_before' : ActiveTeam.objects.filter(round=r.prev).count() if r.prev else None,
            })

        checks.append({
            'type'      : 'Adjudicator',
            'total'     : total_adjs,
            'in_now'    : ActiveAdjudicator.objects.filter(round=r).count(),
            'in_before' : ActiveAdjudicator.objects.filter(round=r.prev).count() if r.prev else None,
        })
        checks.append({
            'type'      : 'Venue',
            'total'     : total_venues,
            'in_now'    : ActiveVenue.objects.filter(round=r).count(),
            'in_before' : ActiveVenue.objects.filter(round=r.prev).count() if r.prev else None,
        })

        # Basic check before enable the button to advance
        if all([checks[0]['in_now'] > 1, checks[1]['in_now'] > 0, checks[2]['in_now'] > 0]):
            kwargs['can_advance'] = True
        else:
            kwargs['can_advance'] = False

        kwargs['checkin_types'] = checks
        kwargs['min_adjudicators'] = int(checks[0]['in_now'] / 2)
        kwargs['min_venues'] = int(checks[0]['in_now'] / 2)
        return super().get_context_data(**kwargs)


# ==============================================================================
# Specific Activation Pages
# ==============================================================================

class AvailabilityTypeBase(RoundMixin, SuperuserRequiredMixin, VueTableMixin):
    template_name = "base_availability.html"

    def get_context_data(self, **kwargs):
        kwargs['update_url'] = reverse_round(self.update_view, self.get_round())
        return super().get_context_data(**kwargs)

    def get_table(self):
        # Do the row highlighting here?
        return super()


class AvailabilityTypeTeamView(AvailabilityTypeBase):
    page_emoji = '👂'
    page_title = 'Team Checkins'
    update_view = 'update_team_availability'

    def get_table(self):
        round = self.get_round()
        table = TabbycatTableBuilder(view=self, sort_key='team')
        teams = round.team_availability()
        table.add_checkbox_columns([t.is_active for t in teams],
            [t.id for t in teams], 'Active Now')
        if round.prev:
            pteams = round.prev.team_availability()
            table.add_column('Active in %s' % round.prev.abbreviation, [{
                'sort': t.is_active,
                'icon': 'glyphicon-ok' if t.is_active else ''
            } for t in pteams])
        table.add_team_columns(teams)
        return table


class AvailabilityTypeAdjudicatorView(AvailabilityTypeBase):
    page_emoji = '👂'
    page_title = 'Adjudicator Checkins'
    update_view = 'update_adjudicator_availability'

    def get_table(self):
        round = self.get_round()
        table = TabbycatTableBuilder(view=self, sort_key='name')
        adjudicators = round.adjudicator_availability()
        table.add_checkbox_columns([a.is_active for a in adjudicators],
            [a.id for a in adjudicators], 'Active Now')
        if round.prev:
            padjudicators = round.prev.adjudicator_availability()
            table.add_column('Active in %s' % round.prev.abbreviation, [{
                'sort': a.is_active,
                'icon': 'glyphicon-ok' if a.is_active else ''
            } for a in padjudicators])
        table.add_adjudicator_columns(adjudicators)
        return table


class AvailabilityTypeVenueView(AvailabilityTypeBase):
    page_emoji = '🎪'
    page_title = 'Venue Checkins'
    update_view = 'update_venue_availability'

    def get_table(self):
        round = self.get_round()
        table = TabbycatTableBuilder(view=self, sort_key='venue')
        venues = round.venue_availability()
        table.add_checkbox_columns([v.is_active for v in venues],
            [v.id for v in venues], 'Active Now')
        if round.prev:
            pvenues = round.prev.venue_availability()
            table.add_column('Active in %s' % round.prev.abbreviation, [{
                'sort': v.is_active,
                'icon': 'glyphicon-ok' if v.is_active else ''
            } for v in pvenues])
        table.add_column("Venue", [v.name for v in venues])
        table.add_column("Group", [v.group.name if v.group else '' for v in venues])
        table.add_column("Priority", [v.priority for v in venues])
        return table


# ==============================================================================
# Bulk Activations
# ==============================================================================

class AvailabilityActivateBase(RoundMixin, SuperuserRequiredMixin, RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        self.activate_function()
        messages.add_message(self.request, messages.SUCCESS,
            self.activation_msg)
        return reverse_round('availability_index', self.get_round())


class AvailabilityActivateAll(AvailabilityActivateBase):
    activation_msg = 'Checked in all teams, adjs and venues'

    def activate_function(self):
        self.get_round().activate_all()


class AvailabilityActivateBreakingAdjs(AvailabilityActivateBase):
    activation_msg = 'Checked in all breaking adjudicators'

    def activate_function(self):
        self.get_round().activate_all_breaking_adjs()


class AvailabilityActivateFromPrevious(AvailabilityActivateBase):
    activation_msg = 'Checked in all teams, adjs and venues from previous round'

    def activate_function(self):
        self.get_round().activate_previous()


# ==============================================================================
# Specific Activation Actions
# ==============================================================================

class AvailabilityUpdateBase(RoundMixin, SuperuserRequiredMixin, View, LogActionMixin):

    def post(self, request, *args, **kwargs):
        try:
            references = request.POST.getlist('references[]')
            self.set_availabilities(self.get_round(), references)
            return HttpResponse('ok')
        except:
            traceback.print_exc()
            return HttpResponseBadRequest()


class AvailabilityUpdateAdjudicators(AvailabilityUpdateBase):
    action_log_type = ActionLogEntry.ACTION_TYPE_AVAIL_ADJUDICATORS_SAVE

    def set_availabilities(self, round, ids):
        round.set_available_adjudicators(ids)


class AvailabilityUpdateTeams(AvailabilityUpdateBase):
    action_log_type = ActionLogEntry.ACTION_TYPE_AVAIL_TEAMS_SAVE

    def set_availabilities(self, round, ids):
        round.set_available_teams(ids)


class AvailabilityUpdateVenues(AvailabilityUpdateBase):
    action_log_type = ActionLogEntry.ACTION_TYPE_AVAIL_VENUES_SAVE

    def set_availabilities(self, round, ids):
        round.set_available_venues(ids)
