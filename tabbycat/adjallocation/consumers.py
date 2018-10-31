import logging

from django.utils.translation import gettext as _

from actionlog.models import ActionLogEntry
from breakqual.utils import calculate_live_thresholds
from draw.consumers import BaseAdjudicatorContainerConsumer, EditDebateOrPanelWorkerMixin
from tournaments.models import Round

from .models import PreformedPanel
from .allocators.hungarian import ConsensusHungarianAllocator, VotingHungarianAllocator
from .preformed import copy_panels_to_debates
from .preformed.anticipated import calculate_anticipated_draw
from .preformed.dumb import DumbPreformedPanelAllocator
from .serializers import (EditPanelAdjsPanelSerializer,
                          SimpleDebateAllocationSerializer, SimpleDebateImportanceSerializer,
                          SimplePanelAllocationSerializer, SimplePanelImportanceSerializer)

logger = logging.getLogger(__name__)


class PanelEditConsumer(BaseAdjudicatorContainerConsumer):
    group_prefix = 'panels'
    model = PreformedPanel
    importance_serializer = SimplePanelImportanceSerializer
    adjudicators_serializer = SimplePanelAllocationSerializer


class AdjudicatorAllocationWorkerConsumer(EditDebateOrPanelWorkerMixin):

    def allocate_debate_adjs(self, event):
        round = Round.objects.get(pk=event['extra']['round_id'])

        if round.preformedpanel_set.exists():

            logger.info("Preformed panels exist, allocating panels to debates")

            round = Round.objects.get(pk=event['extra']['round_id'])
            debates = round.debate_set.all()
            panels = round.preformedpanel_set.all()
            allocator = DumbPreformedPanelAllocator(debates, panels, round)
            debates, panels = allocator.allocate()
            copy_panels_to_debates(debates, panels)

            self.log_action(event['extra'], round, ActionLogEntry.ACTION_TYPE_PREFORMED_PANELS_DEBATES_AUTO)

        else:
            logger.info("Allocating debate adjudicators using traditional allocator")

            # TODO: fix the error handling below
            # if round.draw_status == round.STATUS_RELEASED:
            #     info = _("Draw is already released, unrelease draw to redo auto-allocations.")
            #     logger.warning(info)
            #     # raise BadJsonRequestError(info)
            # if round.draw_status != round.STATUS_CONFIRMED:
            #     info = _("Draw is not confirmed, confirm draw to run auto-allocations.")
            #     logger.warning(info)
            #     # raise BadJsonRequestError(info)

            debates = round.debate_set.all()
            adjs = round.active_adjudicators.all()
            if round.ballots_per_debate == 'per-adj':
                allocator = VotingHungarianAllocator(debates, adjs, round)
            else:
                allocator = ConsensusHungarianAllocator(debates, adjs, round)

            for alloc in allocator.allocate():
                alloc.save()

            self.log_action(event['extra'], round, ActionLogEntry.ACTION_TYPE_ADJUDICATORS_AUTO)

        # TODO: return debates directly from allocator function?
        content = self.reserialize_debates(SimpleDebateAllocationSerializer, round)
        msg = _("Succesfully auto-allocated adjudicators to debates.")
        self.return_response(content, event['extra']['group_name'], msg, 'success')

    def allocate_panel_adjs(self, event):

        round = Round.objects.get(pk=event['extra']['round_id'])
        panels = round.preformedpanel_set.all()
        adjs = round.active_adjudicators.all()
        if round.ballots_per_debate == 'per-adj':
            allocator = VotingHungarianAllocator(panels, adjs, round)
        else:
            allocator = ConsensusHungarianAllocator(panels, adjs, round)

        for alloc in allocator.allocate():
            alloc.save()

        self.log_action(event['extra'], round, ActionLogEntry.ACTION_TYPE_PREFORMED_PANELS_ADJUDICATOR_AUTO)
        content = self.reserialize_panels(SimplePanelAllocationSerializer, round)
        msg = _("Succesfully auto-allocated adjudicators to preformed panels.")
        self.return_response(content, event['extra']['group_name'], msg, 'success')

    def prioritise_debates(self, event):
        # TODO: Debates and panels should really be unified in a single function

        round = Round.objects.get(pk=event['extra']['round_id'])
        debates = round.debate_set.all()

        open_category = round.tournament.breakcategory_set.filter(is_general=True).first()
        if open_category:
            safe, dead = calculate_live_thresholds(open_category, round.tournament, round)
            for debate in debates:
                if debate.bracket >= safe:
                    debate.importance = 0
                elif debate.bracket <= dead:
                    debate.importance = -2
                else:
                    debate.importance = 1
                debate.save()

        self.log_action(event['extra'], round, ActionLogEntry.ACTION_TYPE_DEBATE_IMPORTANCE_AUTO)

        content = self.reserialize_debates(SimpleDebateImportanceSerializer, round, debates)
        msg = _("Succesfully auto-prioritised debates.")
        self.return_response(content, event['extra']['group_name'], msg, 'success')

    def prioritise_panels(self, event):
        round = Round.objects.get(pk=event['extra']['round_id'])
        panels = round.preformedpanel_set.all()

        open_category = round.tournament.breakcategory_set.filter(is_general=True).first()
        if open_category:
            safe, dead = calculate_live_thresholds(open_category, round.tournament, round)
            for panel in panels:
                if panel.bracket_min >= safe:
                    panel.importance = 0
                elif panel.bracket_max <= dead:
                    panel.importance = -2
                else:
                    panel.importance = 1
                panel.save()

        # TODO: If there's no open category, pass back some error message
        # indicating why nothing happened

        self.log_action(event['extra'], round, ActionLogEntry.ACTION_TYPE_PREFORMED_PANELS_IMPORTANCE_AUTO)

        content = self.reserialize_panels(SimplePanelImportanceSerializer, round, panels)
        msg = _("Succesfully auto-prioritised preformed panels.")
        self.return_response(content, event['extra']['group_name'], msg, 'success')

    def create_preformed_panels(self, event):
        round = Round.objects.get(pk=event['extra']['round_id'])
        for i, (bracket_min, bracket_max, liveness) in enumerate(
                calculate_anticipated_draw(round), start=1):
            print('i', i, bracket_min, bracket_max, liveness)
            PreformedPanel.objects.update_or_create(round=round, room_rank=i,
                defaults={
                    'bracket_max': bracket_max,
                    'bracket_min': bracket_min,
                    'liveness': liveness
                })

        self.log_action(event['extra'], round, ActionLogEntry.ACTION_TYPE_PREFORMED_PANELS_CREATE)

        content = self.reserialize_panels(EditPanelAdjsPanelSerializer, round)
        msg = _("Succesfully created new preformed panels for this round.")
        self.return_response(content, event['extra']['group_name'], msg, 'success')
