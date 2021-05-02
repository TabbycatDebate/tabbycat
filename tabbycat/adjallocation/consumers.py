import logging
from itertools import groupby
from operator import attrgetter

from django.db.models import F
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _, ngettext

from actionlog.models import ActionLogEntry
from breakqual.utils import calculate_live_thresholds
from draw.consumers import BaseAdjudicatorContainerConsumer, EditDebateOrPanelWorkerMixin
from participants.prefetch import populate_win_counts
from tournaments.models import Round

from .allocators.base import AdjudicatorAllocationError
from .allocators.hungarian import ConsensusHungarianAllocator, VotingHungarianAllocator
from .models import PreformedPanel
from .preformed import copy_panels_to_debates
from .preformed.anticipated import calculate_anticipated_draw
from .preformed.hungarian import HungarianPreformedPanelAllocator
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

    def _apply_allocation_settings(self, round, settings):
        t = round.tournament
        for key, value in settings.items():
            if key == "usePreformedPanels":
                # Passing this here is much easier than splitting the function
                continue # (Not actually a preference; just a toggle from Vue)
            # No way to force front-end to only accept floats/integers :(
            if isinstance(t.preferences[key], bool):
                t.preferences[key] = bool(value)
            elif isinstance(t.preferences[key], int):
                t.preferences[key] = int(value)
            elif isinstance(t.preferences[key], float):
                t.preferences[key] = float(value)
            else:
                t.preferences[key] = value

    def allocate_debate_adjs(self, event):
        round = Round.objects.get(pk=event['extra']['round_id'])
        self._apply_allocation_settings(round, event['extra']['settings'])

        if round.draw_status == round.STATUS_RELEASED:
            self.return_error(event['extra']['group_name'],
                _("Draw is already released, unrelease draw to redo auto-allocations."))
            return
        if round.draw_status != round.STATUS_CONFIRMED:
            self.return_error(event['extra']['group_name'],
                _("Draw is not confirmed, confirm draw to run auto-allocations."))
            return

        if event['extra']['settings']['usePreformedPanels']:
            if not round.preformedpanel_set.exists():
                self.return_error(event['extra']['group_name'],
                    _("There are no preformed panels available to allocate."))
                return

            logger.info("Preformed panels exist, allocating panels to debates")

            debates = round.debate_set.all()
            panels = round.preformedpanel_set.all()
            allocator = HungarianPreformedPanelAllocator(debates, panels, round)

            debates, panels = allocator.allocate()
            copy_panels_to_debates(debates, panels)

            self.log_action(event['extra'], round, ActionLogEntry.ACTION_TYPE_PREFORMED_PANELS_DEBATES_AUTO)

            msg = _("Successfully auto-allocated preformed panels to debates.")
            level = 'success'

        else:
            logger.info("Allocating debate adjudicators using traditional allocator")

            debates = round.debate_set.all()
            adjs = round.active_adjudicators.all()

            try:
                if round.ballots_per_debate == 'per-adj':
                    allocator = VotingHungarianAllocator(debates, adjs, round)
                else:
                    allocator = ConsensusHungarianAllocator(debates, adjs, round)
                allocation, user_warnings = allocator.allocate()
            except AdjudicatorAllocationError as e:
                self.return_error(event['extra']['group_name'], str(e))
                return

            for alloc in allocation:
                alloc.save()

            self.log_action(event['extra'], round, ActionLogEntry.ACTION_TYPE_ADJUDICATORS_AUTO)

            if user_warnings:
                msg = ngettext(
                    "Successfully auto-allocated adjudicators to debates. However, there was a warning:",
                    "Successfully auto-allocated adjudicators to debates. However, there were %(count)d warnings:",
                    len(user_warnings)) % {'count': len(user_warnings)}
                msg = "<div>" + msg + "</div><ul class=\"mt-1 mb-0\"><li>" + "</li><li>".join(user_warnings) + "</li></ul>"
                level = 'warning'
            else:
                msg = _("Successfully auto-allocated adjudicators to debates.")
                level = 'success'

        # TODO: return debates directly from allocator function?
        content = self.reserialize_debates(SimpleDebateAllocationSerializer, round)

        self.return_response(content, event['extra']['group_name'], msg, level)

    def allocate_panel_adjs(self, event):
        round = Round.objects.get(pk=event['extra']['round_id'])
        self._apply_allocation_settings(round, event['extra']['settings'])

        panels = round.preformedpanel_set.all()

        if not panels.exists():
            self.return_error(event['extra']['group_name'],
                _("There aren't any panels to fill. Create panels first."))
            return

        adjs = round.active_adjudicators.all()

        try:
            if round.ballots_per_debate == 'per-adj':
                allocator = VotingHungarianAllocator(panels, adjs, round)
            else:
                allocator = ConsensusHungarianAllocator(panels, adjs, round)

            allocation, user_warnings = allocator.allocate()
        except AdjudicatorAllocationError as e:
            self.return_error(event['extra']['group_name'], str(e))
            return

        for alloc in allocation:
            alloc.save()

        self.log_action(event['extra'], round, ActionLogEntry.ACTION_TYPE_PREFORMED_PANELS_ADJUDICATOR_AUTO)
        content = self.reserialize_panels(SimplePanelAllocationSerializer, round)

        if user_warnings:
            msg = ngettext(
                "Successfully auto-allocated adjudicators to preformed panels. However, there was a warning:",
                "Successfully auto-allocated adjudicators to preformed panels. However, there were %(count)d warnings:",
                len(user_warnings)) % {'count': len(user_warnings)}
            msg = "<div>" + msg + "</div><ul class=\"mt-1 mb-0\"><li>" + "</li><li>".join(user_warnings) + "</li></ul>"
            level = 'warning'
        else:
            msg = _("Successfully auto-allocated adjudicators to preformed panels.")
            level = 'success'

        self.return_response(content, event['extra']['group_name'], mark_safe(msg), level)

    def _prioritise_by_bracket(self, instances, bracket_attrname):
        instances = instances.order_by('-' + bracket_attrname)
        nimportancelevels = 4
        importance = 1
        boundary = round(len(instances) / nimportancelevels)
        n = 0
        for k, group in groupby(instances, key=attrgetter(bracket_attrname)):
            group = list(group)
            for panel in group:
                panel.importance = importance
                panel.save()
            n += len(group)
            if n >= boundary:
                importance -= 1
                boundary = round((nimportancelevels - 2 - importance) * len(instances) / nimportancelevels)

    def prioritise_debates(self, event):
        # TODO: Debates and panels should really be unified in a single function
        round = Round.objects.get(pk=event['extra']['round_id'])
        debates = round.debate_set_with_prefetches(teams=True, adjudicators=False,
            speakers=False, venues=False)

        priority_method = event['extra']['settings']['type']
        if priority_method == 'liveness':
            populate_win_counts([team for debate in debates for team in debate.teams], round.prev)
            open_category = round.tournament.breakcategory_set.filter(is_general=True).first()
            if open_category:
                safe, dead = calculate_live_thresholds(open_category, round.tournament, round)
                for debate in debates:
                    points_now = [team.points_count for team in debate.teams]
                    highest = max(points_now)
                    lowest = min(points_now)
                    if lowest >= safe:
                        debate.importance = 0
                    elif highest <= dead:
                        debate.importance = -2
                    else:
                        debate.importance = 1
                    debate.save()
            else:
                self.return_error(event['extra']['group_name'],
                    _("You have no break category set as 'is general' so debate importances can't be calculated."))
                return

        elif priority_method == 'bracket':
            self._prioritise_by_bracket(debates, 'bracket')

        self.log_action(event['extra'], round, ActionLogEntry.ACTION_TYPE_DEBATE_IMPORTANCE_AUTO)
        content = self.reserialize_debates(SimpleDebateImportanceSerializer, round, debates)
        msg = _("Succesfully auto-prioritised debates.")
        self.return_response(content, event['extra']['group_name'], msg, 'success')

    def prioritise_panels(self, event):
        rd = Round.objects.get(pk=event['extra']['round_id'])
        panels = rd.preformedpanel_set.all()
        priority_method = event['extra']['settings']['type']

        if priority_method == 'liveness':
            open_category = rd.tournament.breakcategory_set.filter(is_general=True).first()
            if open_category:
                safe, dead = calculate_live_thresholds(open_category, rd.tournament, rd)
                for panel in panels:
                    if panel.liveness > 0:
                        panel.importance = 1
                    elif panel.bracket_min >= safe:
                        panel.importance = 0
                    else:
                        panel.importance = -2
                    panel.save()
            else:
                self.return_error(event['extra']['group_name'],
                    _("You have no break category set as 'is general' so panel importances can't be calculated."))
                return

        elif priority_method == 'bracket':
            panels = panels.annotate(bracket_mid=(F('bracket_max') + F('bracket_min')) / 2)
            self._prioritise_by_bracket(panels, 'bracket_mid')

        self.log_action(event['extra'], rd, ActionLogEntry.ACTION_TYPE_PREFORMED_PANELS_IMPORTANCE_AUTO)
        content = self.reserialize_panels(SimplePanelImportanceSerializer, rd, panels)
        msg = _("Succesfully auto-prioritised preformed panels.")
        self.return_response(content, event['extra']['group_name'], msg, 'success')

    def create_preformed_panels(self, event):
        round = Round.objects.get(pk=event['extra']['round_id'])
        for i, (bracket_min, bracket_max, liveness) in enumerate(
                calculate_anticipated_draw(round), start=1):
            PreformedPanel.objects.update_or_create(round=round, room_rank=i,
                defaults={
                    'bracket_max': bracket_max,
                    'bracket_min': bracket_min,
                    'liveness': liveness,
                })

        self.log_action(event['extra'], round, ActionLogEntry.ACTION_TYPE_PREFORMED_PANELS_CREATE)
        content = self.reserialize_panels(EditPanelAdjsPanelSerializer, round)

        if round.prev is None:
            msg, level = _("Since this is the first round, the preformed panels aren't annotated "
                    "with brackets and liveness."), 'warning'
        elif not round.prev.debate_set.exists():
            msg, level = _("The previous round's draw doesn't exist, so preformed panels can't be "
                    "annotated with brackets and liveness."), 'warning'
        else:
            msg, level = _("Succesfully created new preformed panels for this round."), 'success'

        self.return_response(content, event['extra']['group_name'], msg, level)
