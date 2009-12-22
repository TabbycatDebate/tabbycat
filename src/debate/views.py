from django.http import Http404, HttpResponseRedirect, HttpResponseForbidden, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, loader

from debate.models import Round

# Create your views here.

def index(request):
    return render_to_response('index.html', context_instance=RequestContext(request))

def venue_availability(request, round_id):
    rc = RequestContext(request)
    rc['round'] = get_object_or_404(Round, id=round_id)

    return render_to_response('venue_availability.html',
                              context_instance=rc)

