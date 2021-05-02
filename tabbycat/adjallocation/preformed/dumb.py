from .base import BasePreformedPanelAllocator, register


@register
class DumbPreformedPanelAllocator(BasePreformedPanelAllocator):
    """Allocates panels to debates arbitrarily."""

    key = "dumb"

    def allocate(self):
        return self.debates, self.panels
