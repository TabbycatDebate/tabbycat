from django.http import Http404, HttpResponseRedirect, HttpResponseForbidden, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from django.db.models import Sum, Count

from debate.models import Round, Debate, Team, Venue, Adjudicator
from debate.models import AdjudicatorConflict, DebateAdjudicator
from debate import forms

from functools import wraps
import json

def redirect_to(view, **kwargs):
    return HttpResponseRedirect(reverse(view, **kwargs))

def round_view(view_fn):
    @wraps(view_fn)
    def foo(request, round_id):
        round = get_object_or_404(Round, id=round_id)
        rc = dict(round=round)
        return view_fn(request, rc, round)
    return foo

def expect_post(view_fn):
    @wraps(view_fn)
    def foo(request, *args, **kwargs):
        if request.method != "POST":
            return HttpResponseBadRequest("Expected POST")
        return view_fn(request, *args, **kwargs)
    return foo

def r2r(request, template, extra_context=None):
    rc = RequestContext(request)
    if extra_context:
        rc.update(extra_context)
    return render_to_response(template, context_instance=rc)

def login(request):
    return r2r(request, 'login.html')

def index(request):
    return r2r(request, 'index.html')

def draw_index(request):
    return r2r(request, 'draw_index.html')

@round_view
def round_index(request, rc, round):
    return r2r(request, 'round_index.html', rc)

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
    round = get_object_or_404(Round, id=round_id)

    items = getattr(round, '%s_availability' % model)().order_by('name')

    context = {
        context_name: items,
        'round': round,
    }
    return r2r(request, '%s_availability.html' % model, context)

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

    rc['active_teams'] = round.active_teams.all()
    return r2r(request, "draw_none.html", rc)


def draw_draft(request, rc, round):

    rc['draw'] = round.get_draw()
    return r2r(request, "draw_draft.html", rc)


def draw_confirmed(request, rc, round):

    rc['draw'] = round.get_draw()
    return r2r(request, "draw_confirmed.html", rc)


@expect_post
@round_view
def create_draw(request, rc, round):

    round.draw()
    return redirect_to('draw', args=[round.id])


@expect_post
@round_view
def confirm_draw(request, rc, round):

    if round.draw_status != round.STATUS_DRAFT:
        return HttpResponseBadRequest("Draw status is not DRAFT")

    round.draw_status = round.STATUS_CONFIRMED
    round.save()

    return redirect_to('draw', args=[round.id])


@expect_post
@round_view
def create_adj_allocation(request, rc, round):

    if round.draw_status != round.STATUS_CONFIRMED:
        return HttpResponseBadRequest("Draw is not confirmed")

    from debate.adjudicator.hungarian import HungarianAllocator
    round.allocate_adjudicators(HungarianAllocator)

    return redirect_to('draw', args=[round.id])


@round_view
def results(request, rc, round):

    rc['draw'] = round.get_draw()
    return r2r(request, "results.html", rc)


def enter_result(request, debate_id):

    debate = get_object_or_404(Debate, id=debate_id)
    form = forms.make_results_form(debate)

    return r2r(request, 'enter_results.html', dict(debate=debate, form=form))


@expect_post
def save_result(request, debate_id):
    debate = get_object_or_404(Debate, id=debate_id)

    class_ = forms.make_results_form_class(debate)
    form = class_(request.POST)

    if form.is_valid():
        form.save()
    else:
        raise

    return redirect_to('results', args=[debate.round.id])


@round_view
def team_standings(request, rc, round):
    
    teams = Team.objects.standings(round)
    for team in teams:
        setattr(team, 'results_in', team.results_count >= round.seq)
    rc['teams'] = teams

    return r2r(request, 'team_standings.html', rc)


@round_view
def draw_venues_edit(request, rc, round):

    rc['draw'] = round.get_draw()
    return r2r(request, "draw_venues_edit.html", rc)


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
    return r2r(request, "draw_adjudicators_edit.html", rc)


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


@round_view
def adj_conflicts(request, rc, round):

    data = {
        'conflict': {},
        'history': {},
    }

    def add(type, adj_id, target_id):
        if adj_id not in data[type]:
            data[type][adj_id] = []
        data[type][adj_id].append(target_id)

    for ac in AdjudicatorConflict.objects.all():
        add('conflict', ac.adjudicator_id, ac.team_id)

    history = DebateAdjudicator.objects.filter(
        debate__round__seq__lt = round.seq,
    )

    for da in history:
        add('history', da.adjudicator_id, da.debate.aff_team.id)
        add('history', da.adjudicator_id, da.debate.neg_team.id)

    return HttpResponse(json.dumps(data), mimetype="text/json")


def adj_scores(request):
    data = {}

    #TODO: make round-dependent
    for adj in Adjudicator.objects.all():
        data[adj.id] = adj.score

    return HttpResponse(json.dumps(data), mimetype="text/json")


def adj_feedback(request):

    adjudicators = Adjudicator.objects.all()
    return render_to_response('adjudicator_feedback.html',
                              dict(adjudicators=adjudicators))


def get_adj_feedback(request):

    adj = get_object_or_404(Adjudicator, pk=int(request.GET['id']))
    feedback = adj.get_feedback()
    data = [ [unicode(f.round), 
              f.debate.bracket, 
              unicode(f.debate), 
              unicode(f.source), 
              f.score,
              f.comments,
             ] for f in feedback ]

    return HttpResponse(json.dumps({'aaData': data}), mimetype="text/json")


def enter_feedback(request, adjudicator_id):

    adj = get_object_or_404(Adjudicator, id=adjudicator_id)
    if request.method == "POST":
        form = forms.make_feedback_form_class(adj)(request.POST)
        if form.is_valid():
            form.save()
            return redirect_to('adj_feedback')
        raise

    form = forms.make_feedback_form_class(adj)()
    
    return r2r(request, 'enter_feedback.html', dict(adj=adj, form=form))

