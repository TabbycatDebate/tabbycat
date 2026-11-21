from itertools import zip_longest

from .anticipated import calculate_anticipated_draw
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


def update_or_create_preformed_panels(round):
    """Annotates the preformed panels of `round` with the brackets and liveness
    of its anticipated draw, creating panels for any rooms that don't have one.

    Panels are matched to rooms in the anticipated draw by room rank. Existing
    panels keep their adjudicators and importance, so this can be run again to
    refresh the brackets and liveness, for example after results come in.
    Returns the number of panels created.
    """
    ncreated = 0
    for i, (bracket_min, bracket_max, liveness) in enumerate(calculate_anticipated_draw(round), start=1):
        _, created = round.preformedpanel_set.update_or_create(room_rank=i, defaults={
            'bracket_max': bracket_max,
            'bracket_min': bracket_min,
            'liveness': liveness,
        })
        ncreated += created
    return ncreated
