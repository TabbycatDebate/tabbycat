import logging

from munkres import Munkres

from .base import BasePreformedPanelAllocator, register

logger = logging.getLogger(__name__)


@register
class HungarianPreformedPanelAllocator(BasePreformedPanelAllocator):

    key = "hungarian"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        t = self.tournament
        self.conflict_penalty = t.pref('adj_conflict_penalty')
        self.history_penalty = t.pref('adj_history_penalty')
        self.mismatch_penalty = t.pref('preformed_panel_mismatch_penalty')

        self.munkres = Munkres()

    def calc_cost(self, debate, panel):
        cost = 0

        mismatch = (debate.importance - panel.importance) ** 2
        cost += self.mismatch_penalty * mismatch

        for adj in panel.adjudicators.all():
            for team in debate.teams:
                cost += self.conflict_penalty * self.conflicts.conflict_adj_team(adj, team)
                cost += self.history_penalty * self.history.seen_adj_team(adj, team)

        return cost

    def allocate(self):
        cost_matrix = [
            [self.calc_cost(debate, panel) for panel in self.panels]
            for debate in self.debates
        ]

        logger.info("optimizing panels (matrix size: %d debates by %d panels", len(cost_matrix), len(cost_matrix[0]))
        indices = self.munkres.compute(cost_matrix)
        indices.sort()
        total_cost = sum(cost_matrix[i][j] for i, j in indices)
        logger.info("total cost: %f", total_cost)

        # Need to make sure all debates show up in the returned debates list,
        # corresponding to `None` if it didn't get assigned a panel.
        panels = [None] * len(self.debates)
        for r, c in indices:
            logger.info("debate %d, panel %d: cost %f", r, c, cost_matrix[r][c])
            panels[r] = self.panels[c]

        return list(self.debates), panels
