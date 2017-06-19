from django.utils.translation import ugettext_lazy as _

from .common import BasePairDrawGenerator, DrawError, ManualDrawGenerator, Pairing
from .elimination import FirstEliminationDrawGenerator, EliminationDrawGenerator
from .powerpair import PowerPairedDrawGenerator, PowerPairedWithAllocatedSidesDrawGenerator
from .random import RandomDrawGenerator, RandomWithAllocatedSidesDrawGenerator
from .roundrobin import RoundRobinDrawGenerator


# Flag codes must NOT have commas in them, because they go into a comma-delimited list.
DRAW_FLAG_DESCRIPTIONS = {
    "max_swapped":  _("Too many swaps"),
    "1u1d_hist":    _("One-up-one-down (history)"),
    "1u1d_inst":    _("One-up-one-down (institution)"),
    "1u1d_other":   _("One-up-one-down (to accommodate)"),
    "bub_up_hist":  _("Bubble up (history)"),
    "bub_dn_hist":  _("Bubble down (history)"),
    "bub_up_inst":  _("Bubble up (institution)"),
    "bub_dn_inst":  _("Bubble down (institution)"),
    "bub_up_accom": _("Bubble up (to accommodate)"),
    "bub_dn_accom": _("Bubble down (to accommodate)"),
    "no_bub_updn":  _("Can't bubble up/down"),
    "pullup":       _("Pull-up team"),
}


def DrawGenerator(draw_type, teams, results=None, rrseq=None, **kwargs):  # noqa: N802 (factory function)
    """Factory for draw objects.
    Takes a list of options and returns an appropriate subclass of BaseDrawGenerator.
    'draw_type' is mandatory and can be any of 'random', 'power_paired',
        'first_elimination' and 'elimination'.
    """

    default_side_allocations = BasePairDrawGenerator.BASE_DEFAULT_OPTIONS['side_allocations']

    if draw_type == "random":
        if kwargs.get('side_allocations', default_side_allocations) == "preallocated":
            klass = RandomWithAllocatedSidesDrawGenerator
        else:
            klass = RandomDrawGenerator
    elif draw_type == "manual":
        klass = ManualDrawGenerator
    elif draw_type == "round_robin":
        klass = RoundRobinDrawGenerator
    elif draw_type == "power_paired":
        if kwargs.get('side_allocations', default_side_allocations) == "preallocated":
            klass = PowerPairedWithAllocatedSidesDrawGenerator
        else:
            klass = PowerPairedDrawGenerator
    elif draw_type == "first_elimination":
        klass = FirstEliminationDrawGenerator
    elif draw_type == "elimination":
        klass = EliminationDrawGenerator
    else:
        raise ValueError("Unrecognised draw type: {}".format(draw_type))

    return klass(teams, results, rrseq, **kwargs)
