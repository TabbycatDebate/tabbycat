import logging
from math import exp
from random import shuffle

from .allocator import Allocator
from .munkres import Munkres

logger = logging.getLogger(__name__)


class HungarianAllocator(Allocator):

    MAX_SCORE = 5.0
    MIN_SCORE = 0.0
    MIN_VOTING_SCORE = 1.5

    DEFAULT_IMPORTANCE = 2

    def __init__(self, *args, **kwargs):
        super(HungarianAllocator, self).__init__(*args, **kwargs)
        t = self.debates[0].round.tournament
        self.MIN_SCORE = t.pref('adj_min_score')
        self.MAX_SCORE = t.pref('adj_max_score')
        self.MIN_VOTING_SCORE = t.pref('adj_min_voting_score')

        self.CONFLICT_PENALTY = t.pref('adj_conflict_penalty')
        self.HISTORY_PENALTY = t.pref('adj_history_penalty')

        self.NO_PANELLISTS = t.pref('no_panellist_position')

        self.DUPLICATE_ALLOCATIONS = t.pref('duplicate_adjs')

    def calc_cost(self, debate, adj, adjustment=0):
        cost = 0

        # Normalise debate importances back to the 0-5 (not +/-2) range expected
        normalised_importance = debate.importance + 2

        # Similarly normalise adj scores to the 0-5 range expected
        score_min = self.MIN_SCORE
        score_range = self.MAX_SCORE - score_min
        normalised_adj_score = (adj.score - score_min) / score_range * 5 + 0

        if normalised_adj_score > 5.0:
            logger.warning("%s's score %s is larger than the range" % (adj.name, adj.score))
        elif normalised_adj_score < 0.0:
            logger.warning("%s's score %s is smaller than the range" % (adj.name, adj.score))

        cost += self.CONFLICT_PENALTY * adj.conflict_with(debate.aff_team)
        cost += self.CONFLICT_PENALTY * adj.conflict_with(debate.neg_team)
        cost += self.HISTORY_PENALTY * adj.seen_team(debate.aff_team, debate.round)
        cost += self.HISTORY_PENALTY * adj.seen_team(debate.neg_team, debate.round)

        impt = (normalised_importance or self.DEFAULT_IMPORTANCE) + adjustment
        diff = 5 + impt - adj.score
        if diff > 0.25:
            cost += 100000 * exp(diff - 0.25)

        cost += (self.MAX_SCORE - adj.score) * 100

        return cost

    def allocate(self):
        from adjallocation.allocation import AdjudicatorAllocation

        # Remove trainees
        self.adjudicators = [a for a in self.adjudicators if a.score >= self.MIN_VOTING_SCORE]
        logger.info("There are %s non-trainee adjudidcators", len(self.adjudicators))

        # Sort adjudicators and debates in descending score/importance
        self.adjudicators_sorted = list(self.adjudicators)
        shuffle(self.adjudicators_sorted)  # Randomize equally-ranked judges
        self.adjudicators_sorted.sort(key=lambda a: a.score, reverse=True)
        self.debates_sorted = list(self.debates)
        self.debates_sorted.sort(key=lambda a: a.importance, reverse=True)

        n_adjudicators = len(self.adjudicators)
        n_debates = len(self.debates)
        logger.info("There are %s debates", n_debates)
        if n_adjudicators < n_debates:
            logger.error("There are %d debates but only %d adjudicators", n_debates, n_adjudicators)

        # If not setting panellists allocate all debates a solo chair
        if self.NO_PANELLISTS is True:
            n_solos = n_debates
        else:
            n_solos = n_debates - (n_adjudicators - n_debates)//2

        # get adjudicators that can adjudicate solo
        chairs = self.adjudicators_sorted[:n_solos]
        logger.info("There are %s chairs", len(chairs))

        # get debates that will be judged by solo adjudicators
        chair_debates = self.debates_sorted[:len(chairs)]

        panel_debates = self.debates_sorted[len(chairs):]
        panellists = [a for a in self.adjudicators_sorted if a not in chairs]
        logger.info("There are %s panellists", len(panellists))

        # For tournaments with duplicate allocations there are typically not
        # enough adjudicators to form full panels, so don't crash in that case
        if not self.DUPLICATE_ALLOCATIONS and len(panellists) < len(panel_debates) * 3:
            logger.error("There are %d panel debates but only %d available panellists (less than %d)",
                    len(panel_debates), len(panellists), len(panel_debates) * 3)

        m = Munkres()
        # TODO I think "chairs" actually means "solos", rename variables if correct
        if len(chairs) > 0:

            logger.info("costing chairs")

            n = len(chairs)

            cost_matrix = [[0] * n for i in range(n)]

            for i, debate in enumerate(chair_debates):
                for j, adj in enumerate(chairs):
                    cost_matrix[i][j] = self.calc_cost(debate, adj)

            logger.info("optimizing")

            indexes = m.compute(cost_matrix)

            total_cost = 0
            for r, c in indexes:
                total_cost += cost_matrix[r][c]

            logger.info('total cost for solos %f', total_cost)
            logger.info('number of solo debates %d', n)

            result = ((chair_debates[i], chairs[j]) for i, j in indexes if i <
                      len(chair_debates))
            alloc = [AdjudicatorAllocation(d, c) for d, c in result]

            for a in alloc:
                logger.info("%s %s", a.debate, a.chair)

        else:
            logger.info("No solo adjudicators.")
            alloc = []

        # Skip the next step if there is the panellist position is disabled
        if self.NO_PANELLISTS is True:
            npan = False
        else:
            n = len(panel_debates)
            npan = len(panellists)

        if npan:
            logger.info("costing panellists")

            # matrix is square, dummy debates have cost 0
            cost_matrix = [[0] * npan for i in range(npan)]
            for i, debate in enumerate(panel_debates):
                for j in range(3):

                    # for the top half of these debates, the final panellist
                    # can be of lower quality than the other 2
                    if i < npan/2 and j == 2:
                        adjustment = -1.0
                    else:
                        adjustment = 0

                    for k, adj in enumerate(panellists):
                        cost_matrix[3*i+j][k] = self.calc_cost(debate, adj,
                                                               adjustment)

            logger.info("optimizing")

            indexes = m.compute(cost_matrix)

            cost = 0
            for r, c in indexes:
                cost += cost_matrix[r][c]

            logger.info('total cost for panellists %f', cost)

            # transfer the indices to the debates
            # the debate corresponding to row r is floor(r/3) (i.e. r // 3)
            p = [[] for i in range(n)]
            for r, c in indexes[:n*3]:
                p[r // 3].append(panellists[c])

            # create the corresponding adjudicator allocations, making sure
            # that the chair is the highest-ranked adjudicator in the panel
            for i, d in enumerate(panel_debates):
                a = AdjudicatorAllocation(d)
                p[i].sort(key=lambda a: a.score, reverse=True)
                a.chair = p[i].pop(0)
                a.panellists = p[i]
                alloc.append(a)

        for a in alloc[len(chairs):]:
            logger.info("%s %s %s", a.debate, a.chair, a.panellists)

        return alloc


def test():
    from tournaments.models import Round
    r = Round.objects.get(pk=4)
    debates = r.debates()
    adjs = list(r.active_adjudicators.all())

    HungarianAllocator(debates, adjs).allocate()

if __name__ == '__main__':
    test()
