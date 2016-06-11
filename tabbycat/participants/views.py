import json
from collections import OrderedDict

from django.conf import settings
from django.contrib import messages
from django.forms.models import modelformset_factory
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.cache import cache_page
from django.views.generic.base import View, TemplateView

from adjallocation.models import DebateAdjudicator
from tournaments.mixins import TournamentMixin, PublicTournamentPageMixin
from utils.views import public_optional_tournament_view, tournament_view
from utils.mixins import HeadlessTemplateView, CacheMixin, VueTableMixin, SingleObjectFromTournamentMixin, SingleObjectByRandomisedUrlMixin

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

    def get_context_data(self, **kwargs):
        t = self.get_tournament()

        adjs_data = []
        adjudicators = Adjudicator.objects.filter(tournament=t).select_related('institution')
        for adjudicator in adjudicators:
            ddict = self.adj_cells(adjudicator, t)
            adjs_data.append(OrderedDict(ddict))

        kwargs["table_a_title"] = "Adjudicators"
        kwargs["tableDataA"] = json.dumps(adjs_data)

        speakers_data = []
        speakers = Speaker.objects.filter(team__tournament=t).select_related('team', 'team__institution')
        for speaker in speakers:
            ddict.extend(self.speaker_cells(speaker, t))
            ddict.extend(self.team_cells(speaker.team, t))
            # if t.pref('public_break_categories'):
            #     ddict.append(('Break Categories', s.team.break_categories_nongeneral ))
            speakers_data.append(OrderedDict(ddict))

        kwargs["table_b_title"] = "Speakers"
        kwargs["tableDataB"] = json.dumps(speakers_data)

        return super().get_context_data(**kwargs)


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


# Scheduling


class PublicConfirmShiftView(SingleObjectByRandomisedUrlMixin, PublicTournamentPageMixin, TemplateView):
    # Django doesn't have a class-based view for form sets, so this implements
    # the form processing analogously to FormView, with less decomposition.

    public_page_preference = 'allocation_confirmations'
    template_name = 'confirm_shifts.html'
    model = Adjudicator

    def get_formset(self):
        ShiftFormSet = modelformset_factory(DebateAdjudicator, can_delete=False,
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

