from django.http import Http404, HttpResponseRedirect, HttpResponseForbidden, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from django.db.models import Sum, Count

from debate.models import Round, Debate, Team, Venue
from debate import forms

# Create your views here.

def index(request):
    return render_to_response('index.html', context_instance=RequestContext(request))

def venue_availability(request, round_id):
    return base_availability(request, round_id, 'venue', 'venues')

def update_venue_availability(request, round_id):
    return update_base_availability(request, round_id, 'set_available_venues')

def adjudicator_availability(request, round_id):
    return base_availability(request, round_id, 'adjudicator', 'adjudicators')

def update_adjudicator_availability(request, round_id):
    return update_base_availability(request, round_id, 'set_available_adjudicators')

def team_availability(request, round_id):
    return base_availability(request, round_id, 'team', 'teams')

def update_team_availability(request, round_id):
    return update_base_availability(request, round_id, 'set_available_teams')

def base_availability(request, round_id, model, context_name):
    rc = RequestContext(request)
    round = get_object_or_404(Round, id=round_id)

    items = getattr(round, '%s_availability' % model)().order_by('name')

    rc[context_name] = items 
    rc['round'] = round
    return render_to_response('%s_availability.html' % model,
                              context_instance=rc)

def update_base_availability(request, round_id, update_method):
    round = get_object_or_404(Round, id=round_id)

    if request.method != "POST":
        return HttpResponseBadRequest("expected POST")

    available_ids = [int(a.replace("check_", "")) for a in request.POST.keys()
                     if a.startswith("check_")]

    getattr(round, update_method)(available_ids)

    return HttpResponse("ok")

def draw(request, round_id):
    round = get_object_or_404(Round, id=round_id)
    rc = RequestContext(request)
    rc['round'] = round

    if round.draw_status == round.STATUS_NONE:
        return draw_none(request, round, rc)

    if round.draw_status == round.STATUS_DRAFT:
        return draw_draft(request, round, rc)

    if round.draw_status == round.STATUS_CONFIRMED:
        return draw_confirmed(request, round, rc)

    raise

def draw_none(request, round, rc):
    
    active_teams = round.active_teams.all()
    rc['active_teams'] = active_teams
    return render_to_response("draw_none.html", context_instance=rc)

def draw_draft(request, round, rc):
    rc['draw'] = round.get_draw()

    return render_to_response("draw_draft.html", context_instance=rc)

def draw_confirmed(request, round, rc):
    rc['draw'] = round.get_draw()

    return render_to_response("draw_confirmed.html", context_instance=rc)

def create_draw(request, round_id):
    round = get_object_or_404(Round, id=round_id)

    if request.method != "POST":
        return HttpResponseBadRequest("Expected POST")

    round.draw()

    return HttpResponseRedirect(reverse('draw', args=[round_id])) 

def confirm_draw(request, round_id):
    round = get_object_or_404(Round, id=round_id)

    if request.method != "POST":
        return HttpResponseBadRequest("Expected POST")
    if round.draw_status != round.STATUS_DRAFT:
        return HttpResponseBadRequest("Draw status is not DRAFT")

    round.draw_status = round.STATUS_CONFIRMED
    round.save()

    return HttpResponseRedirect(reverse('draw', args=[round_id])) 

def create_adj_allocation(request, round_id):
    round = get_object_or_404(Round, id=round_id)
    if request.method != "POST":
        return HttpResponseBadRequest("Expected POST")
    if round.draw_status != round.STATUS_CONFIRMED:
        return HttpResponseBadRequest("Draw is not confirmed")
    if round.adjudicator_status != round.STATUS_NONE:
        return HttpResponseBadRequest("Adj allocation is not NONE")

    round.allocate_adjudicators()

    return HttpResponseRedirect(reverse('draw', args=[round_id])) 

def results(request, round_id):
    round = get_object_or_404(Round, id=round_id)

    rc = RequestContext(request)
    rc['round'] = round
    rc['draw'] = round.get_draw()

    return render_to_response("results.html", context_instance=rc)

def enter_result(request, debate_id):
    debate = get_object_or_404(Debate, id=debate_id)

    rc = RequestContext(request)
    rc['debate'] = debate

    form = forms.make_results_form(debate)
    rc['form'] = form

    return render_to_response('enter_results.html', context_instance=rc)

def save_result(request, debate_id):
    if request.method != "POST":
        return HttpResponseBadRequest("Expected POST")

    debate = get_object_or_404(Debate, id=debate_id)

    rc = RequestContext(request)
    rc['debate'] = debate

    class_ = forms.make_results_form_class(debate)
    form = class_(request.POST)

    if form.is_valid():
        form.save()
    else:
        raise

    return HttpResponseRedirect(reverse('results', args=[debate.round.id]))

def team_standings(request, round_id):
    round = get_object_or_404(Round, id=round_id)

    rc = RequestContext(request)
    rc['round'] = round

    
    teams = Team.objects.annotate(
        team_points = Sum('debateteam__teamscore__points'),
        team_score = Sum('debateteam__teamscore__score'),
        results_count = Count('debateteam__teamscore'),
    ).order_by('-team_points', '-team_score')

    for team in teams:
        setattr(team, 'results_in', team.results_count >= round.seq)

    rc['teams'] = teams

    return render_to_response('team_standings.html', context_instance=rc)


def draw_venues_edit(request, round_id):
    round = get_object_or_404(Round, id=round_id)
    rc = RequestContext(request)

    rc['round'] = round
    rc['draw'] = round.get_draw()

    return render_to_response("draw_venues_edit.html", context_instance=rc)

def save_venues(request, round_id):
    round = get_object_or_404(Round, id=round_id)
    if request.method != "POST":
        return HttpResponseBadRequest("Expected POST")

    def v_id(a):
        try:
            return int(request.POST[a].split('_')[1])
        except IndexError:
            return None
    data = [(int(a.split('_')[1]), v_id(a))
             for a in request.POST.keys()]

    debates = Debate.objects.in_bulk([d_id for d_id, _ in data])
    venues = Venue.objects.in_bulk([v_id for _, v_id in data])
    for debate_id, venue_id in data:
        if venue_id == None:
            debates[debate_id].venue = None
        else:
            debates[debate_id].venue = venues[venue_id]

        debates[debate_id].save()

    return HttpResponse("ok")

def draw_adjudicators_edit(request, round_id):
    round = get_object_or_404(Round, id=round_id)
    rc = RequestContext(request)

    rc['round'] = round
    rc['draw'] = round.get_draw()

    return render_to_response("draw_adjudicators_edit.html", context_instance=rc)

def save_adjudicators(request, round_id):
    round = get_object_or_404(Round, id=round_id)
    if request.method != "POST":
        return HttpResponseBadRequest("Expected POST")
    return HttpResponse("ok")


