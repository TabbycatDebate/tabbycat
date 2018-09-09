import json
import logging

from django.contrib import messages
from django.db.models import Q
from django.forms import ModelChoiceField
from django.views.generic.base import TemplateView, View
from django.http import JsonResponse
from django.utils.functional import cached_property
from django.utils.translation import gettext as _, gettext_lazy, ngettext

from actionlog.mixins import LogActionMixin
from actionlog.models import ActionLogEntry
from breakqual.models import BreakCategory
from draw.models import Debate
from participants.models import Adjudicator, Region
from participants.prefetch import populate_feedback_scores
from tournaments.models import Round
from tournaments.mixins import DrawForDragAndDropMixin, RoundMixin, TournamentMixin
from tournaments.views import BaseSaveDragAndDropDebateJsonView
from utils.misc import redirect_tournament, reverse_tournament
from utils.mixins import AdministratorMixin
from utils.views import BadJsonRequestError, JsonDataResponsePostView, ModelFormSetView

from .allocator import allocate_adjudicators
from .hungarian import ConsensusHungarianAllocator, VotingHungarianAllocator
from .models import (AdjudicatorAdjudicatorConflict, AdjudicatorConflict,
                     AdjudicatorInstitutionConflict, DebateAdjudicator)
from .utils import get_clashes, get_histories

from utils.misc import reverse_round

logger = logging.getLogger(__name__)


class AdjudicatorAllocationMixin(DrawForDragAndDropMixin, AdministratorMixin):

    @cached_property
    def get_clashes(self):
        return get_clashes(self.tournament, self.round)

    @cached_property
    def get_histories(self):
        return get_histories(self.tournament, self.round)

    def get_unallocated_adjudicators(self):
        round = self.round
        unused_adj_instances = round.unused_adjudicators().select_related('institution__region')
        populate_feedback_scores(unused_adj_instances)
        unused_adjs = [a.serialize(round) for a in unused_adj_instances]
        unused_adjs = [self.annotate_region_classes(a) for a in unused_adjs]
        unused_adjs = [self.annotate_conflicts(a, 'for_adjs') for a in unused_adjs]
        return json.dumps(unused_adjs)

    def annotate_conflicts(self, serialized_adj_or_team, for_type):
        adj_or_team_id = serialized_adj_or_team['id']
        try:
            serialized_adj_or_team['conflicts']['clashes'] = self.get_clashes[for_type][adj_or_team_id]
        except KeyError:
            serialized_adj_or_team['conflicts']['clashes'] = {}
        try:
            serialized_adj_or_team['conflicts']['histories'] = self.get_histories[for_type][adj_or_team_id]
        except KeyError:
            serialized_adj_or_team['conflicts']['histories'] = {}

        if for_type == 'for_teams':
            # Teams don't show in AdjudicatorInstitutionConflict; need to
            # add own institutional clash manually to reverse things
            if serialized_adj_or_team['institution']:
                ic = [{'id': serialized_adj_or_team['institution']['id']}]
                serialized_adj_or_team['conflicts']['clashes']['institution'] = ic

        return serialized_adj_or_team

    def annotate_draw(self, draw, serialised_draw):
        # Need to unique-ify/reorder break categories/regions for consistent CSS
        for debate in serialised_draw:
            for da in debate['debateAdjudicators']:
                da['adjudicator'] = self.annotate_conflicts(da['adjudicator'], 'for_adjs')
                da['adjudicator'] = self.annotate_region_classes(da['adjudicator'])
            for dt in debate['debateTeams']:
                if not dt['team']:
                    continue
                dt['team'] = self.annotate_conflicts(dt['team'], 'for_teams')

        return super().annotate_draw(draw, serialised_draw)


class EditAdjudicatorAllocationView(AdjudicatorAllocationMixin, TemplateView):

    template_name = 'edit_adjudicators.html'
    auto_url = "adjallocation-auto-allocate"
    save_url = "adjallocation-save-debate-panel"

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
        round_info['updateImportanceURL'] = reverse_round('adjallocation-save-debate-importance', self.round)
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


class CreateAutoAllocation(LogActionMixin, AdjudicatorAllocationMixin, JsonDataResponsePostView):

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

        allocate_adjudicators(self.round, allocator_class)
        return {
            'debates': self.get_draw(),
            'unallocatedAdjudicators': self.get_unallocated_adjudicators()
        }


class SaveDebateImportance(AdministratorMixin, RoundMixin, LogActionMixin, View):
    action_log_type = ActionLogEntry.ACTION_TYPE_DEBATE_IMPORTANCE_EDIT

    def post(self, request, *args, **kwargs):
        body = self.request.body.decode('utf-8')
        posted_info = json.loads(body)
        priorities = posted_info['priorities']

        for debate_id, priority in priorities.items():
            Debate.objects.filter(pk=debate_id).update(importance=priority)

        self.log_action()
        return JsonResponse(json.dumps(priorities), safe=False)


class SaveDebatePanel(BaseSaveDragAndDropDebateJsonView):
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

    def get_formset_queryset(self):
        return self.formset_model.objects.filter(
                adjudicator__tournament=self.tournament).order_by(
                'adjudicator__name')

    def get_formset(self):
        formset = super().get_formset()
        all_adjs = self.tournament.adjudicator_set.order_by('name').all()
        for form in formset:
            form.fields['adjudicator'].queryset = all_adjs # Order list by alpha
        return formset

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
    formset_model = AdjudicatorConflict
    page_title = gettext_lazy("Adjudicator-Team Conflicts")
    save_text = gettext_lazy("Save Adjudicator-Team Conflicts")
    same_view = 'adjallocation-conflicts-adj-team'
    formset_factory_kwargs = BaseAdjudicatorConflictsView.formset_factory_kwargs.copy()
    formset_factory_kwargs.update({
        'fields': ('adjudicator', 'team'),
        'field_classes': {'team': TeamChoiceField},
    })

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
    formset_factory_kwargs.update({'fields': ('adjudicator', 'conflict_adjudicator')})

    def get_formset(self):
        formset = super().get_formset()
        all_adjs = self.tournament.adjudicator_set.order_by('name').all()
        for form in formset:
            form.fields['conflict_adjudicator'].queryset = all_adjs # Order list by alpha
        return formset

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
