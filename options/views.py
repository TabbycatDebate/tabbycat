from django import forms
from .options import make_options_form
from actionlog.models import ActionLogEntry
from utils.views import *

@admin_required
@tournament_view
def tournament_options(request, t):


    from results.dynamic_preferences_registry import tournament_preferences_registry
    # We instanciate a manager for our global preferences
    tournament_preferences_registry = tournament_preferences_registry.manager()

    tournament_preferences = t.preferences


    context = dict()
    if request.method == 'POST':
        form = make_options_form(t, request.POST)
        if form.is_valid():
            form.save()
            ActionLogEntry.objects.log(type=ActionLogEntry.ACTION_TYPE_OPTIONS_EDIT, user=request.user, tournament=t)
            messages.success(request, "Tournament option saved.")
    else:
        form = make_options_form(t)

    context['form'] = form
    context['tournament_preferences_registry'] = tournament_preferences_registry
    context['tournament_preferences'] = tournament_preferences

    return r2r(request, 'tournament_options.html', context)
