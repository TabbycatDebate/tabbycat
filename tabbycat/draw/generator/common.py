import logging

from django.utils.translation import gettext as _

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


class BaseDrawGenerator:
    """Base class for generators for all draw types, for both two-team and BP.
    """

    # Subclasses must define BASE_DEFAULT_OPTIONS

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
            message = "{0} out of {1} teams have an invalid '{name}' attribute.".format(offending_teams, len(self.teams), name=name)
            if choices:
                message += " Valid choices: " + ", ".join(map(repr, choices))
            raise DrawFatalError(message)


class BasePairDrawGenerator(BaseDrawGenerator):
    """Base class for generators for all draw types.
    Options:
        "side_allocations" - Side allocation method, one of:
            "balance" - the team that has affirmed less in prior rounds affirms,
                or randomly if both teams have affirmed the same number of times.
                If used, team objects must have an `side_history` attribute.
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
        "institution_penalty": 1,
    }

    TEAMS_PER_DEBATE = 2

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


class EliminationDrawMixin:
    """Mixin for elimination draws."""

    def generate(self):
        pairings = self.make_pairings()
        self.shuffle_sides(pairings)
        return pairings

    def shuffle_sides(self, pairings):
        for pairing in pairings:
            pairing.shuffle_sides()

    def make_pairings(self):
        raise NotImplementedError


class ManualDrawGenerator(BaseDrawGenerator):
    """Returns an empty draw.
    Since this doesn't really do anything, it works for both two-team and BP.
    """
    DEFAULT_OPTIONS = {}
    BASE_DEFAULT_OPTIONS = {}
    requires_even_teams = False
    requires_prev_results = False

    def generate(self):
        return []
