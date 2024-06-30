from django.utils.translation import gettext_lazy as _

from .common import BasePairDrawGenerator, DrawFatalError, DrawUserError, ManualDrawGenerator
from .pairing import ResultPairing, BPEliminationResultPairing
from .elimination import FirstEliminationDrawGenerator, SubsequentEliminationDrawGenerator
from .powerpair import AustralsPowerPairedDrawGenerator, GraphPowerPairedDrawGenerator, AustralsPowerPairedWithAllocatedSidesDrawGenerator, GraphPowerPairedWithAllocatedSidesDrawGenerator
from .random import (RandomBPDrawGenerator, RandomPolyDrawGenerator, GraphRandomDrawGenerator,
    GraphRandomWithAllocatedSidesDrawGenerator, SwapRandomDrawGenerator, SwapRandomWithAllocatedSidesDrawGenerator)
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

def get_two_team_generator(draw_type, avoid_conflicts='australs', side_allocations=None, **kwargs):

    if draw_type == "first_elimination":
        return FirstEliminationDrawGenerator
    elif draw_type == "elimination":
        return SubsequentEliminationDrawGenerator
    elif avoid_conflicts == 'graph':
        if draw_type == "random":
            if side_allocations == "preallocated":
                return GraphRandomWithAllocatedSidesDrawGenerator
            else:
                return GraphRandomDrawGenerator
        elif draw_type == "power_paired":
            if side_allocations == "preallocated":
                return GraphPowerPairedWithAllocatedSidesDrawGenerator
            else:
                return GraphPowerPairedDrawGenerator
    else:
        if draw_type == "random":
            if side_allocations == "preallocated":
                return SwapRandomWithAllocatedSidesDrawGenerator
            else:
                return SwapRandomDrawGenerator
        elif draw_type == "power_paired":
            if side_allocations == "preallocated":
                return AustralsPowerPairedWithAllocatedSidesDrawGenerator
            else:
                return AustralsPowerPairedDrawGenerator
        else:
            raise ValueError("Unrecognised draw type for two-team draw: {}".format(draw_type))


def get_bp_generator(draw_type):
    try:
        return {
            "random": RandomBPDrawGenerator,
            "power_paired": BPHungarianDrawGenerator,
            "partial_elimination": PartialBPEliminationDrawGenerator,
            "after_partial_elimination": AfterPartialBPEliminationDrawGenerator,
            "first_elimination": FirstBPEliminationDrawGenerator,
            "elimination": SubsequentBPEliminationDrawGenerator
        }[draw_type]
    except KeyError:
        raise ValueError("Unrecognised draw type for BP draw: {}".format(draw_type))


def get_poly_generator(draw_type):
    try:
        return {
            "random": RandomPolyDrawGenerator,
        }[draw_type]
    except KeyError:
        raise ValueError("Unrecognised draw type for poly draw: {}".format(draw_type))


def DrawGenerator(teams_in_debate, draw_type, teams, results=None, rrseq=None, **kwargs):  # noqa: N802 (factory function)
    """Factory for draw objects.
    Takes a list of options and returns an appropriate subclass of BaseDrawGenerator.
    'draw_type' is mandatory and can be any of 'random', 'power_paired',
        'first_elimination' and 'elimination'.
    """

    if draw_type == "manual":
        klass = ManualDrawGenerator

    elif teams_in_debate == 2:
        klass = get_two_team_generator(draw_type, **kwargs)

    elif teams_in_debate == 4:
        klass = get_bp_generator(draw_type)

    else:
        klass = get_poly_generator(draw_type)

    kwargs['teams_in_debate'] = teams_in_debate
    return klass(teams, results, rrseq, **kwargs)
