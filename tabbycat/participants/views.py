import json

from django.conf import settings
from django.contrib import messages
from django.forms.models import modelformset_factory
from django.http import JsonResponse
from django.views.generic.base import TemplateView, View

from adjallocation.models import DebateAdjudicator
from tournaments.mixins import PublicTournamentPageMixin
from utils.mixins import CacheMixin, SingleObjectByRandomisedUrlMixin, SingleObjectFromTournamentMixin, VueTableMixin
from utils.tables import TabbycatTableBuilder

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


class PublicParticipantsListView(PublicTournamentPageMixin, VueTableMixin, CacheMixin):

    public_page_preference = 'public_participants'
    page_title = 'Participants'
    page_emoji = '🚌'

    def get_tables(self):
        t = self.get_tournament()

        adjudicators = Adjudicator.objects.filter(tournament=t).select_related('institution')
        adjs_table = TabbycatTableBuilder(view=self, title="Adjudicators", sort_key="Name")
        adjs_table.add_adjudicator_columns(adjudicators)

        speakers = Speaker.objects.filter(team__tournament=t).select_related('team', 'team__institution')
        speakers_table = TabbycatTableBuilder(view=self, title="Speakers", sort_key="Name")
        speakers_table.add_speaker_columns(speakers)
        speakers_table.add_team_columns([speaker.team for speaker in speakers])

        return [adjs_table, speakers_table]


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
