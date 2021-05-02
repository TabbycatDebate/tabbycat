from django.utils.translation import gettext_lazy as _

from .common import BasePairDrawGenerator, DrawFatalError, DrawUserError, ManualDrawGenerator
from .pairing import ResultPairing, BPEliminationResultPairing
from .elimination import FirstEliminationDrawGenerator, SubsequentEliminationDrawGenerator
from .powerpair import PowerPairedDrawGenerator, PowerPairedWithAllocatedSidesDrawGenerator
from .random import RandomBPDrawGenerator, RandomDrawGenerator, RandomWithAllocatedSidesDrawGenerator
from .bphungarian import BPHungarianDrawGenerator
from .bpelimination import (PartialBPEliminationDrawGenerator, AfterPartialBPEliminationDrawGenerator,
    FirstBPEliminationDrawGenerator, SubsequentBPEliminationDrawGenerator)


DRAW_FLAG_DESCRIPTIONS = (
    ("max_swapped", _("Too many swaps")),
    ("1u1d_hist", _("One-up-one-down (history)")),
    ("1u1d_inst", _("One-up-one-down (institution)")),
    ("1u1d_other", _("One-up-one-down (to accommodate)")),
    ("bub_up_hist", _("Bubble up (history)")),
    ("bub_dn_hist", _("Bubble down (history)")),
    ("bub_up_inst", _("Bubble up (institution)")),
    ("bub_dn_inst", _("Bubble down (institution)")),
    ("bub_up_accom", _("Bubble up (to accommodate)")),
    ("bub_dn_accom", _("Bubble down (to accommodate)")),
    ("no_bub_updn", _("Can't bubble up/down")),
    ("pullup", _("Pull-up team")),
)


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
        elif draw_type == "power_paired":
            if kwargs.get('side_allocations') == "preallocated":
                klass = PowerPairedWithAllocatedSidesDrawGenerator
            else:
                klass = PowerPairedDrawGenerator
        elif draw_type == "first_elimination":
            klass = FirstEliminationDrawGenerator
        elif draw_type == "elimination":
            klass = SubsequentEliminationDrawGenerator
        else:
            raise ValueError("Unrecognised draw type for two-team draw: {}".format(draw_type))

    elif teams_per_debate == 'bp':
        if draw_type == "random":
            klass = RandomBPDrawGenerator
        elif draw_type == "manual":
            klass = ManualDrawGenerator
        elif draw_type == "power_paired":
            klass = BPHungarianDrawGenerator
        elif draw_type == "partial_elimination":
            klass = PartialBPEliminationDrawGenerator
        elif draw_type == "after_partial_elimination":
            klass = AfterPartialBPEliminationDrawGenerator
        elif draw_type == "first_elimination":
            klass = FirstBPEliminationDrawGenerator
        elif draw_type == "elimination":
            klass = SubsequentBPEliminationDrawGenerator
        else:
            raise ValueError("Unrecognised draw type for BP draw: {}".format(draw_type))

    else:
        raise ValueError("Unrecognised teams-per-debate option: {}".format(teams_per_debate))

    return klass(teams, results, rrseq, **kwargs)
