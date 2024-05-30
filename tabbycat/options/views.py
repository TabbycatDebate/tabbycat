import logging

from django.contrib import messages
from django.http import Http404
from django.utils.text import slugify
from django.utils.translation import gettext as _
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.views import PreferenceFormView

from actionlog.mixins import LogActionMixin
from actionlog.models import ActionLogEntry
from tournaments.mixins import TournamentMixin
from users.permissions import Permission
from utils.misc import reverse_tournament
from utils.mixins import AdministratorMixin

from .forms import tournament_preference_form_builder
from .preferences import tournament_preferences_registry
from .presets import all_presets, get_preset_from_slug

logger = logging.getLogger(__name__)


class TournamentConfigIndexView(AdministratorMixin, TournamentMixin, TemplateView):
    template_name = "preferences_index.html"
    view_permission = True

    def get_preset_options(self):
        """Returns a list of all preset classes."""
        preset_options = []

        for preset_class in all_presets():
            preset_class.slugified_name = slugify(preset_class.__name__)
            preset_options.append(preset_class)

        preset_options.sort(key=lambda x: (x.show_in_list, x.name))
        return preset_options

    def get_context_data(self, **kwargs):
        kwargs["presets"] = self.get_preset_options()
        return super().get_context_data(**kwargs)


class MultiPreferenceFormView(PreferenceFormView):
    possible_registries = []

    def dispatch(self, request, *args, **kwargs):
        for registry in self.possible_registries:
            self.registry = registry
            try:
                return super().dispatch(request, *args, **kwargs)
            except Http404:
                continue
        else:
            raise Http404


class TournamentPreferenceFormView(AdministratorMixin, LogActionMixin, TournamentMixin, MultiPreferenceFormView):
    possible_registries = [global_preferences_registry, tournament_preferences_registry]
    section = None
    template_name = "preferences_section_set.html"
    view_permission = Permission.VIEW_SETTINGS
    edit_permission = Permission.EDIT_SETTINGS

    action_log_type = ActionLogEntry.ActionType.OPTIONS_EDIT

    def form_valid(self, *args, **kwargs):
        messages.success(self.request, _("Tournament options (%(section)s) saved.") % {'section': self.section.verbose_name})
        return super().form_valid(*args, **kwargs)

    def get_success_url(self):
        return reverse_tournament('options-tournament-index', self.tournament)

    def get_form_class(self, *args, **kwargs):
        section = self.kwargs.get('section', None)
        form_class = tournament_preference_form_builder(instance=self.tournament, section=section)
        return form_class


class SetPresetPreferencesView(AdministratorMixin, LogActionMixin, TournamentMixin, FormView):
    template_name = "preset_edit.html"
    page_emoji = '❔'
    view_permission = Permission.VIEW_SETTINGS
    edit_permission = Permission.EDIT_SETTINGS

    action_log_type = ActionLogEntry.ActionType.OPTIONS_EDIT

    def get_page_title(self):
        return _("Apply Preset: %s") % self.get_selected_preset().name

    def get_form(self):
        return self.get_selected_preset().get_form(self.tournament, **self.get_form_kwargs())

    def get_selected_preset(self):
        try:
            return get_preset_from_slug(self.kwargs["preset_name"])
        except ValueError as e:
            raise Http404(str(e))

    def get_success_url(self):
        return reverse_tournament('options-tournament-index', self.tournament)

    def form_valid(self, form):
        form.update_preferences()
        messages.success(self.request, _("Tournament options saved based on preset "
                "%(name)s.") % {'name': self.get_selected_preset().name})
        return super().form_valid(form)
