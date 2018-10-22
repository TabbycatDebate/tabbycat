from .base import BasePreformedPanelAllocator, register


@register
class HungarianPreformedPanelAllocator(BasePreformedPanelAllocator):

    key = "hungarian"

    def allocate(self):
        return [], []
