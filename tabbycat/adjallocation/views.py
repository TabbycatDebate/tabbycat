import json
import logging

from django.views.generic.base import TemplateView, View
from django.http import HttpResponse, HttpResponseBadRequest

from actionlog.mixins import LogActionMixin
from actionlog.models import ActionLogEntry
from breakqual.utils import categories_ordered
from draw.models import Debate
from participants.models import Team
from participants.utils import regions_ordered
from tournaments.models import Round
from tournaments.mixins import RoundMixin
from utils.mixins import JsonDataResponsePostView, SuperuserRequiredMixin

from .allocator import allocate_adjudicators
from .hungarian import HungarianAllocator
from .models import DebateAdjudicator
from .utils import adjs_to_json, debates_to_json, get_adjs, populate_conflicts, populate_histories, teams_to_json


logger = logging.getLogger(__name__)


class EditAdjudicatorAllocationView(RoundMixin, SuperuserRequiredMixin, TemplateView):

    template_name = 'edit_adj_allocation.html'

    def get_context_data(self, **kwargs):
        t = self.get_tournament()
        r = self.get_round()

        draw = r.debate_set_with_prefetches(ordering=('room_rank',), speakers=False, divisions=False)

        teams = Team.objects.filter(debateteam__debate__round=r).prefetch_related('speaker_set')
        adjs = get_adjs(self.get_round())

        regions = regions_ordered(t)
        categories = categories_ordered(t)
        adjs, teams = populate_conflicts(adjs, teams)
        adjs, teams = populate_histories(adjs, teams, t, r)

        kwargs['allRegions'] = json.dumps(regions)
        kwargs['allCategories'] = json.dumps(categories)
        kwargs['allDebates'] = debates_to_json(draw, t, r)
        kwargs['allTeams'] = teams_to_json(teams, regions, categories, t, r)
        kwargs['allAdjudicators'] = adjs_to_json(adjs, regions, t)

        return super().get_context_data(**kwargs)


class CreateAutoAllocation(LogActionMixin, RoundMixin, SuperuserRequiredMixin, JsonDataResponsePostView):

    action_log_type = ActionLogEntry.ACTION_TYPE_ADJUDICATORS_AUTO

    def post_data(self):
        round = self.get_round()
        allocate_adjudicators(round, HungarianAllocator)
        return debates_to_json(round.debate_set_with_prefetches(), self.get_tournament(), round)

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
