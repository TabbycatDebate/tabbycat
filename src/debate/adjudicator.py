class DumbAdjAllocator(object):
    def __init__(self, round):
        self.round = round

    def get_allocation(self):
        from debate.models import AdjudicatorAllocation

        debates = self.round.debates()
        adjs = list(self.round.active_adjudicators.order_by('-test_score'))

        result = []
        for debate in debates:
            alloc = AdjudicatorAllocation(debate)
            alloc.chair = adjs.pop(0)
            result.append(alloc)

        while len(adjs) >= 2:
            for alloc in result:
                if len(adjs) >= 2:
                    alloc.panel.append(adjs.pop(0))
                    alloc.panel.append(adjs.pop(0))

        return result
