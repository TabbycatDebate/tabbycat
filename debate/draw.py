from collections import OrderedDict
import random

class Pairing(object):
    """Simple data structure for communicating information about pairings.
    Draws always return a list of these."""

    def __init__(self, teams, bracket, room_rank, flags=[]):
        """'teams' must be a list of two teams."""
        self.teams     = teams
        self.bracket   = bracket
        self.room_rank = room_rank
        self.flags     = flags

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

    def swap_sides(self):
        self.teams.reverse()

class DrawError(Exception):
    pass

class BaseDraw(object):
    """Base class for all draw types.
    Options:
        "balance_sides" - Give affirmative side to team that has affirmed less.
            Requires teams to have 'aff_count' attribute. If off, randomizes
            sides.
        "avoid_history" - if True, draw tries to avoid pairing teams that have
            seen each other before, and tries harder if they've seen each other
            multiple times.
        "avoid_institution" - if True, draw tries to avoid pairing teams that
            are from the same institution, and tries harder if either team
            has seen their own institution multiple times.
        """

    BASE_DEFAULT_OPTIONS = {
        "balance_sides"    : True,
        "avoid_history"    : True,
        "avoid_institution": True
    }

    can_be_first_round = NotImplemented

    # All subclasses must define this with any options that may exist.
    # It's not necessary for them to include these; the constructor will
    # do that.
    DEFAULT_OPTIONS = {}

    def __init__(self, teams, **kwargs):
        self.teams = teams

        # Compute the full dictionary of default options
        self.options = self.BASE_DEFAULT_OPTIONS.copy()
        self.options.update(self.DEFAULT_OPTIONS)

        # Check that all options actually exist
        for key in kwargs:
            if key not in self.options:
                raise ValueError("Unrecognized option: {0}".format(key))

        # Update
        self.options.update(kwargs)


class PowerPairedDraw(BaseDraw):
    """Power-paired draw.
    Options:
        "odd_bracket" - Odd bracket resolution method:
            "pullup_top", "pullup_bottom", "pullup_random", "intermediate",
            or a function.
        "pairing_method" - How to pair teams:
            "slide", "fold", "random" or a function.
        "avoid_conflict"  - How to avoid conflicts.
            "one_up_one_down"
            can be None, which turns off conflict avoidance.
    """

    can_be_first_round = False

    DEFAULT_OPTIONS = {
        "odd_bracket"    : "pullup_top",
        "pairing_method" : "slide",
        "avoid_conflicts": "one_up_one_down"
    }

    def get_draw(self):
        self._brackets = self._make_raw_brackets()
        self.resolve_odd_brackets(self._brackets) # operates in-place
        self._draw = self.generate_pairings(self._brackets)
        self.avoid_conflicts(self._draw) # operates in-place
        self.balance_affs(self._draw) # operates in-place
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
        pairings = list()
        i = 1
        for points, teams in brackets.iteritems():
            top, bottom = subpool_func(teams)
            for teams in zip(top, bottom):
                pairing = Pairing(teams=teams, bracket=points, room_rank=i)
                pairings.append(pairing)
                i = i + 1
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
        function = self._get_option_function("pairing_method", self.PAIRING_FUNCTIONS)
        return function(pairings)

    @staticmethod
    def _one_up_one_down(pairings):


