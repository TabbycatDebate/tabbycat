class AdjAllocation(object):
    def __init__(self):
        self.chair = None
        self.panel = []
        self.trainees = []

class DumbAdjAllocator(object):
    def __init__(self, round):
        self.round = round

    def get_allocation(self):
        debates = self.round.debates()
        adjs = list(self.round.active_adjudicators.order_by('-test_score'))

        result = []
        for debate in debates:
            alloc = AdjAllocation()
            alloc.chair = adjs.pop(0)
            result.append((debate, alloc))

        while len(adjs) >= 2:
            for debate, alloc in result:
                if len(adjs) >= 2:
                    alloc.panel.append(adjs.pop(0))
                    alloc.panel.append(adjs.pop(0))

        return result
