import json
import logging

from django.views.generic.base import TemplateView, View
from django.http import HttpResponseBadRequest, JsonResponse
from django.utils.functional import cached_property

from actionlog.mixins import LogActionMixin
from actionlog.models import ActionLogEntry
from breakqual.models import BreakCategory
from draw.models import Debate
from participants.models import Adjudicator, Region
# from participants.utils import regions_ordered
from tournaments.models import Round
from tournaments.mixins import DrawForDragAndDropMixin, RoundMixin, SaveDragAndDropDebateMixin
from utils.mixins import JsonDataResponsePostView, SuperuserRequiredMixin

from .allocator import allocate_adjudicators
from .hungarian import HungarianAllocator
from .models import DebateAdjudicator
from .utils import get_clashes, get_histories

from utils.misc import reverse_round

logger = logging.getLogger(__name__)


class AdjudicatorAllocationViewBase(DrawForDragAndDropMixin, SuperuserRequiredMixin):

    @cached_property
    def get_clashes(self):
        return get_clashes(self.get_tournament(), self.get_round())

    @cached_property
    def get_histories(self):
        return get_histories(self.get_tournament(), self.get_round())

    def get_unallocated_adjudicators(self):
        round = self.get_round()
        unused_adjs = [a.serialize(round) for a in round.unused_adjudicators()]
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
            # add own institution manually to reverse things
            institution = serialized_adj_or_team['institution']['id']
            serialized_adj_or_team['conflicts']['clashes']['institution'] = [institution]

        return serialized_adj_or_team

    def annotate_draw(self, draw, serialised_draw):
        # Need to unique-ify/reorder break categories/regions for consistent CSS
        for debate in serialised_draw:
            for panellist in debate['panel']:
                panellist['adjudicator'] = self.annotate_conflicts(panellist['adjudicator'], 'for_adjs')
                panellist['adjudicator'] = self.annotate_region_classes(panellist['adjudicator'])
            for (position, team) in debate['teams'].items():
                team = self.annotate_conflicts(team, 'for_teams')

        return super().annotate_draw(draw, serialised_draw)


class EditAdjudicatorAllocationView(AdjudicatorAllocationViewBase, TemplateView):

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
        kwargs['vueUnusedAdjudicators'] = self.get_unallocated_adjudicators()
        return super().get_context_data(**kwargs)


class CreateAutoAllocation(LogActionMixin, AdjudicatorAllocationViewBase, JsonDataResponsePostView):

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


class SaveDebateImportance(SuperuserRequiredMixin, RoundMixin, LogActionMixin, View):
    action_log_type = ActionLogEntry.ACTION_TYPE_DEBATE_IMPORTANCE_EDIT

    def post(self, request, *args, **kwargs):
        body = self.request.body.decode('utf-8')
        posted_info = json.loads(body)
        debate = Debate.objects.get(pk=posted_info['debate_id'])
        debate.importance = posted_info['importance']
        debate.save()
        self.log_action()
        return JsonResponse(json.dumps(posted_info), safe=False)


class SaveDebatePanel(SaveDragAndDropDebateMixin):
    action_log_type = ActionLogEntry.ACTION_TYPE_ADJUDICATORS_SAVE

    def get_moved_item(self, id):
        return Adjudicator.objects.get(pk=id)

    def modify_debate(self, debate, posted_debate):
        panellists = posted_debate['panel']
        message = "Processing change for %s" % debate.id

        # below are DEBUG
        for da in DebateAdjudicator.objects.filter(debate=debate).order_by('type'):
            message += "\nExisting: %s" % da
        for panellist in panellists:
            message += "\nNew: %s %s" % (panellist['adjudicator']['name'], panellist['position'])

        for da in DebateAdjudicator.objects.filter(debate=debate):
            message += "\n\tChecking %s" % da
            match = next((p for p in panellists if p["adjudicator"]["id"] == da.adjudicator.id), None)
            if match:
                message += "\n\t\tExists in panel already %s" % da
                if match['position'] == da.type:
                    message += "\n\t\t\tPASS — Is in same position %s" % da
                else:
                    da.type = match['position']
                    da.save()
                    message += "\n\t\t\tUPDATE — Changed position to %s" % da
                # Updated or not needed to be touched; remove from consideration for adding
                panellists.remove(match)
            else:
                message += "\n\tDELETE — No longer needed; deleting %s" % da
                da.delete()

        for p in panellists:
            adjudicator = Adjudicator.objects.get(pk=p["adjudicator"]["id"])
            new_allocation = DebateAdjudicator.objects.create(debate=debate,
                adjudicator=adjudicator, type=p["position"])
            new_allocation.save() # Move to new location
            message += "\n\tNEW — Creating new allocation %s" % new_allocation

        message += "\n---"
        # print(message)
        return debate
