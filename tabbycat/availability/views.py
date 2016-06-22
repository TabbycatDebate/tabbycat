from django.contrib import messages
from django.shortcuts import render
from django.views.generic.base import TemplateView, RedirectView

from .models import ActiveVenue, ActiveTeam, ActiveAdjudicator

from draw.models import Debate
from participants.models import Person
from actionlog.models import ActionLogEntry
from tournaments.mixins import RoundMixin
from tournaments.models import Round
from utils.tables import TabbycatTableBuilder
from utils.views import admin_required, expect_post, round_view, redirect_round, public_optional_round_view, public_optional_tournament_view, tournament_view
from utils.mixins import SuperuserRequiredMixin, VueTableMixin, PostOnlyRedirectView
from utils.misc import reverse_round


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

        checks = [{
            'type'      : 'Team',
            'total'     : t.teams.count(),
            'in_now'    : ActiveTeam.objects.filter(round=r).count(),
            'in_before' : ActiveTeam.objects.filter(round=r.prev).count() if r.prev else None,
        }, {
            'type'      : 'Adjudicator',
            'total'     : total_adjs,
            'in_now'    : ActiveAdjudicator.objects.filter(round=r).count(),
            'in_before' : ActiveAdjudicator.objects.filter(round=r.prev).count() if r.prev else None,
        }, {
            'type'      : 'Venue',
            'total'     : total_venues,
            'in_now'    : ActiveVenue.objects.filter(round=r).count(),
            'in_before' : ActiveVenue.objects.filter(round=r.prev).count() if r.prev else None,
        }]

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


class AvailabilityActivateFromPrevious(AvailabilityActivateBase):
    activation_msg = 'Checked in all teams, adjs and venues from previous round'
    def activate_function(self):
        self.get_round().activate_previous()


class AvailabilityActivateBreakingAdjs(AvailabilityActivateBase):
    activation_msg = 'Checked in all breaking adjudicators'
    def activate_function(self):
        self.get_round().round.activate_all_breaking_adjs()


class AvailabilityActivateBreakingTeams(AvailabilityActivateBase):
    activation_msg = 'Checked in all breaking teams'
    def activate_function(self):
        self.get_round().round.activate_all_breaking_teams()


class AvailabilityActivateAdvancingTeams(AvailabilityActivateBase):
    activation_msg = 'Checked in all advancing teams'
    def activate_function(self):
        self.get_round().round.activate_all_advancing_teams()


# ==============================================================================
# Specific Activation Pages
# ==============================================================================

class AvailabilityTypeBase(RoundMixin, SuperuserRequiredMixin, VueTableMixin):
    template_name = "base_availability.html"


class AvailabilityTypeTeamView(AvailabilityTypeBase):
    page_emoji = '👂'
    page_title = 'Team Checkins'

    def get_table(self):
        round = self.get_round()
        table = TabbycatTableBuilder(view=self)
        teams = round.team_availability()
        table.add_column("Active", ['' for t in teams])
        table.add_team_columns(teams)
        return table


class AvailabilityTypeAdjudicatorView(AvailabilityTypeBase):
    page_emoji = '👂'
    page_title = 'Adjudicator Checkins'

    def get_table(self):
        round = self.get_round()
        table = TabbycatTableBuilder(view=self)
        adjudicators = round.adjudicator_availability()
        table.add_column("Active", ['Test' for a in adjudicators])
        table.add_adjudicator_columns(adjudicators)
        return table


class AvailabilityTypePersonView(AvailabilityTypeBase):
    page_emoji = '👱'
    page_title = 'People Checkins'

    def get_table(self):
        round = self.get_round()
        table = TabbycatTableBuilder(view=self)
        people = round.person_availability()
        return table

class AvailabilityTypeVenueView(AvailabilityTypeBase):
    page_emoji = '🎪'
    page_title = 'Venue Checkins'

    def get_table(self):
        round = self.get_round()
        table = TabbycatTableBuilder(view=self)
        venues = round.venue_availability()
        table.add_column("Active", ['Test' for v in venues])
        table.add_column("Venue", [v.name for v in venues])
        table.add_column("Group", [v.group.name if v.group else '' for v in venues])
        table.add_column("Priority", [v.priority for v in venues])
        return table

# ==============================================================================
# Specific Activation Pages Actions
# ==============================================================================

# Public (for barcode checkins)
@round_view
def checkin(request, round):
    context = {}
    if request.method == 'POST':
        v = request.POST.get('barcode_id')
        try:
            barcode_id = int(v)
            p = Person.objects.get(barcode_id=barcode_id)
            ch, created = Checkin.objects.get_or_create(
                person=p,
                round=round
            )
            context['person'] = p

        except (ValueError, Person.DoesNotExist):
            context['unknown_id'] = v

    return render(request, 'person_checkin.html', context)


# public (for barcode checkins)
@round_view
def post_checkin(request, round):
    v = request.POST.get('barcode_id')
    try:
        barcode_id = int(v)
        p = Person.objects.get(barcode_id=barcode_id)
        ch, created = Checkin.objects.get_or_create(
            person=p,
            round=round
        )

        message = p.checkin_message

        if not message:
            message = "Checked in %s" % p.name
        return HttpResponse(message)

    except (ValueError, Person.DoesNotExist):
        return HttpResponse("Unknown Id: %s" % v)


@round_view
def checkin_results(request, round, model, context_name):
    return _availability(request, round, model, context_name)


def _update_availability(request, round, update_method, active_model, active_attr):
    if request.POST.get('copy'):
        prev_round = Round.objects.get(tournament=round.tournament,
                                       seq=round.seq-1)

        prev_objects = active_model.objects.filter(round=prev_round)
        available_ids = [getattr(o, '%s_id' % active_attr) for o in prev_objects]
        getattr(round, update_method)(available_ids)

        return HttpResponseRedirect(request.path.replace('update/', ''))

    available_ids = [int(a.replace("check_", "")) for a in list(request.POST.keys())
                     if a.startswith("check_")]

    # Calling the relevenat update method as defined in Round
    getattr(round, update_method)(available_ids)

    ACTION_TYPES = {
        ActiveVenue:       ActionLogEntry.ACTION_TYPE_AVAIL_VENUES_SAVE,
        ActiveTeam:        ActionLogEntry.ACTION_TYPE_AVAIL_TEAMS_SAVE,
        ActiveAdjudicator: ActionLogEntry.ACTION_TYPE_AVAIL_ADJUDICATORS_SAVE,
    }
    if active_model in ACTION_TYPES:
        ActionLogEntry.objects.log(type=ACTION_TYPES[active_model],  # flake8: noqa
            user=request.user, round=round, tournament=round.tournament)

    return HttpResponse("ok")


@admin_required
@expect_post
@round_view
def update_availability(request, round, update_method, active_model, active_attr):
    return _update_availability(request, round, update_method, active_model, active_attr)


@expect_post
@round_view
def checkin_update(request, round, update_method, active_model, active_attr):
    return _update_availability(request, round, update_method, active_model, active_attr)
