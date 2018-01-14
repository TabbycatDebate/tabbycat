import json
import logging

from django.db import transaction
from django.db.models import Q
from django.views.generic.base import TemplateView, View
from django.http import JsonResponse
from django.utils.functional import cached_property
from django.utils.translation import ugettext as _

from actionlog.mixins import LogActionMixin
from actionlog.models import ActionLogEntry
from breakqual.models import BreakCategory
from draw.models import Debate
from participants.models import Adjudicator, Region
from participants.prefetch import populate_feedback_scores
from tournaments.models import Round
from tournaments.mixins import DrawForDragAndDropMixin, RoundMixin
from tournaments.views import BaseSaveDragAndDropDebateJsonView
from utils.mixins import AdministratorMixin
from utils.views import BadJsonRequestError, JsonDataResponsePostView

from .allocator import allocate_adjudicators
from .consensushungarian import ConsensusHungarianAllocator
from .hungarian import HungarianAllocator
from .models import DebateAdjudicator
from .utils import get_clashes, get_histories

from utils.misc import reverse_round

logger = logging.getLogger(__name__)


class AdjudicatorAllocationMixin(DrawForDragAndDropMixin, AdministratorMixin):

    @cached_property
    def get_clashes(self):
        return get_clashes(self.get_tournament(), self.get_round())

    @cached_property
    def get_histories(self):
        return get_histories(self.get_tournament(), self.get_round())

    def get_unallocated_adjudicators(self):
        round = self.get_round()
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
    auto_url = "adjudicators-auto-allocate"
    save_url = "save-debate-panel"

    def get_regions_info(self):
        # Need to extract and annotate regions for the allcoation actions key
        all_regions = [r.serialize for r in Region.objects.order_by('id')]
        for i, r in enumerate(all_regions):
            r['class'] = i
        return all_regions

    def get_categories_info(self):
        # Need to extract and annotate categories for the allcoation actions key
        all_bcs = [c.serialize for c in BreakCategory.objects.filter(
            tournament=self.get_tournament()).order_by('id')]
        for i, bc in enumerate(all_bcs):
            bc['class'] = i
        return all_bcs

    def annotate_round_info(self, round_info):
        t = self.get_tournament()
        r = self.get_round()
        round_info['updateImportanceURL'] = reverse_round('save-debate-importance', r)
        round_info['scoreMin'] = t.pref('adj_min_score')
        round_info['scoreMax'] = t.pref('adj_max_score')
        round_info['scoreForVote'] = t.pref('adj_min_voting_score')
        round_info['allowDuplicateAllocations'] = t.pref('duplicate_adjs')
        round_info['regions'] = self.get_regions_info()
        round_info['categories'] = self.get_categories_info()
        return round_info

    def get_context_data(self, **kwargs):
        t = self.get_tournament()
        kwargs['vueUnusedAdjudicators'] = self.get_unallocated_adjudicators()
        kwargs['showAllocationIntro'] = t.pref('show_allocation_intro')
        # This is meant to be shown once only; so we set false if true
        if t.pref('show_allocation_intro'):
            t.preferences['ui_options__show_allocation_intro'] = False

        return super().get_context_data(**kwargs)


class CreateAutoAllocation(LogActionMixin, AdjudicatorAllocationMixin, JsonDataResponsePostView):

    action_log_type = ActionLogEntry.ACTION_TYPE_ADJUDICATORS_AUTO

    def post_data(self):
        round = self.get_round()
        self.log_action()
        if round.draw_status == Round.STATUS_RELEASED:
            info = _("Draw is already released, unrelease draw to redo auto-allocations.")
            logger.warning(info)
            raise BadJsonRequestError(info)
        if round.draw_status != Round.STATUS_CONFIRMED:
            info = _("Draw is not confirmed, confirm draw to run auto-allocations.")
            logger.warning(info)
            raise BadJsonRequestError(info)

        if self.get_tournament().pref('ballots_per_debate') == 'per-adj':
            allocator_class = HungarianAllocator
        else:
            allocator_class = ConsensusHungarianAllocator

        allocate_adjudicators(self.get_round(), allocator_class)
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

        with transaction.atomic(): # Speed up the saving by using a single query
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
        adjs = Adjudicator.objects.filter(Q(tournament=self.get_tournament()) | Q(tournament__isnull=True), id__in=adj_ids)
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
