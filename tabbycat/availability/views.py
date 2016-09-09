import traceback

from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.db.models import Prefetch
from django.db.models.expressions import RawSQL
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.generic.base import RedirectView, TemplateView, View

from .models import ActiveAdjudicator, ActiveTeam, ActiveVenue

from availability.models import RoundAvailability
from actionlog.mixins import LogActionMixin
from draw.models import Debate
from draw.utils import partial_break_round_split
from participants.models import Adjudicator, Team
from actionlog.models import ActionLogEntry
from tournaments.mixins import RoundMixin
from utils.tables import TabbycatTableBuilder
from utils.mixins import SuperuserRequiredMixin, VueTableTemplateView
from utils.misc import reverse_round
from venues.models import Venue


class AvailabilityIndexView(RoundMixin, SuperuserRequiredMixin, TemplateView):
    template_name = 'availability_index.html'
    page_title = 'Check-Ins Overview'
    page_emoji = '📍'

    def get_context_data(self, **kwargs):
        r = self.get_round()
        t = self.get_tournament()
        total_adjs = r.tournament.adjudicator_set.count()
        total_venues = r.tournament.venue_set.count()

        if r.prev:
            kwargs['previous_unconfirmed'] = r.prev.debate_set.filter(
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

        instances = self.get_queryset().prefetch_related(Prefetch('round_availabilities',
                queryset=RoundAvailability.objects.filter(round=round), to_attr='availability'))
        if round.prev:
            instances = instances.prefetch_related(Prefetch('round_availabilities',
                    queryset=RoundAvailability.objects.filter(round=round.prev), to_attr='prev_availability'))

        table.add_checkbox_columns([len(inst.availability) > 0 for inst in instances],
            [inst.id for inst in instances], "Active Now")

        if round.prev:
            table.add_column("Active in %s" % round.prev.abbreviation, [{
                'sort': len(inst.prev_availability) > 0,
                'icon': 'glyphicon-ok' if len(inst.prev_availability) > 0 else ''
            } for inst in instances])

        self.add_description_columns(table, instances)
        return table


class AvailabilityTypeTeamView(AvailabilityTypeBase):
    page_emoji = '👂'
    model = Team
    sort_key = 'team'
    update_view = 'update_team_availability'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('speaker_set')

    @staticmethod
    def add_description_columns(table, teams):
        table.add_team_columns(teams)


class AvailabilityTypeAdjudicatorView(AvailabilityTypeBase):
    page_emoji = '👂'
    model = Adjudicator
    sort_key = 'name'
    update_view = 'update_adjudicator_availability'

    @staticmethod
    def add_description_columns(table, adjudicators):
        table.add_adjudicator_columns(adjudicators)


class AvailabilityTypeVenueView(AvailabilityTypeBase):
    page_emoji = '🎪'
    model = Venue
    sort_key = 'venue'
    update_view = 'update_venue_availability'

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

class AvailabilityActivateBase(RoundMixin, SuperuserRequiredMixin, RedirectView):

    round_redirect_pattern_name = 'availability_index'

    def get_redirect_url(self, *args, **kwargs):
        self.activate_function()
        messages.add_message(self.request, messages.SUCCESS,
            self.activation_msg)
        return super().get_redirect_url(*args, **kwargs)


class AvailabilityActivateAll(AvailabilityActivateBase):
    activation_msg = 'Checked in all teams, adjudicators and venues'

    def activate_function(self):
        self.get_round().activate_all()


class AvailabilityActivateBreakingAdjs(AvailabilityActivateBase):
    activation_msg = 'Checked in all breaking adjudicators'

    def activate_function(self):
        self.get_round().activate_all_breaking_adjs()


class AvailabilityActivateFromPrevious(AvailabilityActivateBase):
    activation_msg = 'Checked in all teams, adjudicators and venues from previous round'

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
