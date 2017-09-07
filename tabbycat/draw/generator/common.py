import logging
import random

from django.utils.translation import ugettext as _

logger = logging.getLogger(__name__)


class BaseDrawError(Exception):
    pass


class DrawUserError(BaseDrawError):
    """DrawUserError is raised by any DrawGenerator class when a problem that
    would appear to be user error prevents a draw from being produced.
    DrawUserErrors are caught by the view class and shown to the user as an
    error message.

    Because DrawUserErrors expected and rectifier, the strings that go into them
    should be internationalised (marked for translation)."""
    pass


class DrawFatalError(BaseDrawError):
    """DrawAlgorithmError is raised by any DrawGenerator class when a problem
    that is an error condition that should never (ever) happen prevents a draw
    from being produced. DrawAlgorithmError are also caught by the view class
    and shown to the user as an error message. However, because they should
    never happen, their messages are not internationalised, since that just
    creates unnecessary work for translators."""
    pass


class BasePairing:
    """The Pairing classes hold basic information about pairings for
    communication with other modules. Draw generators always return a list of
    them.

    This is a base class for functionality common to both two-team pairings and
    BP pairings."""

    def __init__(self, teams, bracket, room_rank, flags=[], team_flags={}, division=None):
        """'teams' must be a list of two teams, or four teams if it's for BP.
        'bracket' and 'room_rank' are both integers.
        'flags' is a list of strings."""
        self.teams = list(teams)
        self.bracket = bracket
        self.room_rank = room_rank
        self.flags = list(flags)
        self.team_flags = dict(team_flags)
        self.division = division

    @classmethod
    def from_debate(cls, debate):
        teams = [debate.get_team(side) for side in cls.sides] # order matters
        bracket = debate.bracket
        room_rank = debate.room_rank
        flags = debate.flags.split(",")
        team_flags = {debate.aff_team: debate.aff_team.flags.split(","), debate.neg_team: debate.neg_team.flags.split(",")}
        division = debate.division
        return cls(teams, bracket, room_rank, flags, team_flags, division)

    def add_flag(self, flag):
        self.flags.append(flag)

    def add_flags(self, flags):
        self.flags.extend(flags)

    def add_team_flags(self, team, flags):
        self.team_flags.setdefault(team, list()).extend(flags)

    def get_team_flags(self, team):
        if team not in self.teams:
            logger.error("Tried to get flags for team %r in pairing %r", team, self)
        return self.team_flags.get(team, [])

    @property
    def venue_category(self):
        """Abstracted to allow future extension to more causes of venue groups,
        e.g. accessibility."""
        return self.division.venue_category if self.division else None

    def shuffle_sides(self):
        """Randomly allocate sides."""
        random.shuffle(self.teams)


class Pairing(BasePairing):
    """Pairing class for two-team formats."""

    sides = ['aff', 'neg']

    def __init__(self, teams, bracket, room_rank, flags=[], team_flags={}, winner=None, division=None):
        super().__init__(teams, bracket, room_rank, flags, team_flags, division)
        assert len(self.teams) == 2, "There must be two teams in a Pairing"
        self.set_winner(winner)

    @classmethod
    def from_debate(cls, debate):
        instance = super().from_debate(debate)
        winner = debate.confirmed_ballot.result.winning_team() if debate.confirmed_ballot else None
        instance.set_winner(winner)
        return instance

    def __repr__(self):
        return "<Pairing: {0} vs {1} ({2}/{3})>".format(
            self.teams[0], self.teams[1], self.bracket, self.room_rank)

    def balance_sides(self):
        """Puts whoever has the biggest (aff - neg) difference on the negative
        side, or chooses randomly if this is the same for both teams."""

        aff_affs, aff_negs = self.teams[0].side_counts
        neg_affs, neg_negs = self.teams[1].side_counts
        aff_imbalance = aff_affs - aff_negs
        neg_imbalance = neg_affs - neg_negs

        if aff_imbalance < neg_imbalance:
            pass
        elif neg_imbalance < aff_imbalance:
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
            # In theory redundant, since DrawGenerators should use check_teams_for_attribute
            # to check for this.
            raise DrawFatalError("For conflict avoidance, teams must have an attribute 'institution'.")

    @property
    def conflict_hist(self):
        """Returns True if teams have seen each other before.
        Relies on seen() being implemented by the teams."""
        try:
            return self.teams[0].seen(self.teams[1])
        except AttributeError:
            # In theory redundant, since DrawGenerators should use check_teams_for_attribute
            # to check for this.
            raise DrawFatalError("For conflict avoidance, teams must have an attribute 'seen'.")

    def set_winner(self, team):
        """Sets the winner of the Pairing. Raises ValueError if the team isn't
        in the pairing."""
        if team is None:
            self._winner_index = None
        else:
            self._winner_index = self.teams.index(team)

    @property
    def winner(self):
        if self._winner_index is None:
            return None
        return self.teams[self._winner_index]


class BPPairing(BasePairing):
    """Pairing class for British Parliamentary."""

    sides = ['og', 'oo', 'cg', 'co']

    def __init__(self, teams, bracket, room_rank, flags=[], team_flags={}, division=None):
        super().__init__(teams, bracket, room_rank, flags, team_flags, division)
        assert len(self.teams) == 4, "There must be four teams in a BPPairing"

    def __repr__(self):
        return "<BPPairing: {teams} ({p.bracket}/{p.room_rank})>".format(
            teams=", ".join(map(str, self.teams)), p=self)


class BaseDrawGenerator:
    """Base class for generators for all draw types, for both two-team and BP.
    """

    # Subclasses must define BASE_DEFAULT_OPTIONS

    can_be_first_round = True
    requires_even_teams = True
    requires_prev_results = False
    requires_rrseq = False

    def __init__(self, teams, results=None, rrseq=None, **kwargs):
        self.teams = teams
        self.team_flags = dict()
        self.results = results
        self.rrseq = rrseq

        if self.requires_even_teams:
            if not len(self.teams) % self.TEAMS_PER_DEBATE == 0:
                raise DrawUserError(_("The number of teams presented for the draw was not "
                        "a multiple of %(num)d.") % {'num': self.TEAMS_PER_DEBATE})
            if not self.teams:
                raise DrawUserError(_("There were no teams for the draw."))

        if results is None and self.requires_prev_results:
            raise TypeError("'results' is required for draw of type {0:s}".format(
                    self.__class__.__name__))

        if results is not None and not self.requires_prev_results:
            logger.warning("'results' not required for draw of type %s, will probably be ignored",
                    self.__class__.__name__)

        if rrseq is None and self.requires_rrseq:
            raise TypeError("'rrseq' (round robin sequence) is required for draw of type {0:s}".format(
                    self.__class__.__name__))

        # Compute the full dictionary of default options
        self.options = self.BASE_DEFAULT_OPTIONS.copy()
        self.options.update(self.DEFAULT_OPTIONS)
        unrecognised = [key for key in kwargs if key not in self.options]
        if unrecognised:
            raise ValueError("Unrecognised options: " + ", ".join(unrecognised))
        self.options.update(kwargs)

    def generate(self):
        """Abstract method."""
        raise NotImplementedError

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
                    pairing.add_team_flags(team, self.team_flags[team])

    @classmethod
    def available_options(cls):
        keys = set(cls.BASE_DEFAULT_OPTIONS.keys())
        keys |= set(cls.DEFAULT_OPTIONS.keys())
        return sorted(list(keys))

    def check_teams_for_attribute(self, name, choices=None, checkfunc=None):
        """Checks that all teams have the specified attribute, and raises a
        DrawFatalError if they don't. This should be called during the
        constructor. Note: Whether to run this check will sometimes be
        conditional on options supplied to the DrawGenerator. 'name' is the name
        of the attribute. 'choices', if specified, is a list of allowed values
        for the attribute.
        """
        has_attribute = [hasattr(x, name) for x in self.teams]
        if not all(has_attribute):
            offending_teams = has_attribute.count(False)
            raise DrawFatalError("{0} out of {1} teams don't have a '{name}' attribute.".format(
                offending_teams, len(self.teams), name=name))

        if choices:
            attribute_value_valid = [getattr(x, name) in choices for x in self.teams]
        elif checkfunc:
            attribute_value_valid = [checkfunc(getattr(x, name)) for x in self.teams]
        else:
            return

        if not all(attribute_value_valid):
            offending_teams = attribute_value_valid.count(False)
            raise DrawFatalError("{0} out of {1} teams has an invalid '{name}' attribute. Valid choices: ".format(
                offending_teams, len(self.teams), name=name) + ", ".join(map(repr, choices)))


class BasePairDrawGenerator(BaseDrawGenerator):
    """Base class for generators for all draw types.
    Options:
        "side_allocations" - Side allocation method, one of:
            "balance" - the team that has affirmed less in prior rounds affirms,
                or randomly if both teams have affirmed the same number of times.
                If used, team objects must have an `side_counts` attribute.
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

    TEAMS_PER_DEBATE = 2

    can_be_first_round = True
    requires_even_teams = True
    requires_prev_results = False
    requires_rrseq = False

    # All subclasses must define this with any options that may exist.
    DEFAULT_OPTIONS = {}

    def __init__(self, teams, results=None, rrseq=None, **kwargs):
        super().__init__(teams, results, rrseq, **kwargs)

        # Check for required team attributes. Subclasses might do more.
        if self.options["avoid_history"]:
            self.check_teams_for_attribute("seen", checkfunc=callable)
        if self.options["avoid_institution"]:
            self.check_teams_for_attribute("institution")

    def allocate_sides(self, pairings):
        if self.options["side_allocations"] == "balance":
            for pairing in pairings:
                pairing.balance_sides()
        elif self.options["side_allocations"] == "random":
            for pairing in pairings:
                pairing.shuffle_sides()
        elif self.options["side_allocations"] not in ["none", "preallocated"]:
            raise ValueError("side_allocations setting not recognized: {0!r}".format(self.options["side_allocations"]))


class BaseBPDrawGenerator(BaseDrawGenerator):
    BASE_DEFAULT_OPTIONS = {}
    TEAMS_PER_DEBATE = 4


class ManualDrawGenerator(BaseDrawGenerator):
    """Returns an empty draw."""

    can_be_first_round = True
    requires_even_teams = False
    requires_prev_results = False

    def generate(self):
        return []
