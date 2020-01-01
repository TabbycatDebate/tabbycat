from .base import BaseAdjudicatorAllocator, register
from ..allocation import AdjudicatorAllocation


@register
class DumbAllocator(BaseAdjudicatorAllocator):

    key = "dumb"

    def allocate(self):

        debates = self.debates
        adjs = list(self.adjudicators)

        result = []
        for debate in debates:
            alloc = AdjudicatorAllocation(debate)
            alloc.chair = adjs.pop(0)
            result.append(alloc)

        while len(adjs) >= 2:
            for alloc in reversed(result):
                if len(adjs) >= 2:
                    alloc.panellists.append(adjs.pop(0))
                    alloc.panellists.append(adjs.pop(0))

        return result, []
