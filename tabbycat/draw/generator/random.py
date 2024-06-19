"""Draw generators for randomly drawn rounds, both two-team and BP."""

import random
from itertools import islice

from django.utils.translation import gettext as _

from .common import BaseBPDrawGenerator, BaseDrawGenerator, BasePairDrawGenerator, DrawUserError
from .graph import GraphAllocatedSidesMixin, GraphGeneratorMixin
from .pairing import Pairing, PolyPairing
from ..types import DebateSide


def batched(iterable, n):
    # Polyfill for Python 3.12
    if n < 1:
        raise ValueError('n must be at least one')
    iterator = iter(iterable)
    while batch := tuple(islice(iterator, n)):
        yield batch


class RandomPairingsMixin:
    """Provides actual random part of it, generic to pair, BP, and PS draws.
    Classes using this mixin must define teams_in_debate.
    """

    def make_random_pairings(self, teams_in_debate):
        teams = list(self.teams)  # Make a copy
        random.shuffle(teams)
        pairings = [self.pairing_class(teams=t, bracket=0, room_rank=0, num_sides=len(t)) for t in batched(teams, teams_in_debate)]
        return pairings


class BaseRandomDrawGenerator(RandomPairingsMixin, BasePairDrawGenerator):
    """Random draw.
    If there are allocated sides, use RandomDrawWithSideConstraints instead.
    Options:
        "max_swap_attempts": Maximum number of times to attempt to swap to
            avoid conflict before giving up.
        "avoid_conflicts": Whether to avoid conflicts, should be a string (for
            compatibility with other types of DrawGenerator).  Turned off if
            this values is "off", turned on if anything else.
    """

    requires_even_teams = True
    requires_prev_results = False
    pairing_class = Pairing

    DEFAULT_OPTIONS = {"max_swap_attempts": 20, "avoid_conflicts": "off"}

    def generate(self):
        self._draw = self.make_random_pairings(self.TEAMS_IN_DEBATE)
        self.avoid_conflicts(self._draw)  # Operates in-place
        self.allocate_sides(self._draw)  # Operates in-place
        return self._draw

    def _get_pools(self):
        return list(self.teams)


class GraphRandomDrawMixin:
    def make_random_pairings(self, teams_in_debate):
        return self.generate_pairings({0: self._get_pools()})[0]


class SwapRandomDrawMixin:

    def avoid_conflicts(self, pairings):
        # Don't swap sides! The child class RandomDrawWithSideConstraints assumes
        # that in this algorithm, affs will stay affs and negs will stay negs.
        if not (self.options["avoid_history"] or self.options["avoid_institution"]):
            return
        if self.options["avoid_conflicts"] == "off":
            return
        for pairing in pairings:
            if self._badness(pairing) > 0:
                for j in range(self.options["max_swap_attempts"]):
                    swap_pairing = random.choice(pairings)
                    if swap_pairing == pairing:
                        continue
                    badness_orig = self._badness(pairing, swap_pairing)
                    pairing.teams[1], swap_pairing.teams[1] = swap_pairing.teams[1], pairing.teams[1]
                    badness_new = self._badness(pairing, swap_pairing)
                    if badness_new == 0:
                        break  # yay!
                    elif badness_new >= badness_orig or self._badness(swap_pairing) > 0:
                        # swap back and try again
                        pairing.teams[1], swap_pairing.teams[1] = swap_pairing.teams[1], pairing.teams[1]
                    # else, if improvement but not perfect, keep swap and try again
                else:
                    pairing.flags.append("max_swapped")

    def _badness(self, *pairings):
        """Returns a weighted conflict intensity for all the pairings given."""
        score = 0
        if self.options["avoid_history"]:
            score += sum([x.conflict_hist for x in pairings]) * self.options["history_penalty"]
        if self.options["avoid_institution"]:
            score += sum([x.conflict_inst for x in pairings]) * self.options["institution_penalty"]
        return score


class GraphRandomDrawGenerator(GraphGeneratorMixin, GraphRandomDrawMixin, BaseRandomDrawGenerator):
    pass


class SwapRandomDrawGenerator(SwapRandomDrawMixin, BaseRandomDrawGenerator):
    pass


class BaseRandomWithAllocatedSidesDrawGenerator(BaseRandomDrawGenerator):
    """Random draw with allocated sides.
    Override functions of RandomDrawGenerator where sides need to be constrained.
    All teams must have an 'allocated_side' attribute which must be either
    'aff' or 'neg' (case-sensitive)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.check_teams_for_attribute("allocated_side", choices=[DebateSide.AFF, DebateSide.NEG])

    def _get_pools(self):
        return [[t for t in self.teams if t.allocated_side == side] for side in [DebateSide.AFF, DebateSide.NEG]]


class GraphRandomWithAllocatedSidesDrawGenerator(GraphAllocatedSidesMixin, GraphRandomDrawMixin, BaseRandomWithAllocatedSidesDrawGenerator):
    pass


class SwapRandomWithAllocatedSidesDrawGenerator(SwapRandomDrawMixin, BaseRandomWithAllocatedSidesDrawGenerator):

    def make_random_pairings(self, teams_in_debate):
        aff_teams = [t for t in self.teams if t.allocated_side == DebateSide.AFF]
        neg_teams = [t for t in self.teams if t.allocated_side == DebateSide.NEG]

        if len(aff_teams) != len(neg_teams):
            raise DrawUserError(_("There were %(aff_count)d affirmative teams but %(neg_count)d negative "
                    "teams.") % {'aff_count': len(aff_teams), 'neg_count': len(neg_teams)})
        if len(aff_teams) + len(neg_teams) != len(self.teams):
            raise DrawUserError(_("One or more teams had an allocated side that wasn't affirmative or negative."))

        random.shuffle(aff_teams)
        random.shuffle(neg_teams)
        pairings = [Pairing(teams=t, bracket=0, room_rank=0) for t in zip(aff_teams, neg_teams)]
        return pairings


class RandomBPDrawGenerator(RandomPairingsMixin, BaseBPDrawGenerator):

    requires_even_teams = True
    requires_prev_result = False
    pairing_class = PolyPairing

    DEFAULT_OPTIONS = {}

    def generate(self):
        self._draw = self.make_random_pairings(self.TEAMS_IN_DEBATE)
        return self._draw


class RandomPolyDrawGenerator(RandomPairingsMixin, BaseDrawGenerator):

    requires_even_teams = False
    requires_prev_result = False
    pairing_class = PolyPairing

    BASE_DEFAULT_OPTIONS = {}
    DEFAULT_OPTIONS = {}

    def __init__(self, *args, teams_in_debate: int, **kwargs):
        self.teams_in_debate = teams_in_debate
        super().__init__(*args, **kwargs)

    def generate(self):
        self._draw = self.make_random_pairings(self.teams_in_debate)
        return self._draw
