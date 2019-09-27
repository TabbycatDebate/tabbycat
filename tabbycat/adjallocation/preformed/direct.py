from .base import BasePreformedPanelAllocator, register


@register
class DirectPreformedPanelAllocator(BasePreformedPanelAllocator):
    """Allocates panels to debates in the same order as their room ranks."""

    key = "direct"

    def allocate(self):
        return self.debates.order_by('room_rank'), self.panels.order_by('room_rank')
