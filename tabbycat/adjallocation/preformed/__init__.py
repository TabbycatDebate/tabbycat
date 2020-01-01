from itertools import zip_longest

from .base import registry
# These imports add the allocator classes in those files to the registry.
from . import dumb
from . import direct
from . import hungarian


def copy_panels_to_debates(debates, panels):
    """Copies the adjudicators in the given `panels` to the given `debates`.

    If a debate lacks a corresponding panel, either because the iterable of
    panels runs out or because the corresponding panel is `None`, then the
    debate just has its adjudicators cleared. Panels without a corresponding
    debate are ignored. The iterable `debates` must not contain `None`
    (otherwise this function will stop copying there).
    """
    for debate, panel in zip_longest(debates, panels, fillvalue=None):
        if debate is None:
            break
        debate.debateadjudicator_set.all().delete()
        if panel is not None:
            for ppa in panel.preformedpaneladjudicator_set.all():
                debate.debateadjudicator_set.create(adjudicator=ppa.adjudicator, type=ppa.type)
