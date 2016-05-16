import json
from collections import OrderedDict

from django.http import JsonResponse
from django.forms.models import modelformset_factory

from .models import Adjudicator, Speaker, Institution, Team
from adjallocation.models import DebateAdjudicator

from utils.views import *
from utils.mixins import PublicCacheMixin, VueTableMixin, HeadlessTemplateView
from tournaments.mixins import PublicTournamentPageMixin

@cache_page(settings.TAB_PAGES_CACHE_TIMEOUT)
@tournament_view
def team_speakers(request, t, team_id):
    team = Team.objects.get(pk=team_id)
    speakers = team.speakers
    data = {}
    for i, speaker in enumerate(speakers):
        data[i] = "<li>" + speaker.name + "</li>"

    return JsonResponse(data, safe=False)


class PublicParticipants(PublicTournamentPageMixin, VueTableMixin, PublicCacheMixin, HeadlessTemplateView):

    public_page_preference = 'public_participants'
    template_name = 'base_double_vue_table.html'
    page_title = 'Participants'
    page_emoji = '🚌'

    def get_context_data(self, **kwargs):
        t = self.get_tournament()

        adjs_data = []
        adjs = Adjudicator.objects.filter(tournament=t).select_related('institution')
        for a in adjs:
            ddict = [('Name', a.name )]
            if a.adj_core:
                institution = "Independent / " + a.institution.name
            elif a.independent:
                institution = "Independent / " + a.institution.name
            else:
                institution = a.institution.name

            ddict.append(('Institution', institution ))
            adjs_data.append(OrderedDict(ddict))

        kwargs["table_a_title"] = "Adjudicators"
        kwargs["tableDataA"] = json.dumps(adjs_data)

        speakers_data = []
        speakers = Speaker.objects.filter(team__tournament=t).select_related('team','team__institution')
        for speaker in speakers:
            ddict.extend(self.speaker_cells(speaker, t))
            ddict.extend(self.team_cells(speaker.team, t))
            # if t.pref('public_break_categories'):
            #     ddict.append(('Break Categories', s.team.break_categories_nongeneral ))
            speakers_data.append(OrderedDict(ddict))

        kwargs["table_b_title"] = "Speakers"
        kwargs["tableDataB"] = json.dumps(speakers_data)

        return super().get_context_data(**kwargs)


@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@tournament_view
def all_tournaments_all_institutions(request, t):
    institutions = Institution.objects.all()
    return render(request, 'public_all_tournament_institutions.html', dict(
        institutions=institutions))


@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@tournament_view
def all_tournaments_all_teams(request, t):
    teams = Team.objects.filter(tournament__active=True).select_related('tournament').prefetch_related('division')
    return render(request, 'public_all_tournament_teams.html', dict(
        teams=teams))


# Scheduling

@public_optional_tournament_view('allocation_confirmations')
def public_confirm_shift_key(request, t, url_key):
    adj = get_object_or_404(Adjudicator, url_key=url_key)
    adj_debates = DebateAdjudicator.objects.filter(adjudicator=adj)

    ShiftsFormset = modelformset_factory(DebateAdjudicator,
        can_delete=False, extra=0, fields=['timing_confirmed'])

    if request.method == 'POST':
        formset = ShiftsFormset(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            messages.success(request, "Your shift check-ins have been saved")
    else:
        formset = ShiftsFormset(queryset=adj_debates)

    return render(request, 'confirm_shifts.html', dict(formset=formset, adjudicator=adj))
