import json
import logging
from threading import Lock

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.views.decorators.cache import cache_page
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, FormView

from draw.models import Debate, DebateTeam
from participants.models import Institution, Team
from utils.forms import SuperuserCreationForm
from utils.mixins import SuperuserRequiredMixin
from utils.views import admin_required, expect_post, public_optional_tournament_view, redirect_round, round_view, tournament_view
from utils.misc import redirect_tournament
from venues.models import InstitutionVenueConstraint, TeamVenueConstraint, VenueGroup

from .forms import TournamentForm
from .mixins import TournamentMixin
from .models import Division, Tournament

User = get_user_model()
logger = logging.getLogger(__name__)


@cache_page(10)  # Set slower to show new indexes so it will show new pages
@tournament_view
def public_index(request, t):
    return render(request, 'public_tournament_index.html')


def index(request):
    tournaments = Tournament.objects.all()
    if tournaments.count() == 1 and not request.user.is_authenticated():
        logger.debug('One tournament only, user is: %s, redirecting to tournament-public-index', request.user)
        return redirect_tournament('tournament-public-index', tournaments.first())

    elif not tournaments.exists() and not User.objects.exists():
        logger.debug('No users and no tournaments, redirecting to blank-site-start')
        return redirect('blank-site-start')

    else:
        return render(request, 'site_index.html', dict(tournaments=tournaments))


class TournamentAdminHomeView(LoginRequiredMixin, TournamentMixin, TemplateView):

    template_name = "tournament_index.html"

    def get_context_data(self, **kwargs):
        tournament = self.get_tournament()
        round = tournament.current_round
        assert(round is not None)
        kwargs["round"] = round
        kwargs["readthedocs_version"] = settings.READTHEDOCS_VERSION
        kwargs["blank"] = not (tournament.team_set.exists() or tournament.adjudicator_set.exists() or tournament.venue_set.exists())

        draw = round.get_draw()
        kwargs["total_ballots"] = draw.count()
        stats_none = draw.filter(result_status=Debate.STATUS_NONE).count()
        stats_draft = draw.filter(result_status=Debate.STATUS_DRAFT).count()
        stats_confirmed = draw.filter(result_status=Debate.STATUS_CONFIRMED).count()
        kwargs["stats"] = [[0,stats_confirmed], [0,stats_draft], [0,stats_none]]

        return super().get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        tournament = self.get_tournament()
        if tournament.current_round is None:
            if self.request.user.is_superuser:
                tournament.current_round = tournament.round_set.order_by('seq').first()
                if tournament.current_round is None:
                    return HttpResponse('<p>Error: This tournament has no rounds; you\'ll need to add some in the <a href="/admin/">Edit Data</a> area.</p>')
                messages.warning(self.request, "The current round wasn't set, so it's been automatically set to the first round.")
                logger.warning("Automatically set current round to {}".format(tournament.current_round))
                tournament.save()
                self.request.tournament = tournament  # Update for context processors
            else:
                raise Http404()
        return super().get(self, request, *args, **kwargs)


@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@public_optional_tournament_view('public_divisions')
def public_divisions(request, t):
    divisions = Division.objects.filter(tournament=t).all().select_related('venue_group')
    divisions = sorted(divisions, key=lambda x: x.name)
    venue_groups = set(d.venue_group for d in divisions)
    for uvg in venue_groups:
        uvg.divisions = [d for d in divisions if d.venue_group == uvg]

    return render(request, 'public_divisions.html', dict(venue_groups=venue_groups))


@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@tournament_view
def all_tournaments_all_venues(request, t):
    venues = VenueGroup.objects.all()
    return render(request, 'public_all_tournament_venues.html', dict(venues=venues))


@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@tournament_view
def all_draws_for_venue(request, t, venue_id):
    venue_group = VenueGroup.objects.get(pk=venue_id)
    debates = Debate.objects.filter(division__venue_group=venue_group).select_related(
        'round','round__tournament','division')
    return render(request, 'public_all_draws_for_venue.html', dict(
        venue_group=venue_group, debates=debates))


@tournament_view
def all_draws_for_institution(request, t, institution_id):
    # TODO: move to draws app
    institution = Institution.objects.get(pk=institution_id)
    debate_teams = DebateTeam.objects.filter(team__institution=institution).select_related(
        'debate', 'debate__division', 'debate__division__venue_group', 'debate__round')
    debates = [dt.debate for dt in debate_teams]

    return render(request, 'public_all_draws_for_institution.html', dict(
        institution=institution, debates=debates))


@admin_required
@round_view
def round_increment_check(request, round):
    if round != request.tournament.current_round:  # Doesn't make sense if not current round
        raise Http404()
    num_unconfirmed = round.get_draw().filter(
        result_status__in=[Debate.STATUS_NONE, Debate.STATUS_DRAFT]).count()
    increment_ok = num_unconfirmed == 0
    return render(request, "round_increment_check.html", dict(
        num_unconfirmed=num_unconfirmed, increment_ok=increment_ok))


@admin_required
@expect_post
@round_view
def round_increment(request, round):
    if round != request.tournament.current_round:  # Doesn't make sense if not current round
        raise Http404()
    request.tournament.advance_round()
    return redirect_round('draw', request.tournament.current_round)


@admin_required
@tournament_view
def division_allocations(request, t):
    teams = list(Team.objects.filter(tournament=t).all().values(
        'id', 'short_reference', 'division', 'use_institution_prefix', 'institution__code', 'institution__id'))

    for team in teams:
        team['institutional_preferences'] = list(
            InstitutionVenueConstraint.objects.filter(
                institution=team['institution__id']).values(
                    'venue_group__short_name', 'priority', 'venue_group__id').order_by('-priority'))
        team['team_preferences'] = list(
            TeamVenueConstraint.objects.filter(
                team=team['id']).values(
                    'venue_group__short_name', 'priority', 'venue_group__id').order_by('-priority'))

        # team['institutional_preferences'] = "test"
        # team['individual_preferences'] = "test"

    teams = json.dumps(teams)

    venue_groups = json.dumps(list(
        VenueGroup.objects.all().values(
            'id', 'short_name', 'team_capacity')))

    divisions = json.dumps(list(Division.objects.filter(tournament=t).all().values(
        'id', 'name', 'venue_group')))

    return render(request, "division_allocations.html", dict(
        teams=teams, divisions=divisions, venue_groups=venue_groups))


@admin_required
@tournament_view
def create_division(request, t):
    division = Division.objects.create(name="temporary_name", tournament=t)
    division.save()
    division.name = "%s" % division.id
    division.save()
    return redirect_tournament('division_allocations', t)


@admin_required
@tournament_view
def create_byes(request, t):
    divisions = Division.objects.filter(tournament=t)
    Team.objects.filter(tournament=t, type=Team.TYPE_BYE).delete()
    for division in divisions:
        teams_count = Team.objects.filter(division=division).count()
        if teams_count % 2 != 0:
            bye_institution, created = Institution.objects.get_or_create(
                name="Byes", code="Byes")
            Team(
                institution=bye_institution,
                reference="Bye for Division " + division.name,
                short_reference="Bye",
                tournament=t,
                division=division,
                use_institution_prefix=False,
                type=Team.TYPE_BYE
            ).save()

    return redirect_tournament('division_allocations', t)


@admin_required
@tournament_view
def create_division_allocation(request, t):
    from tournaments.division_allocator import DivisionAllocator

    teams = list(Team.objects.filter(tournament=t))
    institutions = Institution.objects.all()
    venue_groups = VenueGroup.objects.all()

    # Delete all existing divisions - this shouldn't affect teams (on_delete=models.SET_NULL))
    divisions = Division.objects.filter(tournament=t).delete()

    alloc = DivisionAllocator(teams=teams, divisions=divisions,
        venue_groups=venue_groups, tournament=t, institutions=institutions)
    success = alloc.allocate()

    if success:
        return redirect_tournament('division_allocations', t)
    else:
        return HttpResponseBadRequest("Couldn't create divisions")


@admin_required
@expect_post
@tournament_view
def set_division_venue_group(request, t):
    division = Division.objects.get(pk=int(request.POST['division']))
    if request.POST['venueGroup'] == '':
        division.venue_group = None
    else:
        division.venue_group = VenueGroup.objects.get(pk=int(request.POST['venueGroup']))

    print("saved venue group for for", division.name)
    division.save()
    return HttpResponse("ok")


@admin_required
@expect_post
@tournament_view
def set_team_division(request, t):
    team = Team.objects.get(pk=int(request.POST['team']))
    if request.POST['division'] == '':
        team.division = None
    else:
        team.division = Division.objects.get(pk=int(request.POST['division']))
        team.save()
        print("saved divison for ", team.short_name)

    return HttpResponse("ok")


@admin_required
@expect_post
@tournament_view
def set_division_time(request, t):
    division = Division.objects.get(pk=int(request.POST['division']))
    if request.POST['division'] == '':
        division = None
    else:
        division.time_slot = request.POST['time']
        division.save()

    return HttpResponse("ok")


class BlankSiteStartView(FormView):
    """This view is presented to the user when there are no tournaments and no
    user accounts. It prompts the user to create a first superuser. It rejects
    all requests, GET or POST, if there exists any user account in the
    system."""

    form_class = SuperuserCreationForm
    template_name = "blank_site_start.html"
    lock = Lock()
    success_url = reverse_lazy('tabbycat-index')

    def get(self, request):
        if User.objects.exists():
            logger.error("Tried to get the blank-site-start view when a user account already exists.")
            return redirect('tabbycat-index')

        return super().get(request)

    def post(self, request):
        with self.lock:
            if User.objects.exists():
                logger.error("Tried to post the blank-site-start view when a user account already exists.")
                messages.error(request, "Whoops! It looks like someone's already created the first user account. Please log in.")
                return redirect('auth-login')

            return super().post(request)

    def form_valid(self, form):
        form.save()
        user = authenticate(username=self.request.POST['username'], password=self.request.POST['password1'])
        login(self.request, user)
        messages.success(self.request, "Welcome! You've created an account for %s." % user.username)

        return super().form_valid(form)


class CreateTournamentView(SuperuserRequiredMixin, CreateView):
    """This view allows a logged-in superuser to create a new tournament."""

    model = Tournament
    form_class = TournamentForm
    template_name = "create_tournament.html"
