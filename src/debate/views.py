from django.http import Http404, HttpResponseRedirect, HttpResponseForbidden, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse

from debate.models import Round

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

    available_ids = [int(a.replace("check_", "")) for a in request.POST.keys()]

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

def create_draw(request, round_id):
    round = get_object_or_404(Round, id=round_id)

    if request.method != "POST":
        return HttpResponseBadRequest("Expected POST")

    round.draw()

    return HttpResponseRedirect(reverse('draw', args=[round_id])) 


