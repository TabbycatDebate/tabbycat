"""Pairing classes.

The pairing classes hold basic information about pairings for communication to
and from other modules.

Draw generators always return a list of pairings (`Pairing` for two-team formats,
`BPPairing` for BP).

Draw generators that take results from the previous round, namely elimination
rounds after the first elimination round, expect to be given a list of pairings.
For this purpose, special "result pairing" classes should be used
(ResultPairing` for two-team formats, `BPEliminationResultPairing` for BP).
These classes add the ability to store the winning (two- team) or advancing (BP)
teams from the debate represented by the pairing.

As much as possible, these classes do not make database queries. Their intent is
to be a Python-only data structure, with a few smarts where convenient. The one
exception is the class method `.from_debate(debate)`, which is provided for
convenience for callers to construct a pairing (typically a result pairing)
from a `Debate` instance.
"""

import logging
import random

from .common import DrawFatalError

logger = logging.getLogger(__name__)


class BasePairing:
    """The Pairing classes hold basic information about pairings for
    communication with other modules. Draw generators always return a list of
    them.

    This is a base class for functionality common to both two-team pairings and
    BP pairings."""

    def __init__(self, teams, bracket, room_rank, flags=[], team_flags={}):
        """'teams' must be a list of two teams, or four teams if it's for BP.
        'bracket' and 'room_rank' are both integers.
        'flags' is a list of strings."""
        self.teams = list(teams)
        self.bracket = bracket
        self.room_rank = room_rank
        self.flags = list(flags)
        self.team_flags = dict(team_flags)

    @classmethod
    def from_debate(cls, debate, tournament=None):
        """Convenience constructor, constructs object from Debate model
        instance. `tournament` can be passed in to avoid redundant SQL queries.
        """
        if tournament is None:
            tournament = debate.round.tournament
        teams = [debate.get_team(side) for side in cls.sides] # order matters
        bracket = debate.bracket
        room_rank = debate.room_rank
        flags = debate.flags
        team_flags = {
            debate.get_team(side): debate.get_dt(side).flags
            for side in tournament.sides
        }
        return cls(teams, bracket=bracket, room_rank=room_rank, flags=flags,
                team_flags=team_flags)

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
        return None

    def shuffle_sides(self):
        """Randomly allocate sides."""
        random.shuffle(self.teams)


class Pairing(BasePairing):
    """Pairing class for two-team formats."""

    sides = ['aff', 'neg']

    def __init__(self, teams, bracket, room_rank, flags=[], team_flags={}):
        super().__init__(teams, bracket, room_rank, flags, team_flags)
        assert len(self.teams) == 2, "There must be two teams in a Pairing"

    def __repr__(self):
        return ("<{p.__class__.__name__}: {p.teams[0]} vs {p.teams[1]} "
            "({p.bracket}/{p.room_rank})>").format(p=self)

    def balance_sides(self):
        """Puts whoever has the biggest (aff - neg) difference on the negative
        side, or chooses randomly if this is the same for both teams."""

        aff_affs, aff_negs = self.teams[0].side_history
        neg_affs, neg_negs = self.teams[1].side_history
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


class ResultPairing(Pairing):
    """Adds functionality for storing information about the winning team.
    This class is the data structure expected by DrawGenerator classes, when
    taking information about the results of the previous round."""

    def __init__(self, teams, bracket, room_rank, flags=[], team_flags={}, winner=None):
        super().__init__(teams, bracket, room_rank, flags, team_flags)
        self.set_winner(winner)

    @classmethod
    def from_debate(cls, debate, tournament=None):
        instance = super().from_debate(debate, tournament)
        winner = debate.confirmed_ballot.result.winning_team() if debate.confirmed_ballot else None
        instance.set_winner(winner)
        return instance

    def set_winner(self, team):
        """Sets the winner of the debate. Raises ValueError if the team isn't
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

    def __init__(self, teams, bracket, room_rank, flags=[], team_flags={}):
        super().__init__(teams, bracket, room_rank, flags, team_flags)
        assert len(self.teams) == 4, "There must be four teams in a BPPairing"

    def __repr__(self):
        return "<{p.__class__.__name__}: {teams} ({p.bracket}/{p.room_rank})>".format(
            teams=", ".join(map(str, self.teams)), p=self)


class BPEliminationResultPairing(BPPairing):
    """Adds functionality for storing information about the advancing teams.
    This class is the data structure expected by DrawGenerator classes, when
    taking information about the results of the previous round."""

    def __init__(self, teams, bracket, room_rank, flags=[], team_flags={}, advancing=[]):
        super().__init__(teams, bracket, room_rank, flags, team_flags)
        self.set_advancing(advancing)

    @classmethod
    def from_debate(cls, debate, tournament=None):
        instance = super().from_debate(debate, tournament)
        advancing = debate.confirmed_ballot.result.advancing_teams() if debate.confirmed_ballot else []
        instance.set_advancing(advancing)
        return instance

    def set_advancing(self, advancing):
        """Sets the advancing teams. Raises ValueError if the team isn't in the
        pairing."""
        self._advancing_indices = [self.teams.index(team) for team in advancing]

    @property
    def advancing(self):
        return [self.teams[i] for i in self._advancing_indices]
