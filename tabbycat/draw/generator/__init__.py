from django.utils.translation import ugettext_lazy as _

from .common import BasePairDrawGenerator, DrawFatalError, DrawUserError, ManualDrawGenerator, Pairing
from .elimination import FirstEliminationDrawGenerator, EliminationDrawGenerator
from .powerpair import PowerPairedDrawGenerator, PowerPairedWithAllocatedSidesDrawGenerator
from .random import RandomBPDrawGenerator, RandomDrawGenerator, RandomWithAllocatedSidesDrawGenerator
from .roundrobin import RoundRobinDrawGenerator
from .bphungarian import BPHungarianDrawGenerator


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


def DrawGenerator(teams_per_debate, draw_type, teams, results=None, rrseq=None, **kwargs):  # noqa: N802 (factory function)
    """Factory for draw objects.
    Takes a list of options and returns an appropriate subclass of BaseDrawGenerator.
    'draw_type' is mandatory and can be any of 'random', 'power_paired',
        'first_elimination' and 'elimination'.
    """

    if teams_per_debate == 'two':
        if draw_type == "random":
            if kwargs.get('side_allocations') == "preallocated":
                klass = RandomWithAllocatedSidesDrawGenerator
            else:
                klass = RandomDrawGenerator
        elif draw_type == "manual":
            klass = ManualDrawGenerator
        elif draw_type == "round_robin":
            klass = RoundRobinDrawGenerator
        elif draw_type == "power_paired":
            if kwargs.get('side_allocations') == "preallocated":
                klass = PowerPairedWithAllocatedSidesDrawGenerator
            else:
                klass = PowerPairedDrawGenerator
        elif draw_type == "first_elimination":
            klass = FirstEliminationDrawGenerator
        elif draw_type == "elimination":
            klass = EliminationDrawGenerator
        else:
            raise ValueError("Unrecognised draw type for two-team draw: {}".format(draw_type))

    elif teams_per_debate == 'bp':
        if draw_type == "random":
            klass = RandomBPDrawGenerator
        elif draw_type == "power_paired":
            klass = BPHungarianDrawGenerator
        else:
            raise ValueError("Unrecognised draw type for BP draw: {}".format(draw_type))

    else:
        raise ValueError("Unrecognised teams-per-debate option: {}".format(teams_per_debate))

    return klass(teams, results, rrseq, **kwargs)
