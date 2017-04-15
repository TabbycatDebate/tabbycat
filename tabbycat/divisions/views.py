import json
import logging

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db import models
from django.http import HttpResponse
from django.views.generic.base import TemplateView, View

from participants.models import Institution, Team
from tournaments.mixins import PublicTournamentPageMixin, TournamentMixin
from utils.mixins import CacheMixin, PostOnlyRedirectView, SuperuserRequiredMixin
from venues.models import VenueCategory, VenueConstraint

from .division_allocator import DivisionAllocator
from .models import Division

User = get_user_model()
logger = logging.getLogger(__name__)


class PublicDivisionsView(PublicTournamentPageMixin, CacheMixin, TemplateView):
    public_page_preference = 'public_divisions'
    template_name = "public_divisions.html"

    def get_context_data(self, **kwargs):
        t = self.get_tournament()
        divisions = Division.objects.filter(tournament=t).all().select_related('venue_category')
        divisions = sorted(divisions, key=lambda x: x.name)
        if len(divisions) > 0:
            venue_categories = set(d.venue_category for d in divisions)
            for uvc in venue_categories:
                uvc.divisions = [d for d in divisions if d.venue_category == uvc]
            kwargs["venue_categories"] = venue_categories
        else:
            kwargs["round"] = None
            messages.success(self.request, 'No divisions have been assigned yet.')
        return super().get_context_data(**kwargs)


class DivisionsAllocatorView(SuperuserRequiredMixin, TournamentMixin, TemplateView):
    template_name = "division_allocations.html"

    def get_context_data(self, **kwargs):
        t = self.get_tournament()
        teams = Team.objects.filter(tournament=t).all()
        teams_json = list(teams.values('id', 'short_reference', 'division',
            'use_institution_prefix', 'institution__code', 'institution__id'))

        # Build a per-team list of all the relevant institutional/team constraints
        for team, team_dict in zip(teams, teams_json):
            team_preferences = VenueConstraint.objects.filter(
                models.Q(team=team)).order_by('-priority')
            team_dict['team_preferences'] = list(
                team_preferences.values('category__name', 'priority'))

            institutional_preferences = VenueConstraint.objects.filter(
                models.Q(institution=team.institution)).order_by('-priority')
            team_dict['institutional_preferences'] = list(
                institutional_preferences.values('category__name', 'priority'))

        venue_categories = []
        for vc in VenueCategory.objects.all():
            venue_categories.append({
                'id': vc.id,
                'name': vc.name,
                'total_capacity': vc.venues.count()})

        kwargs["teams"] = json.dumps(teams_json)
        divisions = Division.objects.filter(tournament=t).all()
        kwargs["divisions"] = json.dumps(list(divisions.values(
            'id', 'name', 'venue_category', 'venue_category__name')))
        kwargs["venue_categories"] = json.dumps(venue_categories)

        return super().get_context_data(**kwargs)


class CreateByesView(SuperuserRequiredMixin, TournamentMixin, PostOnlyRedirectView):
    tournament_redirect_pattern_name = 'division_allocations'

    def post(self, request, *args, **kwargs):
        t = self.get_tournament()
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
        return super().post(request, *args, **kwargs)


class CreateDivisionView(SuperuserRequiredMixin, TournamentMixin, PostOnlyRedirectView):
    tournament_redirect_pattern_name = 'division_allocations'

    def post(self, request, *args, **kwargs):
        t = self.get_tournament()
        division = Division.objects.create(name="temporary_name", tournament=t)
        division.save()
        division.name = "%s" % division.id
        division.save()
        return super().post(request, *args, **kwargs)


class CreateDivisionAllocationView(SuperuserRequiredMixin, TournamentMixin, PostOnlyRedirectView):
    tournament_redirect_pattern_name = 'division_allocations'

    def post(self, request, *args, **kwargs):
        t = self.get_tournament()
        teams = list(Team.objects.filter(tournament=t))
        institutions = Institution.objects.all()
        venue_categories = VenueCategory.objects.all()

        # Delete all existing divisions - this shouldn't affect teams (on_delete=models.SET_NULL))
        divisions = Division.objects.filter(tournament=t).delete()

        alloc = DivisionAllocator(teams=teams, divisions=divisions,
                                  venue_categories=venue_categories, tournament=t,
                                  institutions=institutions)
        alloc.allocate()

        return super().post(request, *args, **kwargs)


class SetDivisionVenueCategoryView(TournamentMixin, SuperuserRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        division = Division.objects.get(pk=int(self.request.POST['division']))
        if self.request.POST['venueCategory'] == '':
            division.venue_category = None
        else:
            division.venue_category = VenueCategory.objects.get(pk=int(self.request.POST['venueCategory']))

        print("saved venue cat for for", division.name)
        division.save()
        return HttpResponse()


class SetTeamDivisionView(TournamentMixin, SuperuserRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        team = Team.objects.get(pk=int(self.request.POST['team']))
        if self.request.POST['division'] == '':
            team.division = None
            print("set division to none for", team.short_name)
        else:
            team.division = Division.objects.get(pk=int(self.request.POST['division']))
            print("saved divison for ", team.short_name)

        team.save()
        return HttpResponse()


class SetDivisionTimeView(TournamentMixin, SuperuserRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        division = Division.objects.get(pk=int(self.request.POST['division']))
        if self.request.POST['division'] == '':
            division = None
        else:
            division.time_slot = self.request.POST['time']
            division.save()
        return HttpResponse()
