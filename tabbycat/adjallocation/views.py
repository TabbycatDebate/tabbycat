import json
import logging

from django.contrib import messages
from django.db.models import Prefetch
from django.forms import ChoiceField, ModelChoiceField
from django.forms.models import ModelChoiceIterator, modelformset_factory
from django.utils.translation import gettext as _, gettext_lazy, ngettext
from django.views import View
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
                     AdjudicatorTeamConflict, N1RuleAssignment, N1RuleFinePayment,
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


# ==============================================================================
# N-1 Rule views
# ==============================================================================

class N1RuleAssignmentsView(LogActionMixin, AdministratorMixin, TournamentMixin, TemplateView):
    """N-1 rule assignments split into two sections on one page:
    institutional coverage (adjudicator → institution) and independent
    team coverage (team → adjudicator).
    """

    view_permission = Permission.VIEW_N1_RULE_ASSIGNMENTS
    edit_permission = Permission.EDIT_N1_RULE_ASSIGNMENTS
    action_log_type = ActionLogEntry.ActionType.N1_RULE_ASSIGNMENTS_EDIT
    template_name = 'n1rule_assignments.html'
    page_title = gettext_lazy("N-1 Rule Assignments")
    page_emoji = '⚖️'
    same_view = 'adjallocation-n1rule-assignments'

    def _can_edit(self):
        return has_permission(self.request.user, self.edit_permission, self.tournament)

    def _make_formset(self, fields, field_classes, queryset, prefix, data=None):
        can_edit = self._can_edit()
        FormSet = modelformset_factory(
            N1RuleAssignment,
            fields=fields,
            field_classes=field_classes,
            extra=3 * int(can_edit),
            can_delete=can_edit,
        )
        kw = {'queryset': queryset, 'prefix': prefix}
        if data is not None:
            kw['data'] = data
        return FormSet(**kw)

    def _build_inst_formset(self, data=None):
        qs = N1RuleAssignment.objects.filter(
            adjudicator__tournament=self.tournament,
            team__isnull=True,
        ).select_related('adjudicator', 'institution').order_by('institution__name', 'adjudicator__name')
        formset = self._make_formset(
            fields=('adjudicator', 'institution'),
            field_classes={'adjudicator': DedupModelChoiceField, 'institution': DedupModelChoiceField},
            queryset=qs,
            prefix='institutional',
            data=data,
        )
        all_adjs = self.tournament.adjudicator_set.order_by('name')
        all_insts = Institution.objects.order_by('name')
        can_edit = self._can_edit()
        for form in formset:
            form.fields['adjudicator'].queryset = all_adjs
            form.fields['institution'].queryset = all_insts
            if not can_edit:
                for field in form.fields.values():
                    field.disabled = True
        return formset

    def _build_indep_formset(self, data=None):
        qs = N1RuleAssignment.objects.filter(
            adjudicator__tournament=self.tournament,
            team__isnull=False,
        ).select_related('adjudicator', 'team').order_by('team__short_name')
        formset = self._make_formset(
            fields=('team', 'adjudicator'),
            field_classes={'adjudicator': DedupModelChoiceField, 'team': DedupModelChoiceField},
            queryset=qs,
            prefix='independent',
            data=data,
        )
        all_adjs = self.tournament.adjudicator_set.order_by('name')
        all_teams = self.tournament.team_set.filter(institution__isnull=True).order_by('short_name')
        can_edit = self._can_edit()
        for form in formset:
            form.fields['adjudicator'].queryset = all_adjs
            form.fields['team'].queryset = all_teams
            if not can_edit:
                for field in form.fields.values():
                    field.disabled = True
        return formset

    def get_context_data(self, inst_formset=None, indep_formset=None, **kwargs):
        if inst_formset is None:
            inst_formset = self._build_inst_formset()
        if indep_formset is None:
            indep_formset = self._build_indep_formset()
        kwargs['inst_formset'] = inst_formset
        kwargs['indep_formset'] = indep_formset
        return super().get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        inst_formset = self._build_inst_formset(data=request.POST)
        indep_formset = self._build_indep_formset(data=request.POST)

        if inst_formset.is_valid() and indep_formset.is_valid():
            inst_saved = inst_formset.save()
            indep_saved = indep_formset.save()
            nsaved = len(inst_saved) + len(indep_saved)
            ndeleted = len(inst_formset.deleted_objects) + len(indep_formset.deleted_objects)
            self.log_action()
            if nsaved > 0:
                messages.success(request, ngettext(
                    "Saved %(count)d N-1 assignment.",
                    "Saved %(count)d N-1 assignments.",
                    nsaved,
                ) % {'count': nsaved})
            if ndeleted > 0:
                messages.success(request, ngettext(
                    "Deleted %(count)d N-1 assignment.",
                    "Deleted %(count)d N-1 assignments.",
                    ndeleted,
                ) % {'count': ndeleted})
            if nsaved == 0 and ndeleted == 0:
                messages.success(request, _("No changes were made to N-1 assignments."))
            return redirect_tournament(self.same_view, self.tournament)

        return self.render_to_response(self.get_context_data(
            inst_formset=inst_formset,
            indep_formset=indep_formset,
        ))


class N1RuleStatusView(AdministratorMixin, TournamentMixin, TemplateView):

    template_name = 'n1rule_status.html'
    page_title = gettext_lazy("N-1 Rule Status")
    page_emoji = '📊'
    view_permission = Permission.VIEW_N1_RULE_ASSIGNMENTS

    def post(self, request, *args, **kwargs):
        from django.http import JsonResponse
        if not has_permission(request.user, self.view_permission, self.tournament):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        try:
            m = int(request.POST.get('m_rounds', 3))
            strict = request.POST.get('strict_mode') == '1'
            n_equals_n = request.POST.get('institution_n_equals_n') == '1'
            self.tournament.preferences['n1_rule__n1_rule_min_rounds'] = m
            self.tournament.preferences['n1_rule__n1_rule_strict_institutions'] = strict
            self.tournament.preferences['n1_rule__n1_rule_institution_n_equals_n'] = n_equals_n
            return JsonResponse({'ok': True})
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid values'}, status=400)

    def get_context_data(self, **kwargs):
        from django.middleware.csrf import get_token
        from participants.models import Institution
        from tournaments.models import Round

        tournament = self.tournament
        m = tournament.pref('n1_rule_min_rounds')
        strict = tournament.pref('n1_rule_strict_institutions')
        n_equals_n = tournament.pref('n1_rule_institution_n_equals_n')

        assignments = list(N1RuleAssignment.objects.filter(
            adjudicator__tournament=tournament,
        ).select_related('adjudicator', 'adjudicator__institution', 'institution', 'team'))

        relevant_adj_ids = [a.adjudicator_id for a in assignments]

        rounds_judged = {}
        if relevant_adj_ids:
            rows = DebateAdjudicator.objects.filter(
                adjudicator_id__in=relevant_adj_ids,
                debate__round__stage=Round.Stage.PRELIMINARY,
                debate__round__tournament=tournament,
            ).values('adjudicator_id', 'debate__round_id').distinct()
            for row in rows:
                adj_id = row['adjudicator_id']
                rounds_judged[adj_id] = rounds_judged.get(adj_id, 0) + 1

        inst_ids = list(tournament.team_set.filter(
            institution__isnull=False,
        ).values_list('institution_id', flat=True).distinct())

        fine_payments = {
            fp.institution_id: fp.fines_paid
            for fp in N1RuleFinePayment.objects.filter(
                tournament=tournament,
                institution__isnull=False,
            )
        }
        team_fine_payments = {
            fp.team_id: fp.fines_paid
            for fp in N1RuleFinePayment.objects.filter(
                tournament=tournament,
                team__isnull=False,
            )
        }

        institutions_data = []
        for inst in Institution.objects.filter(id__in=inst_ids).order_by('name'):
            team_count = tournament.team_set.filter(institution=inst).count()
            inst_assignments = [a for a in assignments
                                if (a.institution_id or a.adjudicator.institution_id) == inst.id and
                                a.team_id is None]
            judge_data = [
                {
                    'adj_id': a.adjudicator_id,
                    'adj_name': a.adjudicator.name,
                    'rounds_judged': rounds_judged.get(a.adjudicator_id, 0),
                }
                for a in inst_assignments
            ]
            institutions_data.append({
                'id': inst.id,
                'name': inst.name,
                'team_count': team_count,
                'assignments': judge_data,
                'fines_paid': fine_payments.get(inst.id, 0),
            })

        independent_teams_data = []
        for team in tournament.team_set.filter(institution__isnull=True).order_by('short_name'):
            assignment = next((a for a in assignments if a.team_id == team.id), None)
            if assignment:
                assigned_adj = {
                    'id': assignment.adjudicator_id,
                    'name': assignment.adjudicator.name,
                    'rounds_judged': rounds_judged.get(assignment.adjudicator_id, 0),
                }
            else:
                assigned_adj = None

            independent_teams_data.append({
                'id': team.id,
                'name': team.short_name,
                'assigned_adj': assigned_adj,
                'fines_paid': team_fine_payments.get(team.id, 0),
            })

        kwargs['institutions'] = json.dumps(institutions_data)
        kwargs['independent_teams'] = json.dumps(independent_teams_data)
        kwargs['initial_m_rounds'] = m
        kwargs['initial_strict_mode'] = json.dumps(strict)
        kwargs['initial_institution_n_equals_n'] = json.dumps(n_equals_n)
        kwargs['csrf_token'] = get_token(self.request)
        return super().get_context_data(**kwargs)


class N1RuleFinePaymentView(LogActionMixin, AdministratorMixin, TournamentMixin, View):
    """AJAX endpoint to update the fine payment count for an institution or independent team."""

    action_log_type = ActionLogEntry.ActionType.N1_RULE_FINES_EDIT
    view_permission = Permission.VIEW_N1_RULE_ASSIGNMENTS
    edit_permission = Permission.EDIT_N1_RULE_ASSIGNMENTS

    def post(self, request, *args, **kwargs):
        from django.http import JsonResponse
        if not has_permission(request.user, self.edit_permission, self.tournament):
            return JsonResponse({'error': 'Permission denied'}, status=403)

        try:
            data = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        try:
            fines_paid = max(0, int(data.get('fines_paid', 0)))
        except (TypeError, ValueError):
            return JsonResponse({'error': 'Invalid fines_paid value'}, status=400)

        institution_id = data.get('institution_id')
        team_id = data.get('team_id')

        if institution_id:
            obj, _ = N1RuleFinePayment.objects.get_or_create(
                tournament=self.tournament,
                institution_id=institution_id,
                defaults={'fines_paid': 0},
            )
            obj.fines_paid = fines_paid
            obj.save(update_fields=['fines_paid'])
        elif team_id:
            obj, _ = N1RuleFinePayment.objects.get_or_create(
                tournament=self.tournament,
                team_id=team_id,
                defaults={'fines_paid': 0},
            )
            obj.fines_paid = fines_paid
            obj.save(update_fields=['fines_paid'])
        else:
            return JsonResponse({'error': 'institution_id or team_id required'}, status=400)

        self.log_action()
        return JsonResponse({'ok': True, 'fines_paid': fines_paid})
