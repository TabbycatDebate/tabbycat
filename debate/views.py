from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import Context, RequestContext, loader, Template
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count

from results.result import BallotSet
from debate.keys import populate_url_keys

from debate.models import *
from allocations.models import DebateAdjudicator
from venues.models import VenueGroup, Venue
from motions.models import Motion
from draws.models import Debate
from action_log.models import ActionLog

from debate import forms
from django.forms.models import modelformset_factory, formset_factory
from django.forms import Textarea

import json

from utils import *

def index(request):
    tournaments = Tournament.objects.all()
    if request.user.is_authenticated():
        return r2r(request, 'site_index.html', dict(tournaments=Tournament.objects.all()))
    elif len(tournaments) == 1:
        sole_tournament = list(tournaments)[0]
        return redirect_tournament('public_index', sole_tournament)
    else:
        return r2r(request, 'site_index.html', dict(tournaments=Tournament.objects.all()))

## Public UI

@cache_page(settings.TAB_PAGES_CACHE_TIMEOUT)
@tournament_view
def team_speakers(request, t, team_id):
    from django.http import JsonResponse
    team = Team.objects.get(pk=team_id)
    speakers = team.speakers
    data = {}
    for i, speaker in enumerate(speakers):
        data[i] = speaker.name

    return JsonResponse(data, safe=False)


@cache_page(10) # Set slower to show new indexes so it will show new pages
@tournament_view
def public_index(request, t):
    return r2r(request, 'public/public_tournament_index.html')


@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@public_optional_tournament_view('public_participants')
def public_participants(request, t):
    adjs = Adjudicator.objects.all()
    speakers = Speaker.objects.all().select_related('team','team__institution')
    return r2r(request, "public/public_participants.html", dict(adjs=adjs, speakers=speakers))



@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@public_optional_tournament_view('public_divisions')
def public_divisions(request, t):
    divisions = Division.objects.filter(tournament=t).all().select_related('venue_group')
    divisions = sorted(divisions, key=lambda x: float(x.name))
    venue_groups = set(d.venue_group for d in divisions)
    for uvg in venue_groups:
        uvg.divisions = [d for d in divisions if d.venue_group == uvg]

    return r2r(request, 'public/public_divisions.html', dict(venue_groups=venue_groups))

@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@tournament_view
def all_tournaments_all_venues(request, t):
    venues = VenueGroup.objects.all()
    return r2r(request, 'public/public_all_tournament_venues.html', dict(venues=venues))

@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@tournament_view
def all_draws_for_venue(request, t, venue_id):
    venue_group = VenueGroup.objects.get(pk=venue_id)
    debates = Debate.objects.filter(division__venue_group=venue_group).select_related(
        'round','round__tournament','division')
    return r2r(request, 'public/public_all_draws_for_venue.html', dict(
        venue_group=venue_group, debates=debates))

@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@tournament_view
def all_tournaments_all_institutions(request, t):
    institutions = Institution.objects.all()
    return r2r(request, 'public/public_all_tournament_institutions.html', dict(
        institutions=institutions))

@tournament_view
def all_draws_for_institution(request, t, institution_id):
    # TODO: move to draws app
    institution = Institution.objects.get(pk=institution_id)
    debate_teams = DebateTeam.objects.filter(team__institution=institution).select_related(
        'debate', 'debate__division', 'debate__division__venue_group', 'debate__round')
    debates = [dt.debate for dt in debate_teams]

    return r2r(request, 'public/public_all_draws_for_institution.html', dict(
        institution=institution, debates=debates))

@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@tournament_view
def all_tournaments_all_teams(request, t):
    teams = Team.objects.filter(tournament__active=True).select_related('tournament').prefetch_related('division')
    return r2r(request, 'public/public_all_tournament_teams.html', dict(
        teams=teams))



## Tab

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



@admin_required
@round_view
def round_index(request, round):
    return r2r(request, 'round_index.html')

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


# public (for barcode checkins)
@round_view
def checkin(request, round):
    context = {}
    if request.method == 'POST':
        v = request.POST.get('barcode_id')
        try:
            barcode_id = int(v)
            p = Person.objects.get(barcode_id=barcode_id)
            ch, created = Checkin.objects.get_or_create(
                person = p,
                round = round
            )
            context['person'] = p

        except (ValueError, Person.DoesNotExist):
            context['unknown_id'] = v

    return r2r(request, 'checkin.html', context)


@admin_required
@tournament_view
def division_allocations(request, t):
    teams = Team.objects.filter(tournament=t).all()
    divisions = Division.objects.filter(tournament=t).all()
    divisions = sorted(divisions, key=lambda x: float(x.name))
    venue_groups = VenueGroup.objects.all()

    return r2r(request, "division_allocation.html", dict(teams=teams, divisions=divisions, venue_groups=venue_groups))


@admin_required
@expect_post
@tournament_view
def save_divisions(request, t):
    culled_dict = dict((int(k), int(v)) for k, v in request.POST.iteritems() if v)

    teams = Team.objects.in_bulk([t_id for t_id in culled_dict.keys()])
    divisions = Division.objects.in_bulk([d_id for d_id in culled_dict.values()])

    for team_id, division_id in culled_dict.iteritems():
        teams[team_id].division = divisions[division_id]
        teams[team_id].save()

    # ActionLog.objects.log(type=ActionLog.ACTION_TYPE_DIVISIONS_SAVE,
    #     user=request.user, tournament=t)

    return HttpResponse("ok")

@admin_required
@expect_post
@tournament_view
def create_division_allocation(request, t):
    from debate.division_allocator import DivisionAllocator

    teams = list(Team.objects.filter(tournament=t))
    for team in teams:
        preferences = list(TeamVenuePreference.objects.filter(team=team))
        team.preferences_dict = dict((p.priority, p.venue_group) for p in preferences)

    # Delete all existing divisions - this shouldn't affect teams (on_delete=models.SET_NULL))
    divisions = Division.objects.filter(tournament=t).delete()

    venue_groups = VenueGroup.objects.all()

    alloc = DivisionAllocator(teams=teams, divisions=divisions,venue_groups=venue_groups, tournament=t)
    success = alloc.allocate()

    if success:
        return HttpResponse("ok")
    else:
        return HttpResponseBadRequest("Couldn't create divisions")


@admin_required
@tournament_view
def randomised_urls(request, t):
    context = dict()
    context['teams'] = t.team_set.all()
    context['adjs'] = t.adjudicator_set.all()
    context['exists'] = t.adjudicator_set.filter(url_key__isnull=False).exists() or \
            t.team_set.filter(url_key__isnull=False).exists()
    context['tournament_slug'] = t.slug
    context['ballot_normal_urls_enabled'] = t.config.get('public_ballots')
    context['ballot_randomised_urls_enabled'] = t.config.get('public_ballots_randomised')
    context['feedback_normal_urls_enabled'] = t.config.get('public_feedback')
    context['feedback_randomised_urls_enabled'] = t.config.get('public_feedback_randomised')
    return r2r(request, 'randomised_urls.html', context)

@admin_required
@tournament_view
@expect_post
def generate_randomised_urls(request, t):
    # Only works if there are no randomised URLs now
    if t.adjudicator_set.filter(url_key__isnull=False).exists() or \
            t.team_set.filter(url_key__isnull=False).exists():
        return HttpResponseBadRequest("There are already randomised URLs. You must use the Django management commands to populate or delete randomised URLs.")

    populate_url_keys(t.adjudicator_set.all())
    populate_url_keys(t.team_set.all())
    return redirect_tournament('randomised_urls', t)