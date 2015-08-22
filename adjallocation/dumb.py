from .allocator import Allocator

class DumbAllocator(Allocator):
    def allocate(self):
        from adjallocation.models import AdjudicatorAllocation

        debates = self.debates
        adjs = self.adjudicators

        result = []
        for debate in debates:
            alloc = AdjudicatorAllocation(debate)
            alloc.chair = adjs.pop(0)
            result.append(alloc)

        while len(adjs) >= 2:
            for alloc in reversed(result):
                if len(adjs) >= 2:
                    alloc.panel.append(adjs.pop(0))
                    alloc.panel.append(adjs.pop(0))

        return result
