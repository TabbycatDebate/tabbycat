from debate.adjudicator import Allocator
from debate.adjudicator.stab import StabAllocator

from munkres import Munkres

from math import exp

class HungarianAllocator(Allocator):

    MAX_SCORE = 5.0
    CHAIR_CUTOFF = 3.5
    MIN_SCORE = 1.5

    def calc_cost(self, debate, adj):
        cost = 0

        cost += 1000000 * adj.conflict_with(debate.aff_team)
        cost += 1000000 * adj.conflict_with(debate.neg_team)
        cost += 10000 * adj.seen_team(debate.aff_team, debate.round)
        cost += 10000 * adj.seen_team(debate.neg_team, debate.round)

        diff = debate.importance - adj.score
        if diff > 0:
            cost += 10000 * exp(diff - 0.25)

        cost += (self.MAX_SCORE - adj.score) * 1000

        return cost

    def allocate(self):
        from debate.models import AdjudicatorAllocation

        # sort adjudicators and debates in descending score/importance
        self.adjudicators_sorted = list(self.adjudicators)
        self.adjudicators_sorted.sort(key=lambda a: a.score, reverse=True)
        self.debates_sorted = list(self.debates)
        self.debates_sorted.sort(key=lambda a: a.importance, reverse=True)

        # get adjudicators that can adjudicate solo
        chairs = [a for a in self.adjudicators_sorted if a.score >
                  self.CHAIR_CUTOFF]

        # get debates that will be judged by solo adjudicators
        chair_debates = self.debates_sorted[:len(chairs)]

        panel_debates = self.debates_sorted[len(chairs):]
        panellists = [a for a in self.adjudicators_sorted if self.MIN_SCORE <
                      a.score < self.CHAIR_CUTOFF]

        assert len(panel_debates) * 3 <= len(panellists)


        print "calculating costs"

        n = len(chairs)

        cost_matrix = [[0] * n for i in range(n)]

        for i, debate in enumerate(chair_debates):
            for j, adj in enumerate(chairs):
                cost_matrix[i][j] = self.calc_cost(debate, adj)

        print "optimizing"

        m = Munkres()
        indexes = m.compute(cost_matrix)

        total_cost = 0
        for r, c in indexes:
            total_cost += cost_matrix[r][c]

        print 'total cost', total_cost
        print n

        result = ((chair_debates[i], chairs[j]) for i, j in indexes)
        alloc = [AdjudicatorAllocation(d, c) for d, c in result]

        print [(a.debate, a.chair) for a in alloc]

        # do panels
        n = len(panel_debates)

        npan = len(panellists)

        print "costing panellists"

        # matrix is square, dummy debates have cost 0
        cost_matrix = [[0] * npan for i in range(npan)]
        for i, debate in enumerate(panel_debates):
            for j in range(3):
                for k, adj in enumerate(panellists):
                    cost_matrix[3*i+j][k] = self.calc_cost(debate, adj)

        print "optimizing"

        indexes = m.compute(cost_matrix)

        cost = 0
        for r, c in indexes:
            cost += cost_matrix[r][c]

        p = [[] for i in range(n)]
        for r, c in indexes[:n*3]:
            p[r // 3].append(panellists[c])

        for i, d in enumerate(panel_debates):
            a = AdjudicatorAllocation(d)
            p[i].sort(key=lambda a: a.score, reverse=True)
            a.chair = p[i].pop(0)
            a.panel = p[i]
            alloc.append(a)

        return alloc 

def test():
    from debate.models import Round
    r = Round.objects.get(pk=4)
    debates = r.debates()
    adjs = list(r.active_adjudicators.all())

    HungarianAllocator(debates, adjs).allocate()

if __name__ == '__main__':
    test()


