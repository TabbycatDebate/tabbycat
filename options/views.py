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


from results.dynamic_preferences_registry import tournament_preferences_registry
from dynamic_preferences.forms import preference_form_builder, PreferenceForm

class TournamentPreferenceForm(PreferenceForm):

    registry = tournament_preferences_registry


def tournament_preference_form_builder(instance, preferences=[], **kwargs):
    return preference_form_builder(TournamentPreferenceForm, preferences, model={'instance': instance}, **kwargs)



from dynamic_preferences.views import PreferenceFormView
class TournamentPreferenceFormView(PreferenceFormView):
    """
    Will pass `request.user` to form_builder
    """
    registry = tournament_preferences_registry

    template_name = "tournament_config.html"

    def get_form_class(self, *args, **kwargs):
        section = self.kwargs.get('section', None)
        form_class = tournament_preference_form_builder(instance=self.request.tournament, section=section)
        return form_class


