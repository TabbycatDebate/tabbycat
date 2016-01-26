from utils.views import *
from .models import Tournament, Division
from participants.models import Team, Institution
from draw.models import Debate, DebateTeam
from draw.models import TeamVenuePreference, InstitutionVenuePreference
from venues.models import VenueGroup

@cache_page(10) # Set slower to show new indexes so it will show new pages
@tournament_view
def public_index(request, t):
    return r2r(request, 'public_tournament_index.html')

def index(request):
    tournaments = Tournament.objects.all()
    if tournaments.count() == 1:
        print('user is ', request.user)
        if request.user.is_authenticated():
            print('tournament_home')
            return redirect_tournament('tournament_home', tournaments.first())
        else:
            print('public_index')
            return redirect_tournament('public_index', tournaments.first())
    else:
        return r2r(request, 'site_index.html', dict(tournaments=Tournament.objects.all()))

@login_required
@tournament_view
def tournament_home(request, t):
    round = t.current_round
    # This should never happen, but if it does, fail semi-gracefully
    if round is None:
        if request.user.is_superuser:
            return HttpResponseBadRequest("You need to set the current round. <a href=\"/admin/debate/tournament\">Go to Django admin.</a>")
        else:
            raise Http404()

    rounds = t.prelim_rounds(until=round).order_by('seq')

    # Draw Status
    draw = round.get_draw()
    total_ballots = draw.count()
    stats_none = draw.filter(result_status=Debate.STATUS_NONE).count()
    stats_draft = draw.filter(result_status=Debate.STATUS_DRAFT).count()
    stats_confirmed = draw.filter(result_status=Debate.STATUS_CONFIRMED).count()
    stats = [[0,stats_confirmed], [0,stats_draft], [0,stats_none]]

    return r2r(request, 'tournament_home.html', dict(stats=stats,
        total_ballots=total_ballots, round=round))

@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@public_optional_tournament_view('public_divisions')
def public_divisions(request, t):
    divisions = Division.objects.filter(tournament=t).all().select_related('venue_group')
    divisions = sorted(divisions, key=lambda x: float(x.name))
    venue_groups = set(d.venue_group for d in divisions)
    for uvg in venue_groups:
        uvg.divisions = [d for d in divisions if d.venue_group == uvg]

    return r2r(request, 'public_divisions.html', dict(venue_groups=venue_groups))

@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@tournament_view
def all_tournaments_all_venues(request, t):
    venues = VenueGroup.objects.all()
    return r2r(request, 'public_all_tournament_venues.html', dict(venues=venues))

@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@tournament_view
def all_draws_for_venue(request, t, venue_id):
    venue_group = VenueGroup.objects.get(pk=venue_id)
    debates = Debate.objects.filter(division__venue_group=venue_group).select_related(
        'round','round__tournament','division')
    return r2r(request, 'public_all_draws_for_venue.html', dict(
        venue_group=venue_group, debates=debates))


@tournament_view
def all_draws_for_institution(request, t, institution_id):
    # TODO: move to draws app
    institution = Institution.objects.get(pk=institution_id)
    debate_teams = DebateTeam.objects.filter(team__institution=institution).select_related(
        'debate', 'debate__division', 'debate__division__venue_group', 'debate__round')
    debates = [dt.debate for dt in debate_teams]

    return r2r(request, 'public_all_draws_for_institution.html', dict(
        institution=institution, debates=debates))



@admin_required
@round_view
def round_increment_check(request, round):
    if round != request.tournament.current_round: # doesn't make sense if not current round
        raise Http404()
    num_unconfirmed = round.get_draw().filter(result_status__in=[Debate.STATUS_NONE, Debate.STATUS_DRAFT]).count()
    increment_ok = num_unconfirmed == 0
    return r2r(request, "round_increment_check.html", dict(num_unconfirmed=num_unconfirmed, increment_ok=increment_ok))

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

    return r2r(request, "division_allocations.html", dict(teams=teams, divisions=divisions, venue_groups=venue_groups))


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

