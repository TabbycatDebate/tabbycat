import json
import logging

from django.contrib import messages
from django.db.models import Prefetch, Q
from django.forms import ModelChoiceField
from django.views.generic.base import TemplateView, View
from django.http import JsonResponse
from django.utils.functional import cached_property
from django.utils.translation import gettext as _, gettext_lazy, ngettext

from actionlog.mixins import LogActionMixin
from actionlog.models import ActionLogEntry
from availability.utils import annotate_availability
from breakqual.models import BreakCategory
from draw.models import Debate
from participants.models import Adjudicator, Region
from participants.prefetch import populate_feedback_scores
from tournaments.models import Round
from tournaments.mixins import DebateDragAndDropMixin, LegacyDrawForDragAndDropMixin, RoundMixin, TournamentMixin
from tournaments.views import BaseSaveDragAndDropDebateJsonView
from utils.misc import ranks_dictionary, redirect_tournament, reverse_tournament
from utils.mixins import AdministratorMixin
from utils.views import BadJsonRequestError, JsonDataResponsePostView, ModelFormSetView

from .allocators import legacy_allocate_adjudicators
from .allocators.hungarian import ConsensusHungarianAllocator, VotingHungarianAllocator
from .conflicts import ConflictsInfo, HistoryInfo
from .models import (AdjudicatorAdjudicatorConflict, AdjudicatorInstitutionConflict,
                     AdjudicatorTeamConflict, DebateAdjudicator,
                     PreformedPanelAdjudicator, TeamInstitutionConflict)
from .serializers import EditDebateAdjsDebateSerializer, EditPanelAdjsPanelSerializer, EditPanelOrDebateAdjSerializer

from utils.misc import reverse_round

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
        info['highlights']['rank'] = ranks_dictionary(self.tournament)
        regions = [{'pk': r.id, 'fields': {'name': r.name}} for r in Region.objects.all()]
        info['highlights']['region'] = regions
        info['adjMinScore'] = self.tournament.pref('adj_min_score')
        info['adjMaxScore'] = self.tournament.pref('adj_max_score')
        allocation_preferences = [
            'draw_rules__adj_min_voting_score',
            'draw_rules__adj_conflict_penalty',
            'draw_rules__adj_history_penalty',
            'draw_rules__preformed_panel_mismatch_penalty',
            'draw_rules__no_trainee_position',
            'draw_rules__no_panellist_position'
        ]
        info['allocationSettings'] = {}
        for key in allocation_preferences:
            info['allocationSettings'][key] = self.tournament.preferences[key]

        info['clashes'] = self.get_adjudicator_conflicts()
        info['histories'] = self.get_history_conflicts()
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

    def get_extra_info(self):
        info = super().get_extra_info()
        return info

    def debates_or_panels_factory(self, debates):
        return EditDebateAdjsDebateSerializer(
            debates, many=True, context={'sides': self.tournament.sides,
                                         'round': self.round})


class EditPanelAdjudicatorsView(BaseEditDebateOrPanelAdjudicatorsView):
    template_name = "edit_panel_adjudicators.html"
    page_title = gettext_lazy("Edit Panels")

    def get_extra_info(self):
        info = super().get_extra_info()
        info['backUrl'] = reverse_tournament('panel-adjudicators-index',
                                             self.tournament)  # Override
        info['backLabel'] = _("Return to Panels Overview")
        return info

    def get_draw_or_panels_objects(self):
        panels = self.round.preformedpanel_set.all().prefetch_related(
            Prefetch('preformedpaneladjudicator_set',
                queryset=PreformedPanelAdjudicator.objects.select_related('adjudicator'))
        )
        return panels

    def debates_or_panels_factory(self, panels):
        return EditPanelAdjsPanelSerializer(panels, many=True,
                                            context={'round': self.round})


class PanelAdjudicatorsIndexView(TemplateView, AdministratorMixin):
    template_name = "preformed_index.html"
    page_title = gettext_lazy("Preformed Panels")


# ==============================================================================
# Legacy Adjudicator Allocation Views
# ==============================================================================

class LegacyAdjudicatorAllocationMixin(LegacyDrawForDragAndDropMixin, AdministratorMixin):
    """@deprecate when legacy drag and drop UIs removed"""

    @cached_property
    def conflicts_and_history(self):
        conflicts = ConflictsInfo(teams=self.tournament.team_set.all(),
            adjudicators=self.tournament.adjudicator_set.all())
        team_conflicts, adj_conflicts = conflicts.serialized_by_participant()
        history = HistoryInfo(self.round)
        team_history, adj_history = history.serialized_by_participant()

        teams_combined = {}
        for team_id, conflicts in team_conflicts.items():
            teams_combined[team_id] = {'clashes': conflicts}
        for team_id, history in team_history.items():
            teams_combined.setdefault(team_id, {})['histories'] = history

        adjs_combined = {}
        for adj_id, conflicts in adj_conflicts.items():
            adjs_combined[adj_id] = {'clashes': conflicts}
        for adj_id, history in adj_history.items():
            adjs_combined.setdefault(adj_id, {})['histories'] = history

        return teams_combined, adjs_combined

    def get_unallocated_adjudicators(self):
        round = self.round
        unused_adj_instances = round.unused_adjudicators().select_related('institution__region')
        populate_feedback_scores(unused_adj_instances)
        unused_adjs = [a.serialize(round) for a in unused_adj_instances]

        _, adj_conflicts = self.conflicts_and_history
        for adj in unused_adjs:
            self.annotate_region_classes(adj)
            adj['conflicts'] = adj_conflicts[adj['id']]

        return json.dumps(unused_adjs)

    def annotate_draw(self, draw, serialised_draw):
        # Need to unique-ify/reorder break categories/regions for consistent CSS

        team_conflicts, adj_conflicts = self.conflicts_and_history

        for debate in serialised_draw:
            for da in debate['debateAdjudicators']:
                da['adjudicator']['conflicts'] = adj_conflicts[da['adjudicator']['id']]
                self.annotate_region_classes(da['adjudicator'])
            for dt in debate['debateTeams']:
                if not dt['team']:
                    continue
                dt['team']['conflicts'] = team_conflicts[dt['team']['id']]

        return super().annotate_draw(draw, serialised_draw)


class LegacyEditAdjudicatorAllocationView(LegacyAdjudicatorAllocationMixin, TemplateView):
    """@deprecate when legacy drag and drop UIs removed"""

    template_name = 'legacy_edit_adjudicators.html'
    auto_url = "legacy-adjallocation-auto-allocate"
    save_url = "legacy-adjallocation-save-debate-panel"

    def get_regions_info(self):
        # Need to extract and annotate regions for the allcoation actions key
        all_regions = [r.serialize for r in Region.objects.order_by('id')]
        for i, r in enumerate(all_regions):
            r['class'] = i
        return all_regions

    def get_categories_info(self):
        # Need to extract and annotate categories for the allcoation actions key
        all_bcs = [c.serialize for c in BreakCategory.objects.filter(
            tournament=self.tournament).order_by('id')]
        for i, bc in enumerate(all_bcs):
            bc['class'] = i
        return all_bcs

    def get_round_info(self):
        round_info = super().get_round_info()
        round_info['updateImportanceURL'] = reverse_round('legacy-adjallocation-save-debate-importance', self.round)
        round_info['scoreMin'] = self.tournament.pref('adj_min_score')
        round_info['scoreMax'] = self.tournament.pref('adj_max_score')
        round_info['scoreForVote'] = self.tournament.pref('adj_min_voting_score')
        round_info['allowDuplicateAllocations'] = self.tournament.pref('duplicate_adjs')
        round_info['regions'] = self.get_regions_info()
        round_info['categories'] = self.get_categories_info()
        return round_info

    def get_context_data(self, **kwargs):
        kwargs['vueUnusedAdjudicators'] = self.get_unallocated_adjudicators()
        kwargs['showAllocationIntro'] = self.tournament.pref('show_allocation_intro')
        # This is meant to be shown once only; so we set false if true
        if self.tournament.pref('show_allocation_intro'):
            self.tournament.preferences['ui_options__show_allocation_intro'] = False

        return super().get_context_data(**kwargs)


class LegacyCreateAutoAllocation(LogActionMixin, LegacyAdjudicatorAllocationMixin, JsonDataResponsePostView):
    """@deprecate when legacy drag and drop UIs removed"""

    action_log_type = ActionLogEntry.ACTION_TYPE_ADJUDICATORS_AUTO

    def post_data(self):
        round = self.round
        self.log_action()
        if round.draw_status == Round.STATUS_RELEASED:
            info = _("Draw is already released, unrelease draw to redo auto-allocations.")
            logger.warning(info)
            raise BadJsonRequestError(info)
        if round.draw_status != Round.STATUS_CONFIRMED:
            info = _("Draw is not confirmed, confirm draw to run auto-allocations.")
            logger.warning(info)
            raise BadJsonRequestError(info)

        if round.ballots_per_debate == 'per-adj':
            allocator_class = VotingHungarianAllocator
        else:
            allocator_class = ConsensusHungarianAllocator

        legacy_allocate_adjudicators(self.round, allocator_class)
        return {
            'debates': self.get_draw(),
            'unallocatedAdjudicators': self.get_unallocated_adjudicators()
        }


class LegacySaveDebateImportance(AdministratorMixin, RoundMixin, LogActionMixin, View):
    """@deprecate when legacy drag and drop UIs removed"""
    action_log_type = ActionLogEntry.ACTION_TYPE_DEBATE_IMPORTANCE_EDIT

    def post(self, request, *args, **kwargs):
        body = self.request.body.decode('utf-8')
        posted_info = json.loads(body)
        priorities = posted_info['priorities']

        for debate_id, priority in priorities.items():
            Debate.objects.filter(pk=debate_id).update(importance=priority)

        self.log_action()
        return JsonResponse(json.dumps(priorities), safe=False)


class LegacySaveDebatePanel(BaseSaveDragAndDropDebateJsonView):
    """@deprecate when legacy drag and drop UIs removed"""
    action_log_type = ActionLogEntry.ACTION_TYPE_ADJUDICATORS_SAVE

    def get_moved_item(self, id):
        return Adjudicator.objects.get(pk=id)

    def modify_debate(self, debate, posted_debate):
        posted_debateadjudicators = posted_debate['debateAdjudicators']

        # Delete adjudicators who aren't in the posted information
        adj_ids = [da['adjudicator']['id'] for da in posted_debateadjudicators]
        delete_count, deleted = debate.debateadjudicator_set.exclude(adjudicator_id__in=adj_ids).delete()
        logger.debug("Deleted %d debate adjudicators from [%s]", delete_count, debate.matchup)

        # Check all the adjudicators are part of the tournament
        adjs = Adjudicator.objects.filter(Q(tournament=self.tournament) | Q(tournament__isnull=True), id__in=adj_ids)
        if len(adjs) != len(posted_debateadjudicators):
            raise BadJsonRequestError(_("Not all adjudicators specified are associated with the tournament."))
        adj_name_lookup = {adj.id: adj.name for adj in adjs}  # for debugging messages

        # Update or create positions of adjudicators in debate
        for debateadj in posted_debateadjudicators:
            adj_id = debateadj['adjudicator']['id']
            adjtype = debateadj['position']
            obj, created = DebateAdjudicator.objects.update_or_create(debate=debate,
                    adjudicator_id=adj_id, defaults={'type': adjtype})
            logger.debug("%s debate adjudicator: %s is now %s in [%s]", "Created" if created else "Updated",
                    adj_name_lookup[adj_id], obj.get_type_display(), debate.matchup)

        return debate


# ==============================================================================
# Conflict formset views
# ==============================================================================

class TeamChoiceField(ModelChoiceField):

    def label_from_instance(self, obj):
        return obj.short_name


class BaseAdjudicatorConflictsView(LogActionMixin, AdministratorMixin, TournamentMixin, ModelFormSetView):

    template_name = 'edit_conflicts.html'
    page_emoji = "🔶"

    formset_factory_kwargs = {
        'extra': 10,
        'can_delete': True,
    }

    def get_context_data(self, **kwargs):
        kwargs['save_text'] = self.save_text
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

    action_log_type = ActionLogEntry.ACTION_TYPE_CONFLICTS_ADJ_TEAM_EDIT
    formset_model = AdjudicatorTeamConflict
    page_title = gettext_lazy("Adjudicator-Team Conflicts")
    save_text = gettext_lazy("Save Adjudicator-Team Conflicts")
    same_view = 'adjallocation-conflicts-adj-team'
    formset_factory_kwargs = BaseAdjudicatorConflictsView.formset_factory_kwargs.copy()
    formset_factory_kwargs.update({
        'fields': ('adjudicator', 'team'),
        'field_classes': {'team': TeamChoiceField},
    })

    def get_formset(self):
        formset = super().get_formset()
        all_adjs = self.tournament.adjudicator_set.order_by('name').all()
        all_teams = self.tournament.team_set.order_by('short_name').all()
        for form in formset:
            form.fields['adjudicator'].queryset = all_adjs  # order alphabetically
            form.fields['team'].queryset = all_teams        # order alphabetically
        return formset

    def get_formset_queryset(self):
        return self.formset_model.objects.filter(
            adjudicator__tournament=self.tournament
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

    action_log_type = ActionLogEntry.ACTION_TYPE_CONFLICTS_ADJ_ADJ_EDIT
    formset_model = AdjudicatorAdjudicatorConflict
    page_title = gettext_lazy("Adjudicator-Adjudicator Conflicts")
    save_text = gettext_lazy("Save Adjudicator-Adjudicator Conflicts")
    same_view = 'adjallocation-conflicts-adj-adj'
    formset_factory_kwargs = BaseAdjudicatorConflictsView.formset_factory_kwargs.copy()
    formset_factory_kwargs.update({'fields': ('adjudicator1', 'adjudicator2')})

    def get_formset(self):
        formset = super().get_formset()
        all_adjs = self.tournament.adjudicator_set.order_by('name').all()
        for form in formset:
            form.fields['adjudicator1'].queryset = all_adjs  # order alphabetically
            form.fields['adjudicator2'].queryset = all_adjs  # order alphabetically
        return formset

    def get_formset_queryset(self):
        return self.formset_model.objects.filter(
            adjudicator1__tournament=self.tournament
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

    action_log_type = ActionLogEntry.ACTION_TYPE_CONFLICTS_ADJ_INST_EDIT
    formset_model = AdjudicatorInstitutionConflict
    page_title = gettext_lazy("Adjudicator-Institution Conflicts")
    save_text = gettext_lazy("Save Adjudicator-Institution Conflicts")
    same_view = 'adjallocation-conflicts-adj-inst'
    formset_factory_kwargs = BaseAdjudicatorConflictsView.formset_factory_kwargs.copy()
    formset_factory_kwargs.update({'fields': ('adjudicator', 'institution')})

    def get_formset(self):
        formset = super().get_formset()
        all_adjs = self.tournament.adjudicator_set.order_by('name').all()
        for form in formset:
            form.fields['adjudicator'].queryset = all_adjs  # order alphabetically
        return formset

    def get_formset_queryset(self):
        return self.formset_model.objects.filter(
            adjudicator__tournament=self.tournament
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

    action_log_type = ActionLogEntry.ACTION_TYPE_CONFLICTS_TEAM_INST_EDIT
    formset_model = TeamInstitutionConflict
    page_title = gettext_lazy("Team-Institution Conflicts")
    save_text = gettext_lazy("Save Team-Institution Conflicts")
    same_view = 'adjallocation-conflicts-team-inst'
    formset_factory_kwargs = BaseAdjudicatorConflictsView.formset_factory_kwargs.copy()
    formset_factory_kwargs.update({
        'fields': ('team', 'institution'),
        'field_classes': {'team': TeamChoiceField},
    })

    def get_formset(self):
        formset = super().get_formset()
        all_teams = self.tournament.team_set.order_by('short_name').all()
        for form in formset:
            form.fields['team'].queryset = all_teams  # order alphabetically
        return formset

    def get_formset_queryset(self):
        return self.formset_model.objects.filter(
            team__tournament=self.tournament
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
