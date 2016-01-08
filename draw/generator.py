from collections import OrderedDict
import random
import math
import copy
from .one_up_one_down import OneUpOneDownSwapper
from warnings import warn

# Flag codes must NOT have commas in them, because they go into a comma-delimited list.
DRAW_FLAG_DESCRIPTIONS = {
    "max_swapped":  "Too many swaps",
    "1u1d_hist":    "One-up-one-down (history)",
    "1u1d_inst":    "One-up-one-down (institution)",
    "1u1d_other":   "One-up-one-down (to accommodate)",
    "bub_up_hist":  "Bubble up (history)",
    "bub_dn_hist":  "Bubble down (history)",
    "bub_up_inst":  "Bubble up (institution)",
    "bub_dn_inst":  "Bubble down (institution)",
    "bub_up_accom": "Bubble up (to accommodate)",
    "bub_dn_accom": "Bubble down (to accommodate)",
    "no_bub_updn":  "Can't bubble up/down",
    "pullup":       "Pull-up team",
}


class DrawError(Exception):
    pass


class Pairing(object):
    """Simple data structure for communicating information about pairings.
    Draws always return a list of these."""

    def __init__(self, teams, bracket, room_rank, flags=[], winner=None, division=None):
        """'teams' must be a list of two teams.
        'bracket' and 'room_rank' are both integers.
        'flags' is a list of strings."""
        self.teams         = list(teams)
        self.bracket       = bracket
        self.room_rank     = room_rank
        self.flags         = list(flags)
        self.division      = division
        if winner is None:
            self._winner_index = None
        else:
            self._winner_index = self.teams.index(winner)

    def __repr__(self):
        return "<Pairing object: {0} vs {1} ({2}/{3})>".format(
            self.teams[0], self.teams[1], self.bracket, self.room_rank)

    @property
    def aff_team(self):
        return self.teams[0]

    @property
    def neg_team(self):
        return self.teams[1]

    def get_team(self, side):
        try:
            index = {"aff": 0, "neg": 1}[side]
        except KeyError:
            raise ValueError("side must be 'aff' or 'neg'")
        return self.teams[index]

    def balance_sides(self):
        """Puts whoever has affirmed less on the affirmative side,
        or chooses randomly if they've done it equally."""
        if self.teams[0].aff_count < self.teams[1].aff_count:
            pass
        elif self.teams[0].aff_count > self.teams[1].aff_count:
            self.teams.reverse()
        else:
            random.shuffle(self.teams)

    def shuffle_sides(self):
        """Randomly allocate sides."""
        random.shuffle(self.teams)

    @property
    def conflict_inst(self):
        """Returns True if both teams are from the same institution.
        Relies on the institution attribute of teams."""
        try:
            return self.teams[0].institution == self.teams[1].institution
        except AttributeError:
            # In theory redundant, since DrawGenerators should use check_teams_for_attribute
            # to check for this.
            raise DrawError("For conflict avoidance, teams must have an attribute 'institution'.")

    @property
    def conflict_hist(self):
        """Returns True if teams have seen each other before.
        Relies on seen() being implemented by the teams."""
        try:
            return self.teams[0].seen(self.teams[1])
        except AttributeError:
            # In theory redundant, since DrawGenerators should use check_teams_for_attribute
            # to check for this.
            raise DrawError("For conflict avoidance, teams must have an attribute 'seen'.")

    def add_flag(self, flag):
        self.flags.append(flag)

    def add_flags(self, flags):
        self.flags.extend(flags)

    def set_winner(self, team):
        try:
            self._winner_index = self.teams.index(team)
        except ValueError:
            raise ValueError('Team {0!r} not found in teams for this pairing'.format(team))

    @property
    def winner(self):
        if self._winner_index is None:
            return None
        return self.teams[self._winner_index]


def DrawGenerator(draw_type, teams, results=None, **kwargs):
    """Factory for draw objects.
    Takes a list of options and returns an appropriate subclass of BaseDrawGenerator.
    'draw_type' is mandatory and can be any of 'random', 'power_paired',
        'first_elimination' and 'elimination'.
    """

    default_side_allocations = BaseDrawGenerator.BASE_DEFAULT_OPTIONS['side_allocations']

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

    return klass(teams, results, **kwargs)


class BaseDrawGenerator(object):
    """Base class for generators for all draw types.
    Options:
        "side_allocations" - Side allocation method, one of:
            "balance" - the team that has affirmed less in prior rounds affirms,
                or randomly if both teams have affirmed the same number of times.
                If used, team objects must have an 'aff_count' attribute.
            "preallocated" - teams were pre-allocated sides. If used, teams must
                have an 'allocated_side' attribute.
            "none" - leave sides as they were when the pairings were drawn.
                (This is almost never desirable.)
            "random" - allocate randomly.
        "avoid_history" - if True, draw tries to avoid pairing teams that have
            seen each other before, and tries harder if they've seen each other
            multiple times.
        "history_penalty" -
        "avoid_institution" - if True, draw tries to avoid pairing teams that
            are from the same institution.
        """

    BASE_DEFAULT_OPTIONS = {
        "side_allocations"   : "balance",
        "avoid_history"      : True,
        "avoid_institution"  : True,
        "history_penalty"    : 1e3,
        "institution_penalty": 1
    }

    can_be_first_round = NotImplemented
    requires_even_teams = True
    requires_prev_results = False
    draw_type = NotImplemented

    # All subclasses must define this with any options that may exist.
    DEFAULT_OPTIONS = {}

    def __init__(self, teams, results=None, **kwargs):
        self.teams = teams
        self.team_flags = dict()

        if self.requires_even_teams:
            if not len(self.teams) % 2 == 0:
                raise DrawError("There was not an even number of active teams.")
            if not self.teams:
                raise DrawError("There were no teams for the draw.")

        if results is None and self.requires_prev_results:
            raise TypeError("'results' is required for draw of type {0:s}".format(
                    self.__class__.__name__))
        if results is not None and not self.requires_prev_results:
            warn("'results' not required for draw of type {0:s}, will probably be ignored".format(
                    self.__class__.__name__))
        if results is not None:
            self.results = results

        # Compute the full dictionary of default options
        self.options = self.BASE_DEFAULT_OPTIONS.copy()
        self.options.update(self.DEFAULT_OPTIONS)

        # Check that all options actually exist
        for key in kwargs:
            if key not in self.options:
                raise ValueError("Unrecognized option: {0}".format(key))

        # Update
        self.options.update(kwargs)

        # Check for required team attributes.
        # Subclasses might do more.
        if self.options["avoid_history"]:
            self.check_teams_for_attribute("seen", checkfunc=callable)
        if self.options["avoid_institution"]:
            self.check_teams_for_attribute("institution")

    def get_option_function(self, option_name, option_dict):
        option = self.options[option_name]
        if callable(option):
            return option
        try:
            return getattr(self, option_dict[option])
        except KeyError:
            raise ValueError("Invalid option for {1}: {0}".format(option, option_name))

    def add_team_flag(self, team, flag):
        """Attaches a flag to a team.
        Child classes may use this when flags should follow teams, but
        eventually be attached to pairings."""
        flags = self.team_flags.setdefault(team, list())
        flags.append(flag)

    def annotate_team_flags(self, pairings):
        """Applies the team flags to the pairings given.
        Child classes that use team flags should call this method as the last
        thing before the draw is returned."""
        for pairing in pairings:
            for team in pairing.teams:
                if team in self.team_flags:
                    pairing.add_flags(self.team_flags[team])

    def balance_sides(self, pairings):
        if self.options["side_allocations"] == "balance":
            for pairing in pairings:
                pairing.balance_sides()
        elif self.options["side_allocations"] == "random":
            for pairing in pairings:
                pairing.shuffle_sides()
        elif self.options["side_allocations"] not in ["none", "preallocated"]:
            raise ValueError("side_allocations setting not recognized: {0!r}".format(self.options["side_allocations"]))

    def generate(self):
        """Abstract method."""
        raise NotImplementedError

    @classmethod
    def available_options(cls):
        keys = set(cls.BASE_DEFAULT_OPTIONS.keys())
        keys |= list(cls.DEFAULT_OPTIONS.keys())
        return sorted(list(keys))

    def check_teams_for_attribute(self, name, choices=None, checkfunc=None):
        """Checks that all teams have the specified attribute, and raises a
        DrawError if they don't. This should be called during the constructor.
        Note: Whether to run this check will sometimes be conditional on options
        supplied to the DrawGenerator.
        'name' is the name of the attribute.
        'choices', if specified, is a list of allowed values for the attribute.
        """
        has_attribute = [hasattr(x, name) for x in self.teams]
        if not all(has_attribute):
            offending_teams = has_attribute.count(False)
            raise DrawError("{0} out of {1} teams don't have a '{name}' attribute.".format(
                    offending_teams, len(self.teams), name=name))
        if choices:
            attribute_value_valid = [getattr(x, name) in choices for x in self.teams]
        elif checkfunc:
            attribute_value_valid = [checkfunc(getattr(x, name)) for x in self.teams]
        else:
            return
        if not all(attribute_value_valid):
            offending_teams = attribute_value_valid.count(False)
            raise DrawError("{0} out of {1} teams has an invalid '{name}' attribute. Valid choices: ".format(
                    offending_teams, len(self.teams), name=name) + ", ".join(map(repr, choices)))


class RandomDrawGenerator(BaseDrawGenerator):
    """Random draw.
    If there are allocated sides, use RandomDrawWithSideConstraints instead.
    Options:
        "max_swap_attempts": Maximum number of times to attempt to swap to
            avoid conflict before giving up.
        "avoid_conflicts": Whether to avoid conflicts, should be a string (for
            compatibility with other types of DrawGenerator).  Turned off if
            this values is "off", turned on if anything else.
    """

    can_be_first_round = True
    requires_even_teams = True
    requires_prev_results = False
    draw_type = "preliminary"

    DEFAULT_OPTIONS = {"max_swap_attempts": 20, "avoid_conflicts": "off"}

    def generate(self):
        self._draw = self._make_initial_pairings()
        self.avoid_conflicts(self._draw) # operates in-place
        self.balance_sides(self._draw) # operates in-place
        return self._draw

    def _make_initial_pairings(self):
        teams = list(self.teams) # make a copy
        random.shuffle(teams)
        debates = len(teams) // 2
        pairings = [Pairing(teams=t, bracket=0, room_rank=0) for t in zip(teams[:debates], teams[debates:])]
        return pairings

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
                        break # yay!
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

    def _make_initial_pairings(self):
        if not all(hasattr(t, 'allocated_side') for t in self.teams):
            raise DrawError("To use allocated sides, all teams must have an 'allocated_side' attribute, which must be 'aff' or 'neg'.")

        aff_teams = [t for t in self.teams if t.allocated_side == "aff"]
        neg_teams = [t for t in self.teams if t.allocated_side == "neg"]

        if len(aff_teams) != len(neg_teams):
            raise DrawError("There were {0} aff teams but {1} neg teams.".format(len(aff_teams), len(neg_teams)))
        if len(aff_teams) + len(neg_teams) != len(self.teams):
            raise DrawError("One or more teams had an allocated side that wasn't 'aff' or 'neg'.")

        random.shuffle(aff_teams)
        random.shuffle(neg_teams)
        debates = len(aff_teams)
        pairings = [Pairing(teams=t, bracket=0, room_rank=0) \
                for t in zip(aff_teams, neg_teams)]
        return pairings


class PowerPairedDrawGenerator(BaseDrawGenerator):
    """Power-paired draw.
    If there are allocated sides, use PowerPairedWithAllocatedSidesDrawGenerator instead.
    Options:
        "odd_bracket" - Odd bracket resolution method, values can be one of:
            "pullup_top"    - pull up the top team from the next bracket down.
            "pullup_bottom" - pull up the bottom team from the next bracket down.
            "pullup_random" - pull up a random team from the next bracket down.
            "intermediate"  - the bottom team from the odd bracket and the top team
                from the next bracket down face each other in an intermediate bubble.
            "intermediate_bubble_up_down" - like "intermediate", but will swap teams
                that conflict by history or institution.
            or a function taking a dict mapping floats to lists of Team-like objects,
                and operating on the dict in-place.
        "pairing_method" - How to pair teams, values can be one of:
            (best explained by example, these examples have a ten-team bracket)
            "slide"  - 1 vs 6, 2 vs 7, ..., 5 vs 10.
            "fold"   - 1 vs 10, 2 vs 9, ..., 5 vs 6.
            "random" - pairs chosen randomly.
            or a function taking a dict mapping floats to even-length lists of
                Team-like objects, and returning a list of Pairing objects with
                those teams.
        "avoid_conflicts" - How to avoid conflicts.
            "one_up_one_down" - swap conflicted teams with the debate above or below,
                in accordance with Australasian Intervarsity Debating Association rules.
            "off" - which turns off conflict avoidance.
    """

    can_be_first_round = False
    requires_even_teams = True
    requires_prev_results = False
    draw_type = "preliminary"

    DEFAULT_OPTIONS = {
        "odd_bracket"    : "intermediate_bubble_up_down",
        "pairing_method" : "slide",
        "avoid_conflicts": "one_up_one_down"
    }

    def __init__(self, *args, **kwargs):
        super(PowerPairedDrawGenerator, self).__init__(*args, **kwargs)
        self.check_teams_for_attribute("points")

    def generate(self):
        self._brackets = self._make_raw_brackets()
        self.resolve_odd_brackets(self._brackets) # operates in-place
        self._pairings = self.generate_pairings(self._brackets)
        self.avoid_conflicts(self._pairings) # operates in-place
        self._draw = list()
        for bracket in self._pairings.values():
            self._draw.extend(bracket)

        self.balance_sides(self._draw) # operates in-place
        self.annotate_team_flags(self._draw) # operates in-place
        return self._draw

    def _make_raw_brackets(self):
        """Returns an OrderedDict mapping bracket names (normally numbers)
        to lists."""
        brackets = OrderedDict()
        teams = list(self.teams)
        while len(teams) > 0:
            top_team = teams.pop(0)
            points = top_team.points
            pool = [top_team]
            while len(teams) > 0 and teams[0].points == points:
                pool.append(teams.pop(0))
            brackets[points] = pool
        return brackets

    ## Odd bracket resolutions

    ODD_BRACKET_FUNCTIONS = {
        "pullup_top"                  : "_pullup_top",
        "pullup_bottom"               : "_pullup_bottom",
        "pullup_random"               : "_pullup_random",
        "intermediate"                : "_intermediate_bubbles",
        "intermediate_bubble_up_down": "_intermediate_bubbles_with_up_down"
    }

    def resolve_odd_brackets(self, brackets):
        """Returns a function taking an OrderedDict as returned by
        _make_raw_brackets(), and adjusting that OrderedDict in-place to
        guarantee that all brackets have an even number of teams."""
        function = self.get_option_function("odd_bracket", self.ODD_BRACKET_FUNCTIONS)
        return function(brackets)

    def _pullup_top(self, brackets):
        self._pullup(brackets, lambda x: 0)

    def _pullup_bottom(self, brackets):
        self._pullup(brackets, lambda x: -1)

    def _pullup_random(self, brackets):
        self._pullup(brackets, lambda x: random.randrange(x))

    def _pullup(self, brackets, pos):
        """'brackets' is what is returned by _make_raw_brackets().
        'pos' is a function taking the number of teams to choose from,
        and returning an index for which team to take as the pullup.
        Operates in-place. Does not remove empty brackets."""
        pullup_needed_for = None
        for points, teams in brackets.items():
            if pullup_needed_for:
                pullup_team = teams.pop(pos(len(teams)))
                self.add_team_flag(pullup_team, "pullup")
                pullup_needed_for.append(pullup_team)
                pullup_needed_for = None
            if len(teams) % 2 != 0:
                pullup_needed_for = teams
        if pullup_needed_for:
            raise DrawError("Last bracket is still odd!\n" + repr(pullup_needed_for))

    @classmethod
    def _intermediate_bubbles(cls, brackets):
        """Operates in-place."""
        new = OrderedDict()
        odd_team = None
        for points, teams in brackets.items():
            if odd_team:
                new[points+0.5] = [odd_team, teams.pop(0)]
                odd_team = None
            if len(teams) % 2 != 0:
                odd_team = teams.pop()
            if len(teams) > 0:
                new[points] = teams
        if odd_team:
            raise DrawError("Last bracket is still odd!\n" + repr(odd_team))
        brackets.clear()
        brackets.update(new)

    def _intermediate_bubbles_with_up_down(self, brackets):
        """Operates in-place.
        Requires Team.institution and Team.seen() to be defined."""
        self._intermediate_bubbles(brackets) # operates in-place
        # Check each of the intermediate bubbles for conflicts.
        # If there is one, try swapping the top team with the bottom team
        # of the bracket above. Failing that, try the same with the bottom
        # team and the top team of the bracket below. Failing that, give up.
        # Note: Under no circumstances do we swap both teams.
        def _check_conflict(team1, team2):
            try:
                if team1.institution == team2.institution:
                    return 1 # institution
                if team1.seen(team2):
                    return 2 # history
            except AttributeError:
                raise DrawError("For conflict avoidance, teams must have attributes 'institution' and 'seen'.")
            return 0 # no conflict

        for points, teams in brackets.items():
            if int(points) == points:
                continue # skip non-intermediate brackets
            # a couple of checks
            assert points % 0.5 == 0
            assert teams[0].points > teams[1].points
            conflict = _check_conflict(*teams)
            if not conflict:
                continue # leave alone if no conflict

            # bubble up, if there exists such a bubble
            # swap bottom team from higher bracket with top team from
            # intermediate bracket.
            if points+0.5 in brackets:
                swap_team = brackets[points+0.5][-1] # bottom team
                if not _check_conflict(swap_team, teams[1]):
                    self.add_team_flag(teams[0], (conflict == 1) and "bub_up_inst" or "bub_up_hist")
                    self.add_team_flag(swap_team, "bub_up_accom")
                    teams[0], brackets[points+0.5][-1] = swap_team, teams[0]
                    continue

            # bubble down, if bubble up didn't work
            if points-0.5 in brackets:
                swap_team = brackets[points-0.5][0] # bottom team
                if not _check_conflict(swap_team, teams[0]):
                    self.add_team_flag(teams[1], (conflict == 1) and "bub_dn_inst" or "bub_dn_hist")
                    self.add_team_flag(swap_team, "bub_dn_accom")
                    teams[1], brackets[points-0.5][0] = swap_team, teams[1]
                    continue

            # if nothing worked, add a "didn't work" flag
            self.add_team_flag(teams[0], "no_bub_updn")


    ## Pairings generation

    PAIRING_FUNCTIONS = {
        "fold"  : "_pairings_fold",
        "slide" : "_pairings_slide",
        "random": "_pairings_random"
    }

    def generate_pairings(self, brackets):
        """Returns a function taking an OrderedDict as returned by
        resolve_odd_brackets(), and returning a list of Debates."""
        function = self.get_option_function("pairing_method", self.PAIRING_FUNCTIONS)
        return function(brackets)

    @staticmethod
    def _pairings(brackets, subpool_func):
        pairings = OrderedDict()
        i = 1
        for points, teams in brackets.items():
            bracket = list()
            top, bottom = subpool_func(teams)
            for teams in zip(top, bottom):
                pairing = Pairing(teams=teams, bracket=points, room_rank=i)
                bracket.append(pairing)
                i = i + 1
            pairings[points] = bracket
        return pairings

    @classmethod
    def _pairings_slide(cls, brackets):
        def slide(teams):
            num_debates = len(teams) // 2
            top = teams[:num_debates]
            bottom = teams[num_debates:]
            return top, bottom
        return cls._pairings(brackets, slide)

    @classmethod
    def _pairings_fold(cls, brackets):
        def fold(teams):
            num_debates = len(teams) // 2
            top = teams[:num_debates]
            bottom = teams[num_debates:]
            bottom.reverse()
            return top, bottom
        return cls._pairings(brackets, fold)

    @classmethod
    def _pairings_random(cls, brackets):
        def shuffle(teams):
            num_debates = len(teams) // 2
            random.shuffle(teams)
            top = teams[:num_debates]
            bottom = teams[num_debates:]
            return top, bottom
        return cls._pairings(brackets, shuffle)

    ## Conflict avoidance

    AVOID_CONFLICT_FUNCTIONS = {
        "one_up_one_down" : "_one_up_one_down",
    }

    def avoid_conflicts(self, pairings):
        """Returns a function taking a list of Pairings returned by
        generate_pairings(), and adjusting it in-place to avoid conflicts."""
        if self.options["avoid_conflicts"] == "off":
            return
        function = self.get_option_function("avoid_conflicts", self.AVOID_CONFLICT_FUNCTIONS)
        return function(pairings)

    def _one_up_one_down(self, pairings):
        """We pass the pairings to one_up_one_down.py, then infer annotations
        based on the result."""

        for bracket in pairings.values():
            pairs = [tuple(p.teams) for p in bracket]
            pairs_orig = list(pairs) # keep a copy for comparison
            OPTIONS = ["avoid_history", "avoid_institution", "history_penalty",
                    "institution_penalty"]
            options = dict((key, self.options[key]) for key in OPTIONS)
            swapper = OneUpOneDownSwapper(**options)
            pairs_new = swapper.run(pairs)
            swaps = swapper.swaps

            for i, (pairing, orig, new) in enumerate(zip(bracket, pairs_orig, pairs_new)):
                assert(tuple(pairing.teams) == orig)
                assert((i in swaps or i-1 in swaps) == (orig != new))
                if orig != new:
                    if pairing.conflict_hist:
                        pairing.add_flag("1u1d_hist")
                    if pairing.conflict_inst:
                        pairing.add_flag("1u1d_inst")
                    if not (pairing.conflict_hist or pairing.conflict_inst):
                        pairing.add_flag("1u1d_other")
                    pairing.teams = list(new)


class PowerPairedWithAllocatedSidesDrawGenerator(PowerPairedDrawGenerator):
    """Power-paired draw with allocated sides.
    Overrides functions of PowerPairedDrawGenerator where sides need to be constrained.
    All teams must have an 'allocated_side' attribute which must be either
    'aff' or 'neg' (case-sensitive).
    Options are as for PowerPairedDrawGenerator, except that the allowable values
    for "odd_bracket" are:
        "pullup_top"
        "pullup_bottom"
        "pullup_random"
        "intermediate1" - the excess teams in a bracket begin an intermediate bubble,
            which is filled by teams allocated to the other side from lower brackets,
            starting from the top of the next bracket down and pulling up as many
            teams as necessary. This may involve pulling up teams from multiple
            brackets if there aren't enough in the next bracket down.
        "intermediate2" - the excess teams in a bracket begin an intermediate bubble,
            which is filled by teams allocated to the other side from lower brackets.
            However, if there aren't enough teams in the next bracket down, then only
            those teams are pulled up into this intermediate bracket, and the excess
            teams (of the original excess) form a new, lower, intermediate bubble (but
            still higher than the next bracket down). So there can be multiple
            intermediate bubbles between two brackets.
    """

    DEFAULT_OPTIONS = {
        "odd_bracket"    : "intermediate1",
        "pairing_method" : "fold",
        "avoid_conflicts": None,
    }

    def __init__(self, *args, **kwargs):
        super(PowerPairedWithAllocatedSidesDrawGenerator, self).__init__(*args, **kwargs)
        self.check_teams_for_attribute("allocated_side", choices=["aff", "neg"])

    def _make_raw_brackets(self):
        """Returns an OrderedDict mapping bracket names (normally numbers)
        to (unordered) dicts. Each unordered dict has an 'aff' and a 'neg' key,
        each mapping to a list of teams."""
        brackets = OrderedDict()
        teams = list(self.teams)
        while len(teams) > 0:
            top_team = teams.pop(0)
            points = top_team.points
            pool = {"aff": list(), "neg": list()}
            pool[top_team.allocated_side].append(top_team)
            while len(teams) > 0 and teams[0].points == points:
                team = teams.pop(0)
                side = team.allocated_side
                pool[side].append(team)
            brackets[points] = pool
        return brackets

    ODD_BRACKET_FUNCTIONS = {
        "pullup_top"                  : "_pullup_top",
        "pullup_bottom"               : "_pullup_bottom",
        "pullup_random"               : "_pullup_random",
        "intermediate1"               : "_intermediate_bubbles_1",
        "intermediate2"               : "_intermediate_bubbles_2"
    }

    def _pullup_top(self, brackets):
        self._pullup(brackets, lambda x, num: range(0, num))

    def _pullup_bottom(self, brackets):
        self._pullup(brackets, lambda x, num: range(-num, 0))

    def _pullup_random(self, brackets):
        self._pullup(brackets, lambda x, num: random.sample(list(range(x)), num))

    # Overriding functions for resolving odd brackets:
    def _pullup(self, brackets, indices):
        """'brackets' is what is returned by _make_raw_brackets().
        'pos' is a function taking the number of teams to choose from
        and number of teams required, and returning a list of indices
        for which teams to take as the pullup.
        Operates in-place. Does not remove empty brackets."""

        # Tuples: (teams_list, side, number_needed)
        # List by highest bracket first.
        pullups_needed_for = list()

        for points, pool in brackets.items():

            # First, try to fulfil any pullups needed from higher brackets.
            # There's no guarantee we will have enough teams in this bracket to
            # fulfil all requirements.
            new_pullups_needed_for = list()
            for pullups_needed_teams, side, number_needed in pullups_needed_for:
                # Figure out which team indices we're pulling up.
                if len(pool[side]) < number_needed:
                    # If there are an unsufficient number of teams, pull up all of them
                    # and add to next pullups needed list.
                    pullup_indices = range(len(pool[side]))
                    new_pullups_needed_for.append((pullups_needed_teams, side, number_needed - len(pool[side])))
                else:
                    # Otherwise, pull up the number required.
                    pullup_indices = indices(len(pool[side]), number_needed)

                pullup_teams = list()
                for i in pullup_indices:
                    # Don't use pop, because that mucks up the indices.
                    pullup_team = pool[side][i]
                    self.add_team_flag(pullup_team, "pullup")
                    pullup_teams.append(pullup_team)

                # Now remove those teams from the bracket.
                # Again, avoiding pop, because it changes the indices.
                for team in pullup_teams:
                    pool[side].remove(team)

                # Finally, add our pullup teams to the destination list.
                pullups_needed_teams.extend(pullup_teams)

            # Then, figure out if we need any pullups in *this* bracket.
            aff_surplus = len(pool["aff"]) - len(pool["neg"]) # could be negative
            if aff_surplus > 0:
                new_pullups_needed_for.append((pool["neg"], "neg", aff_surplus))
            elif aff_surplus < 0:
                new_pullups_needed_for.append((pool["aff"], "aff", -aff_surplus))

            # Assign the new pullups-needed list, then start again!
            pullups_needed_for = new_pullups_needed_for

        if pullups_needed_for:
            raise DrawError("Last bracket still needed pullups!\n" + repr(pullups_needed_for))

    @classmethod
    def _intermediate_bubbles_1(cls, brackets):
        """Operates in-place.
        This implements the first intermediate bubbles method, where there is at most
        one intermediate bubble between brackets, but may have pullups from multiple
        brackets.
        """
        new = OrderedDict()
        unfilled = OrderedDict()

        for points, pool in brackets.items():

            to_delete_from_unfilled = []

            # First, check for unfilled intermediate brackets
            for unfilled_points, unfilled_pool in unfilled.items():
                aff_surplus = len(unfilled_pool["aff"]) - len(unfilled_pool["neg"])
                if aff_surplus > 0:
                    # Take the top teams from negative pool as appropriate.
                    # Note that there may not be enough teams; if there aren't,
                    # then this line just takes all of them.
                    unfilled_pool["neg"].extend(pool["neg"][:aff_surplus])
                    del pool["neg"][:aff_surplus]
                elif aff_surplus < 0:
                    # Take the top teams from affirmative pool as appropriate.
                    unfilled_pool["aff"].extend(pool["aff"][:-aff_surplus])
                    del pool["aff"][:-aff_surplus]
                # If the bubble now looks good, move it to the main brackets and
                # mark it for deletion from the unfilled buffer.
                if len(unfilled_pool["aff"]) == len(unfilled_pool["neg"]):
                    new[unfilled_points] = unfilled_pool
                    to_delete_from_unfilled.append(unfilled_points)

            # Delete the unfilled brackets tht were marked for deletion
            for unfilled_points in to_delete_from_unfilled:
                del unfilled[unfilled_points]

            # Find lesser and greater of number of aff and neg teams.
            nums_teams = list(map(len, list(pool.values())))
            n = min(nums_teams)
            m = max(nums_teams)

            # Assign the main bracket
            new[points] = {"aff": pool["aff"][:n], "neg": pool["neg"][:n]}

            # Assign the intermediate bracket, if any
            if m > n:
                unfilled[points-0.5] = {"aff": pool["aff"][n:], "neg": pool["neg"][n:]}

        if unfilled:
            raise DrawError("There are still unfilled intermediate brackets!\n" + repr(unfilled))

        # Currently, the brackets are out of order, since e.g. 3.5 would have been
        # inserted after 3 (or maybe even after 2). Let's change that:
        new_sorted = sorted(list(new.items()), key=lambda x: x[0], reverse=True)

        brackets.clear()
        brackets.update(new_sorted)

    @classmethod
    def _intermediate_bubbles_2(cls, brackets):
        """Operates in-place.
        This implements the second intermediate bubbles method, where all debates
        in the same intermediate bubble have the same number of wins, but there
        might be multiple intermediate bubbles between brackets.
        """

        new = OrderedDict()
        unfilled = OrderedDict()
        intermediates = OrderedDict() # values are lists of {"aff", "neg"} dicts
        for points, pool in brackets.items():

            to_delete_from_unfilled = []

            # First, check for unfilled intermediate brackets
            for unfilled_points, unfilled_pool in unfilled.items():
                intermediates.setdefault(unfilled_points, list())
                if unfilled_pool["aff"] and unfilled_pool["neg"]:
                    raise DrawError("An unfilled pool unexpectedly had both affirmative and negative teams.")
                elif unfilled_pool["aff"]:
                    # In a new bracket, take the lesser of how many excess affirmative
                    # teams there are, and how many negative teams in the pool we have.
                    num_teams = min(len(unfilled_pool["aff"]), len(pool["neg"]))
                    intermediates[unfilled_points].append({
                        "aff": unfilled_pool["aff"][:num_teams],
                        "neg": pool["neg"][:num_teams]
                    })
                    del unfilled_pool["aff"][:num_teams]
                    del pool["neg"][:num_teams]
                elif unfilled_pool["neg"]:
                    # Take the top teams from affirmative pool as appropriate.
                    num_teams = min(len(unfilled_pool["neg"]), len(pool["aff"]))
                    intermediates[unfilled_points].append({
                        "aff": pool["aff"][:num_teams],
                        "neg": unfilled_pool["neg"][:num_teams]
                    })
                    del pool["aff"][:num_teams]
                    del unfilled_pool["neg"][:num_teams]
                # If we've exhausted the unfilled pool, add all these
                # intermediate brackets to the main list of brackets and mark
                # them for deletion from the unfilled buffer.
                if not unfilled_pool["aff"] and not unfilled_pool["neg"]:
                    num_brackets = len(intermediates[unfilled_points])
                    for i, intermediate_pool in enumerate(intermediates[unfilled_points], start=1):
                        intermediate_points = unfilled_points - i / (num_brackets + 1)
                        new[intermediate_points] = intermediate_pool
                    to_delete_from_unfilled.append(unfilled_points)

            # Delete the unfilled brackets tht were marked for deletion
            for unfilled_points in to_delete_from_unfilled:
                del unfilled[unfilled_points]

            # Find lesser and greater of number of aff and neg teams.
            nums_teams = list(map(len, list(pool.values())))
            n = min(nums_teams)
            m = max(nums_teams)

            # Assign the main bracket
            new[points] = {"aff": pool["aff"][:n], "neg": pool["neg"][:n]}

            # Take note of the excess teams, if any
            if m > n:
                unfilled[points] = {"aff": pool["aff"][n:], "neg": pool["neg"][n:]}

        if unfilled:
            raise DrawError("There are still unfilled intermediate brackets!\n" + repr(unfilled))

        # Currently, the brackets are out of order, since e.g. 3.5 would have been
        # inserted after 3 (or maybe even after 2). Let's change that:
        new_sorted = sorted(list(new.items()), key=lambda x: x[0], reverse=True)

        brackets.clear()
        brackets.update(new_sorted)

    def _intermediate_bubbles_with_up_down():
        """This should never be called - the associated option string is removed
        from the allowable list above."""
        raise NotImplementedError("Intermediate bubbles with conflict avoidance isn't supported with allocated sides.")

    @staticmethod
    def _pairings(brackets, presort_func):
        pairings = OrderedDict()
        i = 1
        for points, pool in brackets.items():
            assert len(pool["aff"]) == len(pool["neg"])
            bracket = list()
            presort_func(pool)
            for teams in zip(pool["aff"], pool["neg"]):
                pairing = Pairing(teams=teams, bracket=points, room_rank=i)
                bracket.append(pairing)
                i = i + 1
            pairings[points] = bracket
        return pairings

    @classmethod
    def _pairings_slide(cls, brackets):
        def slide(pool):
            pass # do nothing
        return cls._pairings(brackets, slide)

    @classmethod
    def _pairings_fold(cls, brackets):
        def fold(pool):
            pool["neg"].reverse()
        return cls._pairings(brackets, fold)

    @classmethod
    def _pairings_random(cls, brackets):
        def shuffle(pool):
            random.shuffle(pool["aff"])
            random.shuffle(pool["neg"])
        return cls._pairings(brackets, shuffle)


class FirstEliminationDrawGenerator(BaseDrawGenerator):
    """Class for draw for a round that is a first w round, with
    a number of teams breaking that is not a power of two."""

    can_be_first_round = False
    requires_even_teams = True
    requires_prev_results = False
    draw_type = "elimination"

    DEFAULT_OPTIONS = {
        "break_size": 8,
    }

    def generate(self):
        # Determine who breaks
        break_size = self.options["break_size"]
        breaking_teams = self.teams[:break_size]
        # Determine who debates
        bypassing, debating = self._bypass_debate_split(break_size)
        assert(bypassing + debating == break_size)
        self._bypassing_teams = breaking_teams[:bypassing]
        debating_teams = breaking_teams[-debating:]
        # Pair the debating teams
        debates = len(debating_teams) // 2
        top = debating_teams[:debates]
        bottom = debating_teams[debates:]
        bottom.reverse()
        pairings = list()
        for i, teams in enumerate(zip(top, bottom), start=bypassing+1):
            pairing = Pairing(teams, bracket=0, room_rank=i)
            pairings.append(pairing)
        return pairings

    @staticmethod
    def _bypass_debate_split(number):
        next_pow2 = 1 << (number.bit_length() - 1)
        if next_pow2 == number: # no partial elimination
            return number, 0
        debates = number - next_pow2
        return next_pow2 - debates, 2*debates

    def get_bypassing_teams(self):
        if hasattr(self, "_bypassing_teams"):
            return self._bypassing_teams
        raise RuntimeError("get_bypassing_teams() must not be called before generate().")


class EliminationDrawGenerator(BaseDrawGenerator):
    """Class for second or subsequent elimination round.
    For this draw type, 'teams' should be the teams that automatically
    advanced to this round (i.e., bypassed the previous break round).
    'results' should be a list of Pairings with winners indicated."""

    can_be_first_round = False
    requires_even_teams = False
    requires_prev_results = True
    draw_type = "elimination"

    def generate(self):
        # Check for argument sanity.
        num_teams = len(self.teams) + len(self.results)
        if num_teams != 1 << (num_teams.bit_length() - 1):
            raise RuntimeError("The number of teams in this round is not a power of two")
        self.results.sort(key=lambda x: x.room_rank)
        teams = list(self.teams)
        teams.extend([p.winner for p in self.results])
        debates = len(teams) // 2
        top = teams[:debates]
        bottom = teams[debates:]
        bottom.reverse()
        pairings = list()
        for i, ts in enumerate(zip(top, bottom), start=1):
            pairing = Pairing(ts, bracket=0, room_rank=i)
            pairings.append(pairing)
        return pairings

class RoundRobinDrawGenerator(BaseDrawGenerator):
    """ Class for round-robin stype matchups using divisions """

    can_be_first_round = True
    requires_even_teams = False
    requires_prev_results = False
    draw_type = "preliminary"
    side_allocations = "balance"

    PAIRING_FUNCTIONS = {
        "random": "_pairings_random"
    }


    DEFAULT_OPTIONS = {"max_swap_attempts": 20, "avoid_conflicts": "off"}

    def generate(self):
        self._brackets = self._make_raw_brackets_from_divisions()
        # TODO: resolving brackets with odd numbers here (see resolve_odd_brackets)
        self._pairings = self.generate_pairings(self._brackets)
        # TODO: avoiding history conflicts here
        self._draw = list()
        for bracket in self._pairings.values():
            self._draw.extend(bracket)

        self.balance_sides(self._draw) # operates in-place
        return self._draw

    def _make_raw_brackets_from_divisions(self):
        """Returns an OrderedDict mapping bracket names (normally numbers)
        to lists."""
        brackets = OrderedDict()
        teams = list(self.teams)
        for team in teams:
            # Converting from bracket's name to a float (so it can pretend to be a Bracket)
            division = float(team.division.name)
            if division in brackets:
                brackets[division].append(team)
            else:
                brackets[division] = [team]

        print("------")

        # Assigning bye teams as needed
        for bracket in brackets.values():
            if len(bracket) % 2 != 0:
                from participants.models import Institution, Team
                bye_tournament = bracket[0].tournament
                bye_institution, created = Institution.objects.get_or_create(
                    name="Byes"
                )
                bye_reference = "Bye %s" % bracket[0].division
                bye_division = bracket[0].division
                bye_team = Team(
                    institution = bye_institution,
                    reference = bye_reference,
                    short_reference = "Bye",
                    tournament= bye_tournament,
                    type = "B",
                    use_institution_prefix = False,
                    division = bye_division,
                    cannot_break = True
                )
                bye_team.aff_count = 0
                bye_team.neg_count = 0
                bye_team.save()
                bracket.append(bye_team)
                print("\t Created a bye team for divison %s" % bracket[0].division)

        # Assigning subranks - fixed based on alphabetical
        for bracket in brackets.values():
            bracket.sort(key=lambda x: x.short_name, reverse=False)
            for i, team in enumerate(bracket):
                i += 1
                team.subrank = i

        return brackets

    def determine_effective_round(self, teams_list):
        # This uses previous matchups to determine the offset
        # Essentially figures out (ignore draw.seq) what the previous matchups
        # have been. TODO: This is pretty flawed.
        effective_round = 1
        for i in range(1, len(teams_list)):
            print("\ttesting round %s" % i)
            right_team_index = -1 * i
            if teams_list[0].seen(teams_list[right_team_index]):
                effective_round += 1

        print("effective roud of %s" % effective_round)
        return effective_round


    def generate_pairings(self, brackets):
        pairings = OrderedDict()

        first_bracket_teams = next(iter(brackets.values()))
        effective_round = self.determine_effective_round(first_bracket_teams)
        print("-------\nTaking as effective round of %s" % effective_round)

        for bracket in brackets.items():
            teams_list = bracket[1] # Team Array is second item
            points =  bracket[0]
            total_debates = len(teams_list) // 2
            print("BRACKET %s with %s teams" % (points, len(teams_list)))

            fold_top = teams_list[:total_debates]
            fold_bottom = teams_list[total_debates:]
            fold_bottom.reverse() # Bottom half ranks high to low

            # Reforming the list for the shuffle
            folded_list = list(fold_top)
            folded_list.extend(fold_bottom)

            print(["%s - %s" % (teams_list.index(t) + 1, t) for t in folded_list[:total_debates]])
            print(["%s - %s" % (teams_list.index(t) + 1, t) for t in folded_list[total_debates:]])

            for i in range(1, effective_round):
                 # left-most bottom goes to position[1] on the top
                folded_list.insert(1, (folded_list.pop(total_debates)))
                # right-most top goes to right-most bottom
                folded_list.append(folded_list.pop(total_debates))
                #print "popping %s iteration %s" % (i, total_debates)

            print(["%s - %s" % (teams_list.index(t) + 1, t) for t in folded_list[:total_debates]])
            print(["%s - %s" % (teams_list.index(t) + 1, t) for t in folded_list[total_debates:]])

            # IE For Round 2 - before and after
            # ['1 - Aquinas 1', '2 - Aquinas 2', '3 - Penrhos 1']
            # ['6 - Santa Maria 1', '5 - Rossmoyne 2', '4 - Rossmoyne 1']
            # popping 1 iteration 3
            # ['1 - Aquinas 1', '6 - Santa Maria 1', '2 - Aquinas 2']
            # ['5 - Rossmoyne 2', '4 - Rossmoyne 1', '3 - Penrhos 1']

            assigned_teams = []
            assigned_pairings = []
            for paired_teams in zip(folded_list[:total_debates], folded_list[total_debates:]):
                aff = paired_teams[0]
                neg = paired_teams[1]
                # Iterating through each half and matching - ie 1-4, 2-5, 3-6
                if neg:
                    pairing = Pairing(
                        teams=(paired_teams),
                        bracket=points,
                        room_rank=1,
                        division=aff.division
                    )
                    print("\t matchup is %s (%s) vs %s (%s)" % (aff, teams_list.index(aff) + 1, neg, teams_list.index(neg) + 1))
                    assigned_pairings.append(pairing)
                    assigned_teams.append(aff)
                    assigned_teams.append(neg)
                else:
                    # Need to deal with Byes and the like here
                    print("couldn't find an opposition")

            pairings[points] = assigned_pairings



        return pairings


class ManualDrawGenerator(BaseDrawGenerator):
    """ Class for round-robin stype matchups using divisions """

    can_be_first_round = True
    requires_even_teams = False
    requires_prev_results = False

    def generate(self):
        self._draw = list()
        return self._draw
