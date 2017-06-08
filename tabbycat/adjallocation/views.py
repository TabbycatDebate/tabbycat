import json
import logging

from django.views.generic.base import TemplateView, View
from django.http import HttpResponse, HttpResponseBadRequest

from actionlog.mixins import LogActionMixin
from actionlog.models import ActionLogEntry
from breakqual.models import BreakCategory
from draw.models import Debate
from participants.models import Region
# from participants.utils import regions_ordered
from tournaments.models import Round
from tournaments.mixins import DrawForDragAndDropMixin, RoundMixin
from utils.mixins import JsonDataResponsePostView, SuperuserRequiredMixin

from .allocator import allocate_adjudicators
from .hungarian import HungarianAllocator
from .models import DebateAdjudicator

from utils.misc import reverse_round

logger = logging.getLogger(__name__)


class AllocationViewBase(DrawForDragAndDropMixin, SuperuserRequiredMixin):

    def get_unallocated_adjudicators(self):
        round = self.get_round()
        unused_adjs = [a.serialize(round) for a in round.unused_adjudicators()]
        unused_adjs = [self.annotate_region_classes(a) for a in unused_adjs]
        return json.dumps(unused_adjs)


class EditAdjudicatorAllocationView(AllocationViewBase, TemplateView):

    template_name = 'edit_adjudicators.html'

    def annotate_round_info(self, round_info):
        t = self.get_tournament()
        r = self.get_round()
        round_info['autoUrl'] = reverse_round('adjudicators-auto-allocate', r)
        round_info['updateImportanceURL'] = reverse_round('save-debate-importance', r)
        round_info['updatePanelURL'] = reverse_round('save-debate-panel', r)
        round_info['scoreMin'] = t.pref('adj_min_score')
        round_info['scoreMax'] = t.pref('adj_max_score')
        round_info['scoreForVote'] = t.pref('adj_min_voting_score')
        round_info['allowDuplicateAllocations'] = t.pref('duplicate_adjs')
        round_info['regions'] = self.get_regions_info()
        round_info['categories'] = self.get_categories_info()
        return round_info

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

    def get_context_data(self, **kwargs):
        # regions = regions_ordered(t)
        # categories = categories_ordered(t)
        # adjs, teams = populate_conflicts(adjs, teams)
        # adjs, teams = populate_histories(adjs, teams, t, r)
        kwargs['vueUnusedAdjudicators'] = self.get_unallocated_adjudicators()
        return super().get_context_data(**kwargs)


class CreateAutoAllocation(LogActionMixin, AllocationViewBase, JsonDataResponsePostView):

    action_log_type = ActionLogEntry.ACTION_TYPE_ADJUDICATORS_AUTO

    def post_data(self):
        allocate_adjudicators(self.get_round(), HungarianAllocator)
        return {
            'debates': self.get_draw(),
            'unallocatedAdjudicators': self.get_unallocated_adjudicators()
        }

    def post(self, request, *args, **kwargs):
        round = self.get_round()
        if round.draw_status == Round.STATUS_RELEASED:
            return HttpResponseBadRequest("Draw is already released, unrelease draw to redo auto-allocations.")
        if round.draw_status != Round.STATUS_CONFIRMED:
            return HttpResponseBadRequest("Draw is not confirmed, confirm draw to run auto-allocations.")
        self.log_action()
        return super().post(request, *args, **kwargs)


class SaveDebateInfo(SuperuserRequiredMixin, RoundMixin, LogActionMixin, View):
    pass


class SaveDebateImportance(SaveDebateInfo):
    action_log_type = ActionLogEntry.ACTION_TYPE_DEBATE_IMPORTANCE_EDIT

    def post(self, request, *args, **kwargs):
        debate_id = request.POST.get('debate_id')
        debate_importance = request.POST.get('importance')

        debate = Debate.objects.get(pk=debate_id)
        debate.importance = debate_importance
        debate.save()

        return HttpResponse()


class SaveDebatePanel(SaveDebateInfo):
    action_log_type = ActionLogEntry.ACTION_TYPE_ADJUDICATORS_SAVE

    def post(self, request, *args, **kwargs):
        debate_id = request.POST.get('debate_id')
        debate_panel = json.loads(request.POST.get('panel'))

        to_delete = DebateAdjudicator.objects.filter(debate_id=debate_id).exclude(
                adjudicator_id__in=[da['id'] for da in debate_panel])
        for debateadj in to_delete:
            logger.info("deleted %s" % debateadj)
        to_delete.delete()

        for da in debate_panel:
            debateadj, created = DebateAdjudicator.objects.update_or_create(debate_id=debate_id,
                    adjudicator_id=da['id'], defaults={'type': da['position']})
            logger.info("%s %s" % ("created" if created else "updated", debateadj))

        return HttpResponse()
