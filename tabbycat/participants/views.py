import json

from django.conf import settings
from django.contrib import messages
from django.forms.models import modelformset_factory
from django.http import JsonResponse
from django.views.generic.base import TemplateView, View

from adjallocation.models import DebateAdjudicator
from tournaments.mixins import PublicTournamentPageMixin, TournamentMixin
from utils.misc import reverse_tournament
from utils.mixins import CacheMixin, HeadlessTemplateView, SingleObjectByRandomisedUrlMixin, SingleObjectFromTournamentMixin, VueTableMixin

from .models import Adjudicator, Institution, Speaker, Team


class TeamSpeakersJsonView(CacheMixin, SingleObjectFromTournamentMixin, View):

    model = Team
    pk_url_kwarg = 'team_id'
    cache_timeout = settings.TAB_PAGES_CACHE_TIMEOUT

    def get(self, request, *args, **kwargs):
        team = self.get_object()
        speakers = team.speakers
        data = {i: "<li>" + speaker.name + "</li>" for i, speaker in enumerate(speakers)}
        return JsonResponse(data, safe=False)


class PublicParticipantsListView(PublicTournamentPageMixin, VueTableMixin, CacheMixin, HeadlessTemplateView):

    public_page_preference = 'public_participants'
    template_name = 'base_double_vue_table.html'
    page_title = 'Participants'
    page_emoji = '🚌'
    sort_key = 'Name'

    def get_context_data(self, **kwargs):
        t = self.get_tournament()

        adjs_data = []
        adjudicators = t.adjudicator_set.select_related('institution')
        for adjudicator in adjudicators:
            ddict = self.adj_cells(adjudicator, t)
            if t.pref('public_summary'):
                ddict[0]['cell']['link'] = reverse_tournament('participants-public-adjudicator-summary',
                        t, kwargs={'pk': adjudicator.pk})
            adjs_data.append(ddict)

        kwargs["table_a_title"] = "Adjudicators"
        kwargs["tableDataA"] = json.dumps(adjs_data)

        speakers_data = []
        speakers = Speaker.objects.filter(team__tournament=t).select_related('team', 'team__institution')
        for speaker in speakers:
            ddict = self.speaker_cells(speaker, t)
            team_cell_index = len(ddict)
            ddict.extend(self.team_cells(speaker.team, t))
            if t.pref('public_summary'):
                ddict[team_cell_index]['cell']['link'] = reverse_tournament('participants-public-team-summary',
                        t, kwargs={'pk': speaker.team.pk})
            speakers_data.append(ddict)

        kwargs["table_b_title"] = "Speakers"
        kwargs["tableDataB"] = json.dumps(speakers_data)

        return super().get_context_data(**kwargs)


# ==============================================================================
# Team and adjudicator summary pages
# ==============================================================================

class ParticipantsListView(TournamentMixin, VueTableMixin, TemplateView):

    template_name = 'base_double_vue_table.html'
    page_title = 'Team and Adjudicator Summary Pages'
    page_emoji = '🌸'
    sort_key = 'Name'

    def get_context_data(self, **kwargs):
        t = self.get_tournament()

        adjs_data = []
        adjudicators = t.adjudicator_set.select_related('institution')
        for adj in adjudicators:
            ddict = self.adj_cells(adj, t)
            ddict[0]['cell']['link'] = reverse_tournament('participants-adjudicator-summary',
                    t, kwargs={'pk': adj.pk})
            adjs_data.append(ddict)

        kwargs["table_a_title"] = "Adjudicators"
        kwargs["tableDataA"] = json.dumps(adjs_data)

        teams_data = []
        teams = t.team_set.select_related('institution')
        for team in teams:
            ddict = self.team_cells(team, t, key='Name')
            ddict[0]['cell']['link'] = reverse_tournament('participants-team-summary',
                    t, kwargs={'pk': team.pk})
            teams_data.append(ddict)

        kwargs["table_b_title"] = "Teams"
        kwargs["tableDataB"] = json.dumps(teams_data)

        return super().get_context_data(**kwargs)

class BaseSummaryView(SingleObjectFromTournamentMixin, VueTableMixin, TemplateView):

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)


class TeamSummaryView(BaseSummaryView):

    model = Team
    template_name = 'team_summary.html'


class AdjudicatorSummaryView(BaseSummaryView):

    model = Adjudicator
    template_name = 'adjudicator_summary.html'


class PublicTeamSummaryView(PublicTournamentPageMixin, TeamSummaryView):
    public_page_preference = 'public_summary'


class PublicAdjudicatorSummaryView(PublicTournamentPageMixin, AdjudicatorSummaryView):
    public_page_preference = 'public_summary'


# ==============================================================================
# Cross-tournament views
# ==============================================================================

class AllTournamentsAllInstitutionsView(PublicTournamentPageMixin, CacheMixin, TemplateView):
    public_page_preference = 'enable_mass_draws'
    template_name = 'public_all_tournament_institutions.html'

    def get_context_data(self, **kwargs):
        kwargs['institutions'] = Institution.objects.all()
        return super().get_context_data(**kwargs)


class AllTournamentsAllTeamsView(PublicTournamentPageMixin, CacheMixin, TemplateView):
    public_page_preference = 'enable_mass_draws'
    template_name = 'public_all_tournament_teams.html'

    def get_context_data(self, **kwargs):
        kwargs['teams'] = Team.objects.filter(tournament__active=True).select_related('tournament').prefetch_related('division')
        return super().get_context_data(**kwargs)


# ==============================================================================
# Shift scheduling
# ==============================================================================

class PublicConfirmShiftView(SingleObjectByRandomisedUrlMixin, PublicTournamentPageMixin, TemplateView):
    # Django doesn't have a class-based view for form sets, so this implements
    # the form processing analogously to FormView, with less decomposition.

    public_page_preference = 'allocation_confirmations'
    template_name = 'confirm_shifts.html'
    model = Adjudicator

    def get_formset(self):
        ShiftFormSet = modelformset_factory(DebateAdjudicator, can_delete=False, # flake8: noqa
                extra=0, fields=['timing_confirmed'])

        if self.request.method in ('POST', 'PUT'):
            return ShiftFormSet(data=self.request.POST, files=self.request.FILES)
        elif self.request.method == 'GET':
            debateadjs = DebateAdjudicator.objects.filter(adjudicator=self.get_object())
            return ShiftFormSet(queryset=debateadjs)

    def get_context_data(self, **kwargs):
        kwargs['adjudicator'] = self.get_object()
        kwargs['formset'] = self.get_formset()
        return super().get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        formset = self.get_formset()
        if formset.is_valid():
            formset.save()
            messages.success(request, "Your shift check-ins have been saved")
        return super().get(request, *args, **kwargs) # then render form as usual (don't call super().post())

    def put(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
