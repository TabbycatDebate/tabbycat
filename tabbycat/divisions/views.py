import json
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.cache import cache_page

from participants.models import Institution, Team
from utils.views import admin_required, expect_post, public_optional_tournament_view, tournament_view
from utils.misc import redirect_tournament
from venues.models import InstitutionVenueConstraint, TeamVenueConstraint, VenueGroup

from .division_allocator import DivisionAllocator
from .models import Division

User = get_user_model()
logger = logging.getLogger(__name__)


@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@public_optional_tournament_view('public_divisions')
def public_divisions(request, t):
    divisions = Division.objects.filter(tournament=t).all().select_related('venue_group')
    divisions = sorted(divisions, key=lambda x: x.name)
    if len(divisions) > 0:
        venue_groups = set(d.venue_group for d in divisions)
        for uvg in venue_groups:
            uvg.divisions = [d for d in divisions if d.venue_group == uvg]
    else:
        venue_groups = None
        messages.success(request, 'No divisions have been assigned yet.')

    return render(request, 'public_divisions.html', dict(venue_groups=venue_groups))


@admin_required
@tournament_view
def division_allocations(request, t):
    # Should be a JsonDataResponseView
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
def create_division(request, t):
    division = Division.objects.create(name="temporary_name", tournament=t)
    division.save()
    division.name = "%s" % division.id
    division.save()
    return redirect_tournament('division_allocations', t)


@admin_required
@tournament_view
def create_division_allocation(request, t):

    teams = list(Team.objects.filter(tournament=t))
    institutions = Institution.objects.all()
    venue_groups = VenueGroup.objects.all()

    # Delete all existing divisions - this shouldn't affect teams (on_delete=models.SET_NULL))
    divisions = Division.objects.filter(tournament=t).delete()

    alloc = DivisionAllocator(teams=teams, divisions=divisions,
                              venue_groups=venue_groups, tournament=t,
                              institutions=institutions)
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
        print("set division to none for", team.short_name)
    else:
        team.division = Division.objects.get(pk=int(request.POST['division']))
        print("saved divison for ", team.short_name)

    team.save()
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
