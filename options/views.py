from django import forms
from .options import make_options_form
from actionlog.models import ActionLogEntry
from utils.views import *
from dynamic_preferences.views import PreferenceFormView

@admin_required
@tournament_view
def tournament_config_index(request, t):
    return r2r(request, 'tournament_config_index.html')


from options.dynamic_preferences_registry import tournament_preferences_registry
from dynamic_preferences.forms import preference_form_builder, PreferenceForm

class TournamentPreferenceForm(PreferenceForm):

    registry = tournament_preferences_registry


def tournament_preference_form_builder(instance, preferences=[], **kwargs):
    return preference_form_builder(TournamentPreferenceForm, preferences, model={'instance': instance}, **kwargs)



class TournamentPreferenceFormView(PreferenceFormView):

    registry = tournament_preferences_registry
    section = None

    template_name = "tournament_config.html"

    def get_form_class(self, *args, **kwargs):
        form_class = tournament_preference_form_builder(instance=self.request.tournament, section=self.section)
        return form_class


