from django.http import Http404, HttpResponseRedirect, HttpResponseForbidden, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from django.db.models import Sum, Count

from debate.models import Round, Debate, Team, Venue
from debate import forms

from functools import wraps
# Create your views here.

def round_view(view_fn):
    @wraps(view_fn)
    def foo(request, round_id):
        round = get_object_or_404(Round, id=round_id)
        rc = RequestContext(request)
        rc['round'] = round
        return view_fn(request, rc, round)
    return foo

def expect_post(view_fn):
    @wraps(view_fn)
    def foo(request, *args, **kwargs):
        if request.method != "POST":
            return HttpResponseBadRequest("Expected POST")
        return view_fn(request, *args, **kwargs)
    return foo

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
@expect_post
def update_base_availability(request, round_id, update_method):
    round = get_object_or_404(Round, id=round_id)

    available_ids = [int(a.replace("check_", "")) for a in request.POST.keys()
                     if a.startswith("check_")]

    getattr(round, update_method)(available_ids)

    return HttpResponse("ok")

@round_view
def draw(request, rc, round):

    if round.draw_status == round.STATUS_NONE:
        return draw_none(request, rc, round)

    if round.draw_status == round.STATUS_DRAFT:
        return draw_draft(request, rc, round)

    if round.draw_status == round.STATUS_CONFIRMED:
        return draw_confirmed(request, rc, round)

    raise

def draw_none(request, rc, round):
    
    active_teams = round.active_teams.all()
    rc['active_teams'] = active_teams
    return render_to_response("draw_none.html", context_instance=rc)

def draw_draft(request, rc, round):
    rc['draw'] = round.get_draw()

    return render_to_response("draw_draft.html", context_instance=rc)

def draw_confirmed(request, rc, round):
    rc['draw'] = round.get_draw()

    return render_to_response("draw_confirmed.html", context_instance=rc)

@expect_post
@round_view
def create_draw(request, rc, round):

    round.draw()

    return HttpResponseRedirect(reverse('draw', args=[round.id])) 

@expect_post
@round_view
def confirm_draw(request, rc, round):

    if round.draw_status != round.STATUS_DRAFT:
        return HttpResponseBadRequest("Draw status is not DRAFT")

    round.draw_status = round.STATUS_CONFIRMED
    round.save()

    return HttpResponseRedirect(reverse('draw', args=[round.id])) 

@expect_post
@round_view
def create_adj_allocation(request, rc, round):
    if round.draw_status != round.STATUS_CONFIRMED:
        return HttpResponseBadRequest("Draw is not confirmed")

    from debate.adjudicator.stab import StabAllocator
    round.allocate_adjudicators(StabAllocator)

    return HttpResponseRedirect(reverse('draw', args=[round.id])) 

@round_view
def results(request, rc, round):
    rc['draw'] = round.get_draw()

    return render_to_response("results.html", context_instance=rc)

def enter_result(request, debate_id):
    debate = get_object_or_404(Debate, id=debate_id)

    rc = RequestContext(request)
    rc['debate'] = debate

    form = forms.make_results_form(debate)
    rc['form'] = form

    return render_to_response('enter_results.html', context_instance=rc)

@expect_post
def save_result(request, debate_id):

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

@round_view
def team_standings(request, rc, round):
    
    teams = Team.objects.standings(round)
    for team in teams:
        setattr(team, 'results_in', team.results_count >= round.seq)

    rc['teams'] = teams

    return render_to_response('team_standings.html', context_instance=rc)


@round_view
def draw_venues_edit(request, rc, round):
    rc['draw'] = round.get_draw()

    return render_to_response("draw_venues_edit.html", context_instance=rc)

@expect_post
@round_view
def save_venues(request, rc, round):

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

@round_view
def draw_adjudicators_edit(request, rc, round):
    rc['draw'] = round.get_draw()

    return render_to_response("draw_adjudicators_edit.html", context_instance=rc)

@round_view
def save_adjudicators(request, rc, round):
    if request.method != "POST":
        return HttpResponseBadRequest("Expected POST")

    def id(s):
        return int(s.split('_')[1])

    debate_ids = set(id(a) for a in request.POST);
    debates = Debate.objects.in_bulk(list(debate_ids));
    debate_adjudicators = {}
    for d_id, debate in debates.items():
        a = debate.adjudicators
        a.delete()
        debate_adjudicators[d_id] = a

    for key, vals in request.POST.lists():
        if key.startswith("chair_"):
            debate_adjudicators[id(key)].chair = vals[0]
        if key.startswith("panel_"):
            for val in vals:
                debate_adjudicators[id(key)].panel.append(val)

    for d_id, alloc in debate_adjudicators.items():
        alloc.save()

    return HttpResponse("ok")

def adj_conflicts(request):
    import json
    from debate.models import AdjudicatorConflict

    data = {}

    for ac in AdjudicatorConflict.objects.all():
        if ac.adjudicator_id not in data:
            data[ac.adjudicator_id] = list()
        data[ac.adjudicator_id].append(ac.team_id)

    return HttpResponse(json.dumps(data), mimetype="text/json")


def adj_scores(request):
    import json
    from debate.models import Adjudicator

    data = {}

    for adj in Adjudicator.objects.all():
        data[adj.id] = adj.test_score

    return HttpResponse(json.dumps(data), mimetype="text/json")


