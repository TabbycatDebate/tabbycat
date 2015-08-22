from django import forms

from .options import make_options_form

from . import models
from actionlog.models import ActionLogEntry

from utils.views import *

@admin_required
@tournament_view
def tournament_options(request, t):

    context = dict()
    if request.method == 'POST':
        form = make_options_form(t, request.POST)
        if form.is_valid():
            form.save()
            ActionLogEntry.objects.log(type=ActionLogEntry.ACTION_TYPE_CONFIG_EDIT, user=request.user, tournament=t)
            messages.success(request, "Tournament option saved.")
    else:
        form = make_options_form(t)

    context['form'] = form

    return r2r(request, 'tournament_options.html', context)
