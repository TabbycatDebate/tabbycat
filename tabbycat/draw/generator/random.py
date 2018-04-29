"""Draw generators for randomly drawn rounds, both two-team and BP."""

import random

from django.utils.translation import gettext as _

from .common import BaseBPDrawGenerator, BasePairDrawGenerator, DrawUserError
from .pairing import BPPairing, Pairing


class RandomPairingsMixin:
    """Provides actual random part of it, generic to pair and BP draws.
    Classes using this mixin must define self.TEAMS_PER_DEBATE.
    """

    def make_random_pairings(self):
        teams = list(self.teams)  # Make a copy
        random.shuffle(teams)
        args = [iter(teams)] * self.TEAMS_PER_DEBATE  # recipe from Python itertools docs
        pairings = [self.pairing_class(teams=t, bracket=0, room_rank=0) for t in zip(*args)]
        return pairings


class RandomDrawGenerator(RandomPairingsMixin, BasePairDrawGenerator):
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
        self._draw = self.make_random_pairings()
        self.avoid_conflicts(self._draw)  # Operates in-place
        self.allocate_sides(self._draw)  # Operates in-place
        return self._draw

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
        """Returns a weighted conflict intensity for all of the pairings given."""
        score = 0
        if self.options["avoid_history"]:
            score += sum([x.conflict_hist for x in pairings]) * self.options["history_penalty"]
        if self.options["avoid_institution"]:
            score += sum([x.conflict_inst for x in pairings]) * self.options["institution_penalty"]
        return score


class RandomWithAllocatedSidesDrawGenerator(RandomDrawGenerator):
    """Random draw with allocated sides.
    Overrides functions of RandomDrawGenerator where sides need to be constrained.
    All teams must have an 'allocated_side' attribute which must be either
    'aff' or 'neg' (case-sensitive)."""

    def __init__(self, *args, **kwargs):
        super(RandomWithAllocatedSidesDrawGenerator, self).__init__(*args, **kwargs)
        self.check_teams_for_attribute("allocated_side", choices=["aff", "neg"])

    def make_random_pairings(self):
        aff_teams = [t for t in self.teams if t.allocated_side == "aff"]
        neg_teams = [t for t in self.teams if t.allocated_side == "neg"]

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
    pairing_class = BPPairing

    DEFAULT_OPTIONS = {}

    def generate(self):
        self._draw = self.make_random_pairings()
        return self._draw
