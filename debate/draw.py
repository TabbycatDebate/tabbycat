from collections import OrderedDict
import random
import copy
from one_up_one_down import OneUpOneDownSwapper
from warnings import warn

class DrawError(Exception):
    pass

class Pairing(object):
    """Simple data structure for communicating information about pairings.
    Draws always return a list of these."""

    def __init__(self, teams, bracket, room_rank, flags=[], winner=None):
        """'teams' must be a list of two teams."""
        self.teams         = list(teams)
        self.bracket       = bracket
        self.room_rank     = room_rank
        self.flags         = list(flags)
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
        """Puts whoever has affirmed less on the affirmative sides,
        or chooses randomly if they've done it equally."""
        if self.teams[0].aff_count < self.teams[1].aff_count:
            pass
        elif self.teams[0].aff_count > self.teams[1].aff_count:
            self.teams.reverse()
        else:
            random.shuffle(self.teams)

    @property
    def conflict_inst(self):
        """Returns True if both teams are from the same institution.
        Relies on the institution attribute of teams."""
        try:
            return self.teams[0].institution == self.teams[1].institution
        except AttributeError:
            raise DrawError("For conflict avoidance, teams must have an attribute 'institution'.")

    @property
    def conflict_hist(self):
        """Returns True if teams have seen each other before.
        Relies on seen() being implemented by the teams."""
        try:
            return self.teams[0].seen(self.teams[1])
        except AttributeError:
            raise DrawError("For conflict avoidance, teams must have an attribute 'seen'.")

    def add_flag(self, flag):
        self.flags.append(flag)

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


class BaseDraw(object):
    """Base class for all draw types.
    Options:
        "balance_sides" - Give affirmative side to team that has affirmed less.
            Requires teams to have 'aff_count' attribute. If off, randomizes
            sides.
        "avoid_history" - if True, draw tries to avoid pairing teams that have
            seen each other before, and tries harder if they've seen each other
            multiple times.
        "history_penalty" -
        "avoid_institution" - if True, draw tries to avoid pairing teams that
            are from the same institution.
        """

    BASE_DEFAULT_OPTIONS = {
        "balance_sides"      : True,
        "avoid_history"      : True,
        "avoid_institution"  : True,
        "history_penalty"    : 1e2,
        "institution_penalty": 1
    }

    can_be_first_round = NotImplemented
    requires_prev_results = False
    draw_type = NotImplemented

    # All subclasses must define this with any options that may exist.
    DEFAULT_OPTIONS = {}

    def __init__(self, teams, results=None, **kwargs):
        self.teams = teams

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

    def balance_sides(self, pairings):
        if not self.options["balance_sides"]:
            return
        for pairing in pairings:
            pairing.balance_sides()

    def make_draw(self):
        """Abstract method."""
        raise NotImplementedError

class RandomDraw(BaseDraw):
    """Random draw.
    Options:
        "max_swap_attempts": Maximum number of times to attempt to swap to
            avoid conflict before giving up.
    """

    can_be_first_round = True
    requires_prev_results = False
    draw_type = "preliminary"

    DEFAULT_OPTIONS = {"max_swap_attempts": 20}


    def make_draw(self):
        self._draw = self._make_initial_pairings()
        self.avoid_conflicts(self._draw) # operates in-place
        self.balance_sides(self._draw) # operates in-place
        return self._draw

    def _make_initial_pairings(self):
        teams = list(self.teams) # make a copy
        random.shuffle(teams)
        debates = len(teams)/2
        pairings = list()
        pairings = [Pairing(teams=t, bracket=0, room_rank=0) \
                for t in zip(teams[:debates], teams[debates:])]
        return pairings

    def avoid_conflicts(self, pairings):
        if not (self.options["avoid_history"] or self.options["avoid_institution"]):
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
            score += sum(map(lambda x: x.conflict_hist, pairings)) * self.options["history_penalty"]
        if self.options["avoid_institution"]:
            score += sum(map(lambda x: x.conflict_inst, pairings)) * self.options["institution_penalty"]
        return score

class PowerPairedDraw(BaseDraw):
    """Power-paired draw.
    Options:
        "odd_bracket" - Odd bracket resolution method:
            "pullup_top", "pullup_bottom", "pullup_random", "intermediate",
            or a function.
        "pairing_method" - How to pair teams:
            "slide", "fold", "random" or a function.
        "avoid_conflict" - How to avoid conflicts.
            "one_up_one_down"
            can be None, which turns off conflict avoidance.
    """

    can_be_first_round = False
    requires_prev_results = False
    draw_type = "preliminary"

    DEFAULT_OPTIONS = {
        "odd_bracket"    : "pullup_top",
        "pairing_method" : "slide",
        "avoid_conflicts": "one_up_one_down"
    }

    def make_draw(self):
        self._brackets = self._make_raw_brackets()
        self.resolve_odd_brackets(self._brackets) # operates in-place
        self._pairings = self.generate_pairings(self._brackets)
        self.avoid_conflicts(self._pairings) # operates in-place
        self._draw = list()
        for bracket in self._pairings.itervalues():
            self._draw.extend(bracket)

        self.balance_sides(self._draw) # operates in-place
        return self._draw

    def _get_option_function(self, option_name, option_dict):
        option = self.options[option_name]
        if callable(option):
            return option
        try:
            return getattr(self, option_dict[option])
        except KeyError:
            raise ValueError("Invalid option for {1}: {0}".format(option, option_name))

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
        "pullup_top"   : "_pullup_top",
        "pullup_bottom": "_pullup_bottom",
        "pullup_random": "_pullup_random",
        "intermediate" : "_intermediate_bubbles"
    }

    def resolve_odd_brackets(self, brackets):
        """Returns a function taking an OrderedDict as returned by
        _make_raw_brackets(), and adjusting that OrderedDict in-place to
        guarantee that all brackets have an even number of teams."""
        function = self._get_option_function("odd_bracket", self.ODD_BRACKET_FUNCTIONS)
        return function(brackets)

    @classmethod
    def _pullup_top(cls, brackets):
        cls._pullup(brackets, lambda x: 0)

    @classmethod
    def _pullup_bottom(cls, brackets):
        cls._pullup(brackets, lambda x: -1)

    @classmethod
    def _pullup_random(cls, brackets):
        cls._pullup(brackets, lambda x: random.randrange(x))

    @staticmethod
    def _pullup(brackets, pos):
        """'brackets' is what is returned by _make_raw_brackets().
        'pos' is a function taking the number of teams to choose from,
        and returning an index for which team to take as the pullup."""
        pullup_needed = None
        for points, teams in brackets.iteritems():
            if pullup_needed:
                pullup_needed.append(teams.pop(pos(len(teams))))
                pullup_needed = 0
            if len(teams) % 2 != 0:
                pullup_needed = teams
        if pullup_needed:
            print brackets
            raise DrawError("Last bracket is still odd!")

    @classmethod
    def _intermediate_bubbles(cls, brackets):
        new = OrderedDict()
        odd_team = None
        for points, teams in brackets.iteritems():
            if odd_team:
                new[points+0.5] = [odd_team, teams.pop(0)]
                odd_team = None
            if len(teams) % 2 != 0:
                odd_team = teams.pop()
            if len(teams) > 0:
                new[points] = teams
        if odd_team:
            raise DrawError("Last bracket is still odd!")
        brackets.clear()
        brackets.update(new)

    ## Pairings generation

    PAIRING_FUNCTIONS = {
        "fold"  : "_pairings_fold",
        "slide" : "_pairings_slide",
        "random": "_pairings_random"
    }

    def generate_pairings(self, brackets):
        """Returns a function taking an OrderedDict as returned by
        resolve_odd_brackets(), and returning a list of Debates."""
        function = self._get_option_function("pairing_method", self.PAIRING_FUNCTIONS)
        return function(brackets)

    @staticmethod
    def _pairings(brackets, subpool_func):
        pairings = OrderedDict()
        i = 1
        for points, teams in brackets.iteritems():
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
            num_debates = len(teams) / 2
            top = teams[:num_debates]
            bottom = teams[num_debates:]
            return top, bottom
        return cls._pairings(brackets, slide)

    @classmethod
    def _pairings_fold(cls, brackets):
        def fold(teams):
            num_debates = len(teams) / 2
            top = teams[:num_debates]
            bottom = teams[num_debates:]
            bottom.reverse()
            return top, bottom
        return cls._pairings(brackets, fold)

    @classmethod
    def _pairings_random(cls, brackets):
        def shuffle(teams):
            num_debates = len(teams) / 2
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
        if self.options["avoid_conflicts"] is None:
            return
        function = self._get_option_function("avoid_conflicts", self.AVOID_CONFLICT_FUNCTIONS)
        return function(pairings)

    def _one_up_one_down(self, pairings):
        """We pass the pairings to one_up_one_down.py, then infer annotations
        based on the result."""

        for bracket in pairings.itervalues():
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
                        pairing.add_flag("1u1d_history")
                    if pairing.conflict_inst:
                        pairing.add_flag("1u1d_institution")
                    if not (pairing.conflict_hist or pairing.conflict_inst):
                        pairing.add_flag("1u1d_other")
                    pairing.teams = list(new)

class FirstEliminationDraw(BaseDraw):
    """Class for draw for a round that is a first w round, with
    a number of teams breaking that is not a power of two."""

    can_be_first_round = False
    requires_prev_results = False
    draw_type = "elimination"

    DEFAULT_OPTIONS = {
        "break_size": 8,
    }

    def make_draw(self):
        # Determine who breaks
        break_size = self.options["break_size"]
        breaking_teams = self.teams[:break_size]
        # Determine who debates
        bypassing, debating = self._bypass_debate_split(break_size)
        assert(bypassing + debating == break_size)
        self._bypassing_teams = breaking_teams[:bypassing]
        debating_teams = breaking_teams[-debating:]
        # Pair the debating teams
        debates = len(debating_teams)/2
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
        raise RuntimeError("get_bypassing_teams() must not be called before make_draw().")

class EliminationDraw(BaseDraw):
    """Class for second or subsequent elimination round.
    For this draw type, 'teams' should be the teams that automatically
    advanced to this round (i.e., bypassed the previous break round).
    'results' should be a list of Pairings with winners indicated."""

    can_be_first_round = False
    requires_prev_results = True
    draw_type = "elimination"

    def make_draw(self):
        # Check for argument sanity.
        num_teams = len(self.teams) + len(self.results)
        if num_teams != 1 << (num_teams.bit_length() - 1):
            raise RuntimeError("The number of teams in this round is not a power of two")
        self.results.sort(key=lambda x: x.room_rank)
        teams = list(self.teams)
        teams.extend([p.winner for p in self.results])
        debates = len(teams)/2
        top = teams[:debates]
        bottom = teams[debates:]
        bottom.reverse()
        pairings = list()
        for i, ts in enumerate(zip(top, bottom), start=1):
            pairing = Pairing(ts, bracket=0, room_rank=i)
            pairings.append(pairing)
        return pairings