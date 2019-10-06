import logging

from django.conf import settings
from django.contrib import messages
from django.http import Http404
from django.utils.text import slugify
from django.utils.translation import gettext as _
from django.views.generic import TemplateView
from dynamic_preferences.views import PreferenceFormView

from actionlog.mixins import LogActionMixin
from actionlog.models import ActionLogEntry
from tournaments.mixins import TournamentMixin
from utils.mixins import AdministratorMixin
from utils.misc import reverse_tournament

from .presets import all_presets, get_preferences_data
from .forms import tournament_preference_form_builder
from .preferences import tournament_preferences_registry

logger = logging.getLogger(__name__)


class TournamentConfigIndexView(AdministratorMixin, TournamentMixin, TemplateView):
    template_name = "preferences_index.html"

    def get_preset_options(self):
        """Returns a list of all preset classes."""
        preset_options = []

        for preset_class in all_presets():
            preset_class.slugified_name = slugify(preset_class.__name__)
            preset_options.append(preset_class)

        preset_options.sort(key=lambda x: (x.show_in_list, x.name))
        if not settings.LEAGUE:
            return [p for p in preset_options if p.name != "WADL Options"]
        else:
            return preset_options

    def get_context_data(self, **kwargs):
        kwargs["presets"] = self.get_preset_options()
        kwargs["show_leagues"] = settings.LEAGUE
        t = self.tournament
        if t.pref('teams_in_debate') == 'bp':
            if t.pref('ballots_per_debate_prelim') == 'per-adj' or \
               t.pref('ballots_per_debate_elim') == 'per-adj':
                error = _("Your draw rules specify four teams per-debate but "
                          "your ballot setting specifies that adjudicators "
                          "submit independent ballots. These settings "
                          "<strong>are not compatible and will cause results "
                          "entry to crash</strong>. You need to go back to "
                          "the Debate Rules settings and change your "
                          "configuration to use consensus ballots.")
                messages.error(self.request, error)

        return super().get_context_data(**kwargs)


class TournamentPreferenceFormView(AdministratorMixin, LogActionMixin, TournamentMixin, PreferenceFormView):
    registry = tournament_preferences_registry
    section = None
    template_name = "preferences_section_set.html"

    action_log_type = ActionLogEntry.ACTION_TYPE_OPTIONS_EDIT

    def form_valid(self, *args, **kwargs):
        messages.success(self.request, _("Tournament options (%(section)s) saved.") % {'section': self.section.verbose_name})
        return super().form_valid(*args, **kwargs)

    def get_success_url(self):
        return reverse_tournament('options-tournament-index', self.tournament)

    def get_form_class(self, *args, **kwargs):
        section = self.kwargs.get('section', None)
        form_class = tournament_preference_form_builder(instance=self.tournament, section=section)
        return form_class


class ConfirmTournamentPreferencesView(AdministratorMixin, TournamentMixin, TemplateView):
    template_name = "preferences_presets_confirm.html"

    def get_selected_preset(self):
        preset_name = self.kwargs["preset_name"]
        # Retrieve the class that matches the name
        selected_presets = [x for x in all_presets() if slugify(x.__name__) == preset_name]
        if len(selected_presets) == 0:
            logger.warning("Could not find preset: %s", preset_name)
            raise Http404("Preset {!r} no found.".format(preset_name))
        elif len(selected_presets) > 1:
            logger.warning("Found more than one preset for %s", preset_name)
        return selected_presets[0]

    def get_context_data(self, **kwargs):
        selected_preset = self.get_selected_preset()
        preset_preferences = get_preferences_data(selected_preset, self.tournament)
        kwargs["preset_title"] = selected_preset.name
        kwargs["preset_name"] = self.kwargs["preset_name"]
        kwargs["changed_preferences"] = [p for p in preset_preferences if p['changed']]
        kwargs["unchanged_preferences"] = [p for p in preset_preferences if not p['changed']]
        return super().get_context_data(**kwargs)

    def get_template_names(self):
        if self.request.method == 'GET':
            return ["preferences_presets_confirm.html"]
        else:
            return ["preferences_presets_complete.html"]

    def save_presets(self):
        selected_preset = self.get_selected_preset()
        preset_preferences = get_preferences_data(selected_preset, self.tournament)

        for pref in preset_preferences:
            self.tournament.preferences[pref['key']] = pref['new_value']

        ActionLogEntry.objects.log(type=ActionLogEntry.ACTION_TYPE_OPTIONS_EDIT,
                user=self.request.user, tournament=self.tournament, content_object=self.tournament)
        messages.success(self.request, _("Tournament options saved according to preset "
                "%(name)s.") % {'name': selected_preset.name})

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        self.save_presets()
        return self.render_to_response(context)
