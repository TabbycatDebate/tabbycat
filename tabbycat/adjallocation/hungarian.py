import logging
import random
from math import exp

from munkres import Munkres

from .allocation import AdjudicatorAllocation
from .allocator import Allocator

logger = logging.getLogger(__name__)


class HungarianAllocator(Allocator):

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
            logger.warning("%s's score %s is larger than the range" % (adj.name, adj._hungarian_score))
        elif normalised_adj_score < 0.0:
            logger.warning("%s's score %s is smaller than the range" % (adj.name, adj._hungarian_score))

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
        voting = [a for a in self.adjudicators if a._hungarian_score >= self.min_voting_score and not a.novice]
        random.shuffle(voting)
        voting.sort(key=lambda a: a._hungarian_score, reverse=True)

        # Divide into solos, panellists and trainees
        n_debates = len(self.debates)
        n_voting = len(voting)

        if self.no_panellists:
            solos = voting[:n_debates]
            panellists = []
        else:
            n_expected_solos = n_debates if self.no_panellists else n_debates - (n_voting - n_debates) // 2
            solos = voting[:n_expected_solos]
            panellists = voting[n_expected_solos:]

        if self.no_trainees:
            trainees = []
        else:
            trainees = [a for a in self.adjudicators if a not in voting]
            trainees.sort(key=lambda a: a._hungarian_score, reverse=True)

        # Divide debates into solo-chaired debates and panel debates
        debates_sorted = sorted(self.debates, key=lambda d: (-d.importance, d.room_rank))
        solo_debates = debates_sorted[:len(solos)]
        panel_debates = debates_sorted[len(solos):]

        logger.info("There are %d debates (%d solo, %d panel), %d solos, %d panellists "
                "(including chairs) and %d trainees", len(debates_sorted), len(solo_debates),
                len(panel_debates), len(solos), len(panellists), len(trainees))
        if n_voting < n_debates:
            logger.warning("There are %d debates but only %d voting adjudicators", n_debates, n_voting)

        # For tournaments with duplicate allocations there are typically not
        # enough adjudicators to form full panels, so don't crash in that case
        if not self.duplicate_allocations and len(panellists) < len(panel_debates) * 3:
            logger.warning("There are %d panel debates but only %d available panellists "
                    "(less than %d)", len(panel_debates), len(panellists), len(panel_debates) * 3)

        # Allocate solos

        m = Munkres()

        if len(solos) > 0:
            logger.info("costing solos")
            cost_matrix = []
            for debate in solo_debates:
                row = [self.calc_cost(debate, adj) for adj in solos]
                cost_matrix.append(row)

            logger.info("optimizing solos (matrix size: %d positions by %d adjudicators)", len(cost_matrix), len(cost_matrix[0]))
            indexes = m.compute(cost_matrix)
            total_cost = sum(cost_matrix[i][j] for i, j in indexes)
            logger.info('total cost for %d solo debates: %f', len(solos), total_cost)

            result = ((solo_debates[i], solos[j]) for i, j in indexes if i < len(solo_debates))
            alloc = [AdjudicatorAllocation(d, c) for d, c in result]
            for aa in alloc:
                logger.info("allocating to %s: %s", aa.debate, aa.chair)

        else:
            logger.info("No solo adjudicators.")
            alloc = []

        # Allocate panellists

        if len(panellists) > 0:
            logger.info("costing panellists")
            cost_matrix = []
            for i, debate in enumerate(panel_debates):
                for j in range(3):
                    # for the top half of these debates, the final panellist
                    # can be of lower quality than the other 2
                    adjustment = -1.0 if i < len(panel_debates)/2 and j == 2 else 0.0
                    row = [self.calc_cost(debate, adj, adjustment) for adj in panellists]
                    cost_matrix.append(row)

            logger.info("optimizing panellists (matrix size: %d positions by %d adjudicators)", len(cost_matrix), len(cost_matrix[0]))
            indexes = m.compute(cost_matrix)
            total_cost = sum(cost_matrix[i][j] for i, j in indexes)
            logger.info('total cost for %d panel debates: %f', len(panel_debates), total_cost)

            # transfer the indices to the debates
            # the debate corresponding to row r is floor(r/3) (i.e. r // 3)
            n = len(panel_debates)
            panels = [[] for i in range(n)]
            for r, c in indexes[:n*3]:
                panels[r // 3].append(panellists[c])

            # create the corresponding adjudicator allocations, making sure that
            # the chair is the highest-ranked adjudicator in the panel
            for i, debate in enumerate(panel_debates):
                aa = AdjudicatorAllocation(debate)
                panels[i].sort(key=lambda a: a._hungarian_score, reverse=True)
                if not panels[i]:
                    continue
                aa.chair = panels[i].pop(0)
                aa.panellists = panels[i]
                alloc.append(aa)

        for aa in alloc[len(solos):]:
            logger.info("allocating to %s: %s (c), %s", aa.debate, aa.chair, ", ".join([str(p) for p in aa.panellists]))

        # Allocate trainees, one per solo debate (leave the rest unallocated)

        if len(trainees) > 0:
            allocation_by_debate = {aa.debate: aa for aa in alloc}

            logger.info("costing trainees")
            cost_matrix = []
            for debate in solo_debates:
                chair = allocation_by_debate[debate].chair
                row = [self.calc_cost(debate, adj, adjustment=-2.0, chair=chair) for adj in trainees]
                cost_matrix.append(row)

            logger.info("optimizing trainees (matrix size: %d positions by %d trainees)", len(cost_matrix), len(cost_matrix[0]))
            indexes = m.compute(cost_matrix)
            total_cost = sum(cost_matrix[i][j] for i, j in indexes)
            logger.info('total cost for %d trainees: %f', len(solos), total_cost)

            result = ((solo_debates[i], trainees[j]) for i, j in indexes if i < len(solo_debates))
            for debate, trainee in result:
                allocation_by_debate[debate].trainees.append(trainee)
                logger.info("allocating to %s: %s (t)", debate, trainee)

        return alloc


def test():
    from tournaments.models import Round
    r = Round.objects.get(pk=4)
    debates = r.debates()
    adjs = list(r.active_adjudicators.all())

    HungarianAllocator(debates, adjs).allocate()

if __name__ == '__main__':
    test()
