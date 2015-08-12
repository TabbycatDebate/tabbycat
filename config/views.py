from django.contrib import messages

from debate.views import admin_required, tournament_view, r2r
from config import make_config_form

from . import models
from action_log.models import ActionLog

@admin_required
@tournament_view
def tournament_config(request, t):

    context = dict()
    if request.method == 'POST':
        form = make_config_form(t, request.POST)
        if form.is_valid():
            form.save()
            ActionLog.objects.log(type=ActionLog.ACTION_TYPE_CONFIG_EDIT, user=request.user, tournament=t)
            messages.success(request, "Tournament configuration saved.")
    else:
        form = make_config_form(t)

    context['form'] = form

    return r2r(request, 'tournament_config.html', context)
