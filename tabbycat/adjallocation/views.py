import json
import logging

from django.contrib import messages
from django.db.models import Prefetch
from django.forms import ChoiceField, ModelChoiceField
from django.forms.models import ModelChoiceIterator
from django.utils.translation import gettext as _, gettext_lazy, ngettext
from django.views.generic.base import TemplateView

from actionlog.mixins import LogActionMixin
from actionlog.models import ActionLogEntry
from adjallocation.models import DebateAdjudicator
from availability.utils import annotate_availability
from draw.models import Debate, DebateTeam
from draw.types import DebateSide
from options.utils import use_team_code_names
from participants.models import Adjudicator, Institution, Region, Speaker
from participants.prefetch import populate_feedback_scores, populate_win_counts
from tournaments.mixins import DebateDragAndDropMixin, TournamentMixin
from users.permissions import has_permission, Permission
from utils.misc import ranks_dictionary, redirect_tournament, reverse_tournament
from utils.mixins import AdministratorMixin
from utils.views import ModelFormSetView

from .conflicts import ConflictsInfo, HistoryInfo
from .models import (AdjudicatorAdjudicatorConflict, AdjudicatorInstitutionConflict,
                     AdjudicatorTeamConflict,
                     PreformedPanelAdjudicator, TeamInstitutionConflict)
from .serializers import EditDebateAdjsDebateSerializer, EditPanelAdjsPanelSerializer, EditPanelOrDebateAdjSerializer

logger = logging.getLogger(__name__)


class BaseEditDebateOrPanelAdjudicatorsView(DebateDragAndDropMixin, AdministratorMixin, TemplateView):

    def get_extra_info(self):
        info = super().get_extra_info()
        # TODO: construct adj score ranges from settings
        info['highlights']['gender'] = [
            {'pk': 'm', 'fields': {'name': _('Male')}},
            {'pk': 'f', 'fields': {'name': _('Female')}},
            {'pk': 'o', 'fields': {'name': _('Other')}},
            {'pk': 'u', 'fields': {'name': _('Unknown')}},
        ]
        info['adjMinScore'] = self.tournament.pref('adj_min_score')
        info['adjMaxScore'] = self.tournament.pref('adj_max_score')
        info['highlights']['rank'] = ranks_dictionary(
            self.tournament, info['adjMinScore'], info['adjMaxScore'])
        regions = [{'pk': r.id, 'fields': {'name': r.name}} for r in Region.objects.all()]
        info['highlights']['region'] = regions
        allocation_preferences = [
            'draw_rules__adj_min_voting_score',
            'draw_rules__adj_conflict_penalty',
            'draw_rules__adj_history_penalty',
            'draw_rules__preformed_panel_mismatch_penalty',
            'draw_rules__no_trainee_position',
            'draw_rules__no_panellist_position',
        ]
        info['allocationSettings'] = {}
        for key in allocation_preferences:
            info['allocationSettings'][key] = self.tournament.preferences[key]

        info['clashes'] = self.get_adjudicator_conflicts()
        info['histories'] = self.get_history_conflicts()
        info['hasPreformedPanels'] = self.round.preformedpanel_set.exists()
        return info

    def get_serialised_allocatable_items(self):
        adjs = Adjudicator.objects.filter(tournament=self.tournament)
        adjs = annotate_availability(adjs, self.round)
        populate_feedback_scores(adjs)
        weight = self.tournament.current_round.feedback_weight
        serialized_adjs = EditPanelOrDebateAdjSerializer(
            adjs, many=True, context={'feedback_weight': weight})
        return self.json_render(serialized_adjs.data)

    def get_adjudicator_conflicts(self):
        conflicts = ConflictsInfo(teams=self.tournament.team_set.all(),
                                  adjudicators=self.tournament.adjudicator_set.all())
        team_conflicts, adj_conflicts = conflicts.serialized_by_participant()
        return {'teams': team_conflicts, 'adjudicators': adj_conflicts}

    def get_history_conflicts(self):
        history = HistoryInfo(self.round)
        team_history, adj_history = history.serialized_by_participant()
        return {'teams': team_history,  'adjudicators': adj_history}

    def get_context_data(self, **kwargs):
        kwargs['vueDebatesOrPanelAdjudicators'] = json.dumps(None)
        return super().get_context_data(**kwargs)


class EditDebateAdjudicatorsView(BaseEditDebateOrPanelAdjudicatorsView):
    template_name = "edit_debate_adjudicators.html"
    page_title = gettext_lazy("Edit Allocation")
    prefetch_adjs = True # Fetched in full as get_serialised

    view_permission = Permission.VIEW_DEBATEADJUDICATORS
    edit_permission = Permission.EDIT_DEBATEADJUDICATORS

    def get_extra_info(self):
        info = super().get_extra_info()
        return info

    def debates_or_panels_factory(self, debates):
        return EditDebateAdjsDebateSerializer(
            debates, many=True, context={'sides': self.tournament.sides,
                                         'round': self.round})


class MultiRoundEditDebateAdjudicatorsView(BaseEditDebateOrPanelAdjudicatorsView):
    template_name = "edit_debate_adjudicators.html"
    page_title = gettext_lazy("Edit Allocation (Concurrent Rounds)")
    prefetch_adjs = True

    view_permission = Permission.VIEW_DEBATEADJUDICATORS
    edit_permission = Permission.EDIT_DEBATEADJUDICATORS

    def debates_or_panels_factory(self, debates):
        return EditDebateAdjsDebateSerializer(
            debates, many=True, context={'sides': self.tournament.sides,
                                         'round': self.round})

    def get_draw_or_panels_objects(self):
        """Include debates from all current elimination rounds (one per break category)."""
        if not self.round.is_break_round:
            return super().get_draw_or_panels_objects()

        prefetches = ()
        if self.prefetch_venues:
            prefetches += ('venue__venuecategory_set',)
        if self.prefetch_adjs:
            prefetches += (Prefetch('debateadjudicator_set',
                queryset=DebateAdjudicator.objects.select_related('adjudicator')),)
        if self.prefetch_teams:
            prefetches += (Prefetch('debateteam_set',
                queryset=DebateTeam.objects.select_related('team').prefetch_related(
                    Prefetch('team__speaker_set', queryset=Speaker.objects.order_by('name')),
                    'team__break_categories',
                )),
            )
        else:
            prefetches += ('debateteam_set__team__break_categories',)

        draw = Debate.objects.filter(round__in=self.tournament.current_rounds).exclude(
            debateteam__side=DebateSide.BYE,
        ).select_related('round__tournament', 'venue').prefetch_related(*prefetches)

        if self.prefetch_teams:
            populate_win_counts([dt.team for debate in draw for dt in debate.debateteam_set.all()])
        return draw


class EditPanelAdjudicatorsView(BaseEditDebateOrPanelAdjudicatorsView):
    template_name = "edit_panel_adjudicators.html"
    page_title = gettext_lazy("Edit Panels")

    view_permission = Permission.VIEW_PREFORMEDPANELS
    edit_permission = Permission.EDIT_PREFORMEDPANELS

    def get_extra_info(self):
        info = super().get_extra_info()
        info['backUrl'] = reverse_tournament('panel-adjudicators-index',
                                             self.tournament)  # Override
        info['backLabel'] = _("Return to Panels Overview")
        return info

    def get_draw_or_panels_objects(self):
        panels = self.round.preformedpanel_set.all().prefetch_related(
            Prefetch('preformedpaneladjudicator_set',
                queryset=PreformedPanelAdjudicator.objects.select_related('adjudicator')),
        )
        return panels

    def debates_or_panels_factory(self, panels):
        return EditPanelAdjsPanelSerializer(panels, many=True,
                                            context={'round': self.round})


class PanelAdjudicatorsIndexView(AdministratorMixin, TournamentMixin, TemplateView):
    template_name = "preformed_index.html"
    page_title = gettext_lazy("Preformed Panels")
    view_permission = True


# ==============================================================================
# Conflict formset views
# ==============================================================================

class DedupModelChoiceIterator(ModelChoiceIterator):
    def __iter__(self):
        if self.field.empty_label is not None:
            yield ("", self.field.empty_label)
        for obj in self.queryset:
            yield self.choice(obj)


class DedupModelChoiceField(ModelChoiceField):
    iterator = DedupModelChoiceIterator

    def __deepcopy__(self, memo):
        return super(ChoiceField, self).__deepcopy__(memo)

    def _get_queryset(self):
        return self._queryset

    def _set_queryset(self, queryset):
        self._queryset = queryset
        self.widget.choices = self.choices

    queryset = property(_get_queryset, _set_queryset)


class TeamChoiceField(DedupModelChoiceField):

    def label_from_instance(self, obj):
        return obj.code_name if self.use_code_names else obj.short_name


class BaseAdjudicatorConflictsView(LogActionMixin, AdministratorMixin, TournamentMixin, ModelFormSetView):

    template_name = 'edit_conflicts.html'
    page_emoji = "🔶"

    formset_factory_kwargs = {}

    def get_formset_factory_kwargs(self):
        can_edit = has_permission(self.request.user, self.get_edit_permission(), self.tournament)
        kwargs = super().get_formset_factory_kwargs()
        kwargs['extra'] = 10 * int(can_edit)
        kwargs['can_delete'] = can_edit
        return kwargs

    def get_formset(self):
        formset = super().get_formset()
        if not has_permission(self.request.user, self.get_edit_permission(), self.tournament):
            for form in formset:
                for field in form.fields.values():
                    field.disabled = True
        return formset

    def get_context_data(self, **kwargs):
        kwargs['save_text'] = self.save_text
        kwargs['can_edit'] = has_permission(self.request.user, self.get_edit_permission(), self.tournament)
        return super().get_context_data(**kwargs)

    def get_success_url(self, *args, **kwargs):
        return reverse_tournament('importer-simple-index', self.tournament)

    def formset_valid(self, formset):
        result = super().formset_valid(formset)
        nsaved = len(self.instances)
        ndeleted = len(formset.deleted_objects)
        self.add_message(nsaved, ndeleted)
        if "add_more" in self.request.POST:
            return redirect_tournament(self.same_view, self.tournament)
        return result


class AdjudicatorTeamConflictsView(BaseAdjudicatorConflictsView):

    view_permission = Permission.VIEW_ADJ_TEAM_CONFLICTS
    edit_permission = Permission.EDIT_ADJ_TEAM_CONFLICTS

    action_log_type = ActionLogEntry.ActionType.CONFLICTS_ADJ_TEAM_EDIT
    formset_model = AdjudicatorTeamConflict
    page_title = gettext_lazy("Adjudicator-Team Conflicts")
    save_text = gettext_lazy("Save Adjudicator-Team Conflicts")
    same_view = 'adjallocation-conflicts-adj-team'
    formset_factory_kwargs = BaseAdjudicatorConflictsView.formset_factory_kwargs.copy()
    formset_factory_kwargs.update({
        'fields': ('adjudicator', 'team'),
        'field_classes': {'adjudicator': DedupModelChoiceField, 'team': TeamChoiceField},
    })

    def get_formset(self):
        formset = super().get_formset()
        all_adjs = self.tournament.adjudicator_set.order_by('name').all()
        use_code_names = use_team_code_names(self.tournament, admin=True, user=self.request.user)
        all_teams = self.tournament.team_set.order_by('code_name' if use_code_names else 'short_name').all()
        for form in formset:
            form.fields['adjudicator'].queryset = all_adjs  # order alphabetically
            form.fields['team'].queryset = all_teams        # order alphabetically
            form.fields['team'].use_code_names = use_code_names
        return formset

    def get_formset_queryset(self):
        return self.formset_model.objects.filter(
            adjudicator__tournament=self.tournament,
        ).order_by('adjudicator__name')

    def add_message(self, nsaved, ndeleted):
        if nsaved > 0:
            messages.success(self.request, ngettext(
                "Saved %(count)d adjudicator-team conflict.",
                "Saved %(count)d adjudicator-team conflicts.",
                nsaved,
            ) % {'count': nsaved})
        if ndeleted > 0:
            messages.success(self.request, ngettext(
                "Deleted %(count)d adjudicator-team conflict.",
                "Deleted %(count)d adjudicator-team conflicts.",
                ndeleted,
            ) % {'count': ndeleted})
        if nsaved == 0 and ndeleted == 0:
            messages.success(self.request, _("No changes were made to adjudicator-team conflicts."))


class AdjudicatorAdjudicatorConflictsView(BaseAdjudicatorConflictsView):

    view_permission = Permission.VIEW_ADJ_ADJ_CONFLICTS
    edit_permission = Permission.EDIT_ADJ_ADJ_CONFLICTS

    action_log_type = ActionLogEntry.ActionType.CONFLICTS_ADJ_ADJ_EDIT
    formset_model = AdjudicatorAdjudicatorConflict
    page_title = gettext_lazy("Adjudicator-Adjudicator Conflicts")
    save_text = gettext_lazy("Save Adjudicator-Adjudicator Conflicts")
    same_view = 'adjallocation-conflicts-adj-adj'
    formset_factory_kwargs = BaseAdjudicatorConflictsView.formset_factory_kwargs.copy()
    formset_factory_kwargs.update({
        'fields': ('adjudicator1', 'adjudicator2'),
        'field_classes': {'adjudicator1': DedupModelChoiceField, 'adjudicator2': DedupModelChoiceField},
    })

    def get_formset(self):
        formset = super().get_formset()
        all_adjs = self.tournament.adjudicator_set.order_by('name').all()
        for form in formset:
            form.fields['adjudicator1'].queryset = all_adjs  # order alphabetically
            form.fields['adjudicator2'].queryset = all_adjs  # order alphabetically
        return formset

    def get_formset_queryset(self):
        return self.formset_model.objects.filter(
            adjudicator1__tournament=self.tournament,
        ).order_by('adjudicator1__name')

    def add_message(self, nsaved, ndeleted):
        if nsaved > 0:
            messages.success(self.request, ngettext(
                "Saved %(count)d adjudicator-adjudicator conflict.",
                "Saved %(count)d adjudicator-adjudicator conflicts.",
                nsaved,
            ) % {'count': nsaved})
        if ndeleted > 0:
            messages.success(self.request, ngettext(
                "Deleted %(count)d adjudicator-adjudicator conflict.",
                "Deleted %(count)d adjudicator-adjudicator conflicts.",
                ndeleted,
            ) % {'count': ndeleted})
        if nsaved == 0 and ndeleted == 0:
            messages.success(self.request, _("No changes were made to adjudicator-adjudicator conflicts."))


class AdjudicatorInstitutionConflictsView(BaseAdjudicatorConflictsView):

    view_permission = Permission.VIEW_ADJ_INST_CONFLICTS
    edit_permission = Permission.EDIT_ADJ_INST_CONFLICTS

    action_log_type = ActionLogEntry.ActionType.CONFLICTS_ADJ_INST_EDIT
    formset_model = AdjudicatorInstitutionConflict
    page_title = gettext_lazy("Adjudicator-Institution Conflicts")
    save_text = gettext_lazy("Save Adjudicator-Institution Conflicts")
    same_view = 'adjallocation-conflicts-adj-inst'
    formset_factory_kwargs = BaseAdjudicatorConflictsView.formset_factory_kwargs.copy()
    formset_factory_kwargs.update({
        'fields': ('adjudicator', 'institution'),
        'field_classes': {'adjudicator': DedupModelChoiceField, 'institution': DedupModelChoiceField},
    })

    def get_formset(self):
        formset = super().get_formset()
        all_adjs = self.tournament.adjudicator_set.order_by('name').all()
        insts = Institution.objects.all()
        for form in formset:
            form.fields['adjudicator'].queryset = all_adjs  # order alphabetically
            form.fields['institution'].queryset = insts
        return formset

    def get_formset_queryset(self):
        return self.formset_model.objects.filter(
            adjudicator__tournament=self.tournament,
        ).order_by('adjudicator__name')

    def add_message(self, nsaved, ndeleted):
        if nsaved > 0:
            messages.success(self.request, ngettext(
                "Saved %(count)d adjudicator-institution conflict.",
                "Saved %(count)d adjudicator-institution conflicts.",
                nsaved,
            ) % {'count': nsaved})
        if ndeleted > 0:
            messages.success(self.request, ngettext(
                "Deleted %(count)d adjudicator-institution conflict.",
                "Deleted %(count)d adjudicator-institution conflicts.",
                ndeleted,
            ) % {'count': ndeleted})
        if nsaved == 0 and ndeleted == 0:
            messages.success(self.request, _("No changes were made to adjudicator-institution conflicts."))


class TeamInstitutionConflictsView(BaseAdjudicatorConflictsView):

    view_permission = Permission.VIEW_TEAM_INST_CONFLICTS
    edit_permission = Permission.EDIT_TEAM_INST_CONFLICTS

    action_log_type = ActionLogEntry.ActionType.CONFLICTS_TEAM_INST_EDIT
    formset_model = TeamInstitutionConflict
    page_title = gettext_lazy("Team-Institution Conflicts")
    save_text = gettext_lazy("Save Team-Institution Conflicts")
    same_view = 'adjallocation-conflicts-team-inst'
    formset_factory_kwargs = BaseAdjudicatorConflictsView.formset_factory_kwargs.copy()
    formset_factory_kwargs.update({
        'fields': ('team', 'institution'),
        'field_classes': {'team': TeamChoiceField, 'institution': DedupModelChoiceField},
    })

    def get_formset(self):
        formset = super().get_formset()
        use_code_names = use_team_code_names(self.tournament, admin=True, user=self.request.user)
        all_teams = self.tournament.team_set.order_by('code_name' if use_code_names else 'short_name').all()
        all_teams = self.tournament.team_set.order_by('short_name').all()
        insts = Institution.objects.all()
        for form in formset:
            form.fields['team'].queryset = all_teams  # order alphabetically
            form.fields['team'].use_code_names = use_code_names
            form.fields['institution'].queryset = insts
        return formset

    def get_formset_queryset(self):
        return self.formset_model.objects.filter(
            team__tournament=self.tournament,
        ).order_by('team__short_name')

    def add_message(self, nsaved, ndeleted):
        if nsaved > 0:
            messages.success(self.request, ngettext(
                "Saved %(count)d team-institution conflict.",
                "Saved %(count)d team-institution conflicts.",
                nsaved,
            ) % {'count': nsaved})
        if ndeleted > 0:
            messages.success(self.request, ngettext(
                "Deleted %(count)d team-institution conflict.",
                "Deleted %(count)d team-institution conflicts.",
                ndeleted,
            ) % {'count': ndeleted})
        if nsaved == 0 and ndeleted == 0:
            messages.success(self.request, _("No changes were made to team-institution conflicts."))
