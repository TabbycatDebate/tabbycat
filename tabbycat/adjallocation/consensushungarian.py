import logging
import random
from math import exp

from munkres import Munkres

from .allocation import AdjudicatorAllocation
from .allocator import Allocator

logger = logging.getLogger(__name__)


class ConsensusHungarianAllocator(Allocator):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        t = self.tournament
        self.min_score = t.pref('adj_min_score')
        self.max_score = t.pref('adj_max_score')
        self.min_voting_score = t.pref('adj_min_voting_score')
        self.conflict_penalty = t.pref('adj_conflict_penalty')
        self.history_penalty = t.pref('adj_history_penalty')
        self.no_panellists = t.pref('no_panellist_position')
        self.no_trainees = t.pref('no_trainee_position')
        self.duplicate_allocations = t.pref('duplicate_adjs')
        self.feedback_weight = t.current_round.feedback_weight

    def populate_adj_scores(self, adjudicators):
        for adj in adjudicators:
            adj._hungarian_score = adj.weighted_score(self.feedback_weight)

    def calc_cost(self, debate, adj, adjustment=0, chair=None):
        cost = 0

        # Normalise debate importances back to the 1-5 (not ±2) range expected
        normalised_importance = debate.importance + 3

        # Similarly normalise adj scores to the 0-5 range expected
        score_min = self.min_score
        score_range = self.max_score - score_min
        normalised_adj_score = (adj._hungarian_score - score_min) / score_range * 5 + 0

        if normalised_adj_score > 5.0:
            logger.warning("Normalised score %s is larger than 5.0 (raw score %s, min %s, max %s)",
                normalised_adj_score, adj._hungarian_score, self.min_score, self.max_score)
        elif normalised_adj_score < 0.0:
            logger.warning("Normalised score %s is smaller than 0.0 (raw score %s, min %s, max %s)",
                normalised_adj_score, adj._hungarian_score, self.min_score, self.max_score)

        for side in self.tournament.sides:
            cost += self.conflict_penalty * adj.conflicts_with_team(debate.get_team(side))
            cost += self.history_penalty * adj.seen_team(debate.get_team(side), debate.round)
        if chair:
            cost += self.conflict_penalty * adj.conflicts_with_adj(chair)
            cost += self.history_penalty * adj.seen_adjudicator(chair, debate.round)

        impt = normalised_importance + adjustment
        diff = 5 + impt - adj._hungarian_score
        if diff > 0.25:
            cost += 1000 * exp(diff - 0.25)

        cost += self.max_score - adj._hungarian_score

        return cost

    def allocate(self):
        self.populate_adj_scores(self.adjudicators)

        # Sort voting adjudicators in descending order by score
        voting = [a for a in self.adjudicators if a._hungarian_score >= self.min_voting_score and not a.trainee]
        random.shuffle(voting)
        voting.sort(key=lambda a: a._hungarian_score, reverse=True)

        n_debates = len(self.debates)
        if self.no_panellists:
            voting = voting[:n_debates]
        n_voting = len(voting)

        if self.no_trainees:
            trainees = []
        else:
            trainees = [a for a in self.adjudicators if a not in voting]
            trainees.sort(key=lambda a: a._hungarian_score, reverse=True)

        # Divide debates into solo-chaired debates and panel debates
        debates_sorted = sorted(self.debates, key=lambda d: (-d.importance, d.room_rank))

        # Figure out how many judges per room, prioritising the most important
        judges_per_room_floor = n_voting // n_debates
        n_bigger_panels = n_voting % n_debates
        judges_per_room = [judges_per_room_floor+1] * n_bigger_panels + [judges_per_room_floor] * (n_debates - n_bigger_panels)

        logger.info("There are %d debates, %d voting adjudicators and %d trainees",
                len(debates_sorted), len(voting), len(trainees))
        if n_voting < n_debates:
            logger.warning("There are %d debates but only %d voting adjudicators", n_debates, n_voting)

        # Allocate voting
        m = Munkres()

        logger.info("costing voting adjudicators")
        cost_matrix = []
        for debate, njudges in zip(debates_sorted, judges_per_room):
            for i in range(njudges):
                row = [self.calc_cost(debate, adj, adjustment=-i) for adj in voting]
                cost_matrix.append(row)

        logger.info("optimizing voting adjudicators (matrix size: %d positions by %d adjudicators)",
                len(cost_matrix), len(cost_matrix[0]))
        indexes = m.compute(cost_matrix)
        indexes.sort()
        total_cost = sum(cost_matrix[i][j] for i, j in indexes)
        logger.info('total cost for %d debates: %f', n_debates, total_cost)

        # transfer the indices to the debates
        alloc = []
        for debate, njudges in zip(debates_sorted, judges_per_room):
            aa = AdjudicatorAllocation(debate)
            panel_indices = indexes[0:njudges]
            panel = [voting[c] for r, c in panel_indices]
            panel.sort(key=lambda a: a._hungarian_score, reverse=True)
            try:
                aa.chair = panel.pop(0)
            except IndexError:
                aa.chair = None
            aa.panellists = panel
            alloc.append(aa)
            del indexes[0:njudges]

            logger.info("allocating to %s: %s (c), %s", aa.debate, aa.chair, ", ".join([str(p) for p in aa.panellists]))

        # Allocate trainees, one per debate
        if len(trainees) > 0 and len(debates_sorted) > 0:
            allocation_by_debate = {aa.debate: aa for aa in alloc}

            logger.info("costing trainees")
            cost_matrix = []
            for debate in debates_sorted:
                chair = allocation_by_debate[debate].chair
                row = [self.calc_cost(debate, adj, adjustment=-2.0, chair=chair) for adj in trainees]
                cost_matrix.append(row)

            logger.info("optimizing trainees (matrix size: %d positions by %d trainees)", len(cost_matrix), len(cost_matrix[0]))
            indexes = m.compute(cost_matrix)
            total_cost = sum(cost_matrix[i][j] for i, j in indexes)
            logger.info('total cost for %d trainees: %f', len(trainees), total_cost)

            result = ((debates_sorted[i], trainees[j]) for i, j in indexes if i < len(debates_sorted))
            for debate, trainee in result:
                allocation_by_debate[debate].trainees.append(trainee)
                logger.info("allocating to %s: %s (t)", debate, trainee)

        return alloc
