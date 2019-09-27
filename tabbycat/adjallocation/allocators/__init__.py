from tournaments.models import Round

from utils.views import BadJsonRequestError

from .base import AdjudicatorAllocationError, registry
# These imports add the allocator classes in those files to the registry.
from . import hungarian
from . import dumb
from . import anneal


def legacy_allocate_adjudicators(round, alloc_class):
    """@deprecate when legacy drag and drop UIs removed"""
    if round.draw_status != Round.STATUS_CONFIRMED:
        raise RuntimeError("Tried to allocate adjudicators on unconfirmed draw")

    debates = round.debate_set.all()
    adjs = list(round.active_adjudicators.all())
    allocator = alloc_class(debates, adjs, round)

    try:
        allocation, _ = allocator.allocate()
    except AdjudicatorAllocationError as e:
        # legacy views expect BadJsonRequestError, not AdjudicatorAllocationError
        raise BadJsonRequestError(e)

    for alloc in allocation:
        alloc.save()
