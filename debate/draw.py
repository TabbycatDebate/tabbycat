from collections import OrderedDict
import random

class Debate(object):
    """Simple data structure for communicating information about debates.
    Draws always return a list of these."""

    def __init__(self, aff_team, neg_team, bracket, room_rank, flags=[]):
        self.teams     = [aff_team, neg_team]
        self.bracket   = bracket
        self.room_rank = room_rank
        self.flags     = flags

    @property
    def aff_team(self):
        return self.teams[0]

    @property
    def neg_team(self):
        return self.teams[1]

    def swap_sides(self):
        self.teams.reverse()

class DrawError(Exception):
    pass

class BaseDraw(object):
    """Base class for all draw types."""

    BASE_DEFAULT_OPTIONS = {
        "balance_affs"     : True,
        "history_limit"    : 1,
        "institution_limit": 1,
    }

    can_be_first_round = NotImplemented

    # All subclasses must define this with any options that may exist.
    # It's not necessary for them to include these; the constructor will
    # do that.
    DEFAULT_OPTIONS = {}

    def __init__(self, standings, **kwargs):
        self.standings = standings

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
        "odd_bracket"   : "pullup_top",
        "pairing_method": "slide",
        "avoid_conflict": "one_up_one_down"
    }

    def get_draw(self):
        self._brackets = self._make_raw_brackets()
        self.resolve_odd_brackets(self._brackets) # operates in-place
        self._draw = self.generate_pairings(self._brackets)
        self._draw = self.avoid_conflicts(self._draw)
        self._draw = self.balance_affs(self._draw)
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

    # Odd bracket resolutions

    @classmethod
    def _pullup_top(cls, brackets):
        cls._pullup(brackets, lambda x: 0)

    @classmethod
    def _pullup_bottom(cls, brackets):
        cls._pullup(brackets, lambda x: -1)

    @classmethod
    def _pullup_random(cls, brackets):
        cls._pullup(brackets, lambda x: random.randrange(len(x)))

    @staticmethod
    def _pullup(brackets, pos):
        pullup_needed = None
        for points, teams in brackets.iteritems():
            if pullup_needed:
                pullup_needed.append(teams.pop(pos(teams)))
                pullup_needed = 0
            if len(teams) % 2 != 0:
                pullup_needed = teams
        if pullup_needed:
            raise DrawError("Last bracket is odd!")

    @classmethod
    def _intermediate_bubbles(self, brackets):
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
        brackets.clear()
        brackets.update(new)

    ODD_BRACKET_FUNCTIONS = {
        "pullup_top"   : _pullup_top,
        "pullup_bottom": _pullup_bottom,
        "pullup_random": _pullup_random,
        "intermediate" : _intermediate_bubbles
    }

    @property
    def resolve_odd_brackets(self):
        """Returns a function taking an OrderedDict as returned by
        _make_raw_brackets(), and returning an OrderedDict of similar
        form but guaranteeing that all brackets have an even number
        of teams."""
        option = self.options["odd_bracket"]
        if callable(option):
            return option
        try:
            return self.ODD_BRACKET_FUNCTIONS[option]
        except KeyError:
            raise ValueError("Invalid option for odd_bracket: {0}".format(option))

brackets = OrderedDict([
    (4, [1, 2, 3, 4, 5]),
    (3, [6, 7, 8, 9]),
    (2, [10, 11, 12, 13, 14]),
    (1, [15, 16])
])
print brackets
import copy
ODD_BRACKET_FUNCTIONS = {
    "pullup_top"   : PowerPairedDraw._pullup_top,
    "pullup_bottom": PowerPairedDraw._pullup_bottom,
    "pullup_random": PowerPairedDraw._pullup_random,
    "intermediate" : PowerPairedDraw._intermediate_bubbles
}
for name, func in ODD_BRACKET_FUNCTIONS.iteritems():
    print name
    b2 = copy.deepcopy(brackets)
    func(b2)
    print b2

