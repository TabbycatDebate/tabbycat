import logging
logger = logging.getLogger(__name__)
from threading import Lock

from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import FormView, CreateView
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
import django.contrib.messages as messages

from utils.views import *
from .models import Tournament, Division
from .forms import TournamentForm
from utils.forms import SuperuserCreationForm
from participants.models import Team, Institution
from draw.models import Debate, DebateTeam
from draw.models import TeamVenuePreference, InstitutionVenuePreference
from venues.models import VenueGroup

@cache_page(10) # Set slower to show new indexes so it will show new pages
@tournament_view
def public_index(request, t):
    return render(request, 'public_tournament_index.html')

def index(request):
    tournaments = Tournament.objects.all()
    if tournaments.count() == 1:
        logger.info('One tournament only, user is: %s', request.user)
        if request.user.is_authenticated():
            logger.info('Redirecting to tournament-admin-home')
            return redirect_tournament('tournament-admin-home', tournaments.first())
        else:
            logger.info('Redirecting to tournament-public-index')
            return redirect_tournament('tournament-public-index', tournaments.first())

    elif not tournaments.exists() and not User.objects.exists():
        logger.info('No users and no tournaments, redirecting to blank-site-start')
        return redirect('blank-site-start')

    else:
        return render(request, 'site_index.html', dict(tournaments=tournaments))

@login_required
@tournament_view
def tournament_home(request, t):
    round = t.current_round
    # This should never happen, but if it does, fail semi-gracefully
    if round is None:
        if request.user.is_superuser:
            return HttpResponseBadRequest("You need to set the current round. <a href=\"/admin/tournaments/tournament\">Go to Django admin.</a>")
        else:
            raise Http404()

    context = {}

    context["round"] = round
    context["readthedocs_version"] = settings.READTHEDOCS_VERSION

    # If the tournament is blank, display a message on the page
    context["blank"] = not (t.team_set.exists() or t.adjudicator_set.exists() or t.venue_set.exists())

    # Draw Status
    draw = round.get_draw()
    context["total_ballots"] = draw.count()
    stats_none = draw.filter(result_status=Debate.STATUS_NONE).count()
    stats_draft = draw.filter(result_status=Debate.STATUS_DRAFT).count()
    stats_confirmed = draw.filter(result_status=Debate.STATUS_CONFIRMED).count()
    context["stats"] = [[0,stats_confirmed], [0,stats_draft], [0,stats_none]]

    return render(request, 'tournament_home.html', context)

@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@public_optional_tournament_view('public_divisions')
def public_divisions(request, t):
    divisions = Division.objects.filter(tournament=t).all().select_related('venue_group')
    divisions = sorted(divisions, key=lambda x: float(x.name))
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
    if round != request.tournament.current_round: # doesn't make sense if not current round
        raise Http404()
    num_unconfirmed = round.get_draw().filter(result_status__in=[Debate.STATUS_NONE, Debate.STATUS_DRAFT]).count()
    increment_ok = num_unconfirmed == 0
    return render(request, "round_increment_check.html", dict(num_unconfirmed=num_unconfirmed, increment_ok=increment_ok))

@admin_required
@expect_post
@round_view
def round_increment(request, round):
    if round != request.tournament.current_round: # doesn't make sense if not current round
        raise Http404()
    request.tournament.advance_round()
    return redirect_round('draw', request.tournament.current_round )

@admin_required
@tournament_view
def division_allocations(request, t):
    teams = Team.objects.filter(tournament=t).all()
    divisions = Division.objects.filter(tournament=t).all()
    divisions = sorted(divisions, key=lambda x: float(x.name))
    venue_groups = VenueGroup.objects.all()

    return render(request, "division_allocations.html", dict(teams=teams, divisions=divisions, venue_groups=venue_groups))


@admin_required
@expect_post
@tournament_view
def save_divisions(request, t):
    culled_dict = dict((int(k), int(v)) for k, v in request.POST.items() if v)

    teams = Team.objects.in_bulk([t_id for t_id in list(culled_dict.keys())])
    divisions = Division.objects.in_bulk([d_id for d_id in list(culled_dict.values())])

    for team_id, division_id in culled_dict.items():
        teams[team_id].division = divisions[division_id]
        teams[team_id].save()

    # ActionLog.objects.log(type=ActionLog.ACTION_TYPE_DIVISIONS_SAVE,
    #     user=request.user, tournament=t)

    return HttpResponse("ok")

@admin_required
@expect_post
@tournament_view
def create_division_allocation(request, t):
    from tournaments.division_allocator import DivisionAllocator

    teams = list(Team.objects.filter(tournament=t))
    institutions = Institution.objects.all()
    venue_groups = VenueGroup.objects.all()

    # Delete all existing divisions - this shouldn't affect teams (on_delete=models.SET_NULL))
    divisions = Division.objects.filter(tournament=t).delete()

    alloc = DivisionAllocator(teams=teams, divisions=divisions, venue_groups=venue_groups, tournament=t, institutions=institutions)
    success = alloc.allocate()

    if success:
        return HttpResponse("ok")
    else:
        return HttpResponseBadRequest("Couldn't create divisions")


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

        return super(BlankSiteStartView, self).get(request)

    def post(self, request):
        form = self.form_class(request.POST)
        with self.lock:
            if User.objects.exists():
                logger.error("Tried to post the blank-site-start view when a user account already exists.")
                messages.error(request, "Whoops! It looks like someone's already created the first user account. Please log in.")
                return redirect('auth-login')

            return super(BlankSiteStartView, self).post(request)

    def form_valid(self, form):
        form.save()
        user = authenticate(username=self.request.POST['username'], password=self.request.POST['password1'])
        login(self.request, user)
        messages.success(self.request, "Welcome! You've created an account for %s." % user.username)

        return super(BlankSiteStartView, self).form_valid(form)

class CreateTournamentView(SuperuserRequiredMixin, CreateView):
    """This view allows a logged-in superuser to create a new tournament."""

    model = Tournament
    form_class = TournamentForm
    template_name = "create_tournament.html"
