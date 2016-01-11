from .allocator import Allocator
from .stab import StabAllocator

from .munkres import Munkres

from math import exp
from random import shuffle

class HungarianAllocator(Allocator):

    MAX_SCORE = 5.0
    CHAIR_CUTOFF = 3.5
    MIN_SCORE = 1.5

    DEFAULT_IMPORTANCE = 2

    def __init__(self, *args, **kwargs):
        super(HungarianAllocator, self).__init__(*args, **kwargs)
        preferences = self.debates[0].round.tournament.preferences
        self.MAX_SCORE = preferences.feedback__adj_max_score
        self.MIN_SCORE = preferences.draw_rules__adj_min_voting_score
        self.CHAIR_CUTOFF = preferences.draw_rules__adj_chair_min_score

        self.CONFLICT_PENALTY = preferences.draw_rules__adj_conflict_penalty
        self.HISTORY_PENALTY = preferences.draw_rules__adj_history_penalty

    def calc_cost(self, debate, adj, adjustment=0):
        cost = 0

        cost += self.CONFLICT_PENALTY * adj.conflict_with(debate.aff_team)
        cost += self.CONFLICT_PENALTY * adj.conflict_with(debate.neg_team)
        cost += self.HISTORY_PENALTY * adj.seen_team(debate.aff_team, debate.round)
        cost += self.HISTORY_PENALTY * adj.seen_team(debate.neg_team, debate.round)

        impt = (debate.importance or self.DEFAULT_IMPORTANCE) + adjustment
        diff = 5+ impt - adj.score
        if diff > 0.25:
            cost += 100000 * exp(diff - 0.25)

        cost += (self.MAX_SCORE - adj.score) * 100

        return cost

    def allocate(self):
        from adjallocation.models import AdjudicatorAllocation

        # remove trainees
        self.adjudicators = [a for a in self.adjudicators if a.score >= self.MIN_SCORE]

        # sort adjudicators and debates in descending score/importance
        self.adjudicators_sorted = list(self.adjudicators)
        shuffle(self.adjudicators_sorted) # randomize equally-ranked judges
        self.adjudicators_sorted.sort(key=lambda a: a.score, reverse=True)
        self.debates_sorted = list(self.debates)
        self.debates_sorted.sort(key=lambda a: a.importance, reverse=True)

        n_adjudicators = len(self.adjudicators)
        n_debates = len(self.debates)

        n_solos = n_debates - (n_adjudicators - n_debates)//2

        # get adjudicators that can adjudicate solo
        chairs = self.adjudicators_sorted[:n_solos]
        #chairs = [a for a in self.adjudicators_sorted if a.score >
        #          self.CHAIR_CUTOFF]

        # get debates that will be judged by solo adjudicators
        chair_debates = self.debates_sorted[:len(chairs)]

        panel_debates = self.debates_sorted[len(chairs):]
        panellists = [a for a in self.adjudicators_sorted if a not in chairs]

        assert len(panel_debates) * 3 <= len(panellists)

        print("costing chairs")

        n = len(chairs)
        cost_matrix = [[0] * n for i in range(n)]

        for i, debate in enumerate(chair_debates):
            for j, adj in enumerate(chairs):
                cost_matrix[i][j] = self.calc_cost(debate, adj)

        print("optimizing")

        m = Munkres()
        indexes = m.compute(cost_matrix)

        total_cost = 0
        for r, c in indexes:
            total_cost += cost_matrix[r][c]

        print('total cost for solos', total_cost)
        print('number of solo debates', n)

        result = ((chair_debates[i], chairs[j]) for i, j in indexes if i <
                  len(chair_debates))
        alloc = [AdjudicatorAllocation(d, c) for d, c in result]

        print([(a.debate, a.chair) for a in alloc])

        # do panels
        n = len(panel_debates)

        npan = len(panellists)

        if npan:
            print("costing panellists")

            # matrix is square, dummy debates have cost 0
            cost_matrix = [[0] * npan for i in range(npan)]
            for i, debate in enumerate(panel_debates):
                for j in range(3):

                    # for the top half of these debates, the final panellist
                    # can be of lower quality than the other 2
                    if i < npan/2 and j==2:
                        adjustment = -1.0
                    else:
                        adjustment = 0

                    for k, adj in enumerate(panellists):
                        cost_matrix[3*i+j][k] = self.calc_cost(debate, adj,
                                                               adjustment)

            print("optimizing")

            indexes = m.compute(cost_matrix)

            cost = 0
            for r, c in indexes:
                cost += cost_matrix[r][c]

            print('total cost for panellists', cost)

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
                a.panel = p[i]
                alloc.append(a)

        print([(a.debate, a.chair, a.panel) for a in alloc[len(chairs):]])

        return alloc

def test():
    from tournaments.models import Round
    r = Round.objects.get(pk=4)
    debates = r.debates()
    adjs = list(r.active_adjudicators.all())

    HungarianAllocator(debates, adjs).allocate()

if __name__ == '__main__':
    test()
