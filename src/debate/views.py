from django.http import Http404, HttpResponseRedirect, HttpResponseForbidden, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, loader

# Create your views here.

def index(request):
    return render_to_response('base.html', context_instance=RequestContext(request))