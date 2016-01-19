from django.http import JsonResponse
from django.forms.models import modelformset_factory
from utils.views import *
from .models import Adjudicator, Speaker, Institution, Team
from adjallocation.models import DebateAdjudicator

@cache_page(settings.TAB_PAGES_CACHE_TIMEOUT)
@tournament_view
def team_speakers(request, t, team_id):
    team = Team.objects.get(pk=team_id)
    speakers = team.speakers
    data = {}
    for i, speaker in enumerate(speakers):
        data[i] = speaker.name

    return JsonResponse(data, safe=False)

@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@public_optional_tournament_view('public_participants')
def public_participants(request, t):
    adjs = Adjudicator.objects.all()
    speakers = Speaker.objects.all().select_related('team','team__institution')
    return r2r(request, "public_participants.html", dict(adjs=adjs, speakers=speakers))


@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@tournament_view
def all_tournaments_all_institutions(request, t):
    institutions = Institution.objects.all()
    return r2r(request, 'public_all_tournament_institutions.html', dict(
        institutions=institutions))


@cache_page(settings.PUBLIC_PAGE_CACHE_TIMEOUT)
@tournament_view
def all_tournaments_all_teams(request, t):
    teams = Team.objects.filter(tournament__active=True).select_related('tournament').prefetch_related('division')
    return r2r(request, 'public_all_tournament_teams.html', dict(
        teams=teams))


# Scheduling

@public_optional_tournament_view('allocation_confirmations')
def public_confirm_shift_key(request, t, url_key):
    adj = get_object_or_404(Adjudicator, tournament=t, url_key=url_key)
    adj_debates = DebateAdjudicator.objects.filter(adjudicator=adj)

    ShiftsFormset = modelformset_factory(DebateAdjudicator,
        can_delete=False, extra=0, fields=['timing_confirmed'])

    if request.method == 'POST':
        formset = ShiftsFormset(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            messages.success(request, "Your shift checkins have been saved")
    else:
        formset = ShiftsFormset(queryset=adj_debates)



    return r2r(request, 'confirm_shifts.html', dict(formset=formset, adjudicator=adj))

