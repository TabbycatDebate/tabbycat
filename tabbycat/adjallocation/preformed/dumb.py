from .base import BasePreformedPanelAllocator


class DumbPreformedPanelAllocator(BasePreformedPanelAllocator):
    """Allocates panels to debates in the same order as their room ranks."""

    def get_allocations(self):
        debates = sorted(self.debates, key=lambda d: d.room_rank)
        panels = sorted(self.panels, key=lambda p: p.room_rank)
        return zip(debates, panels)
