"""Scoresheet classes.

The scoresheet classes are responsible for storing a buffer of scores, and
computing basic results like the winner and margin for that scoresheet. They do
not interact with the database and have no concept of team identity---that is
the responsiblity of the debate result classes.

"Position", "side" and "team" take the same meanings as in result.py. However,
since the scoresheet classes don't know about team identities, the word "team"
should not appear in any of them.
"""


def get_scoresheet_class(tournament):
    """Returns the correct scoresheet class for the given tournament's options."""
    teams_in_debate = tournament.pref('teams_in_debate')
    if teams_in_debate == 'two':
        return HighPointWinsRequiredScoresheet
    elif teams_in_debate == 'bp':
        return BPScoresheet
    else:
        raise ValueError("Unrecognised teams_in_debate option: {}".format(teams_in_debate))


class BaseScoresheet:

    def __init__(self, *args, **kwargs):
        """Absorb leftover arguments."""
        pass

    def is_complete(self):
        """Base implementation. Does nothing."""
        return True

    def is_valid(self):
        return self.is_complete()

    def identical(self, other):
        """Base implementation. Does nothing."""
        return True


class ScoresMixin:
    """Provides functionality for speaker scores.
    Does not do any result calculation, since different scoresheets do this in
    different ways. This class is agnostic to  how many sides there are in a
    debate."""

    def __init__(self, positions, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.positions = positions
        self.scores = {side: dict.fromkeys(self.positions, None) for side in self.sides}

    def is_complete(self):
        scores_complete = all(self.scores[s][p] is not None for s in self.sides
                for p in self.positions)
        return super().is_complete() and scores_complete

    def set_score(self, side, position, score):
        self.scores[side][position] = score

    def get_score(self, side, position):
        return self.scores[side][position]

    def get_total(self, side):
        scores = [self.scores[side][p] for p in self.positions]
        if None in scores:
            return None
        return sum(scores)

    def identical(self, other):
        return super().identical(other) and self.scores == other.scores


class DeclaredWinnerMixin:
    """Provides functionality for explicit declaration of winner.  Only makes
    sense for two-team scoresheets."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.declared_winner = None

    def is_complete(self):
        return super().is_complete() and (self.declared_winner in self.sides)

    def set_declared_winner(self, winner):
        assert winner in self.sides or winner is None, "Declared winner must be one of " + ", ".join(map(repr, self.sides))
        self.declared_winner = winner

    def get_declared_winner(self):
        return self.declared_winner

    def identical(self, other):
        return super().identical(other) and self.declared_winner == other.declared_winner


class BaseTwoTeamScoresheet(BaseScoresheet):

    sides = ['aff', 'neg']

    def winner(self):
        """Returns 'aff' is the affirmative team won, and 'neg' if the negative
        team won. `self._get_winner()` must be implemented by subclasses."""
        if not self.is_complete():
            return None
        return self._get_winner()

    def is_valid(self):
        return super().is_valid() and self.winner() is not None


class ResultOnlyScoresheet(DeclaredWinnerMixin, BaseTwoTeamScoresheet):
    """Winner only, no scores. In this case the scoresheet is basically just
    a shell for a single piece of data (the winner)."""

    def _get_winner(self):
        return self.declared_winner


class HighPointWinsRequiredScoresheet(ScoresMixin, BaseTwoTeamScoresheet):
    """Draws are not permitted; winning teams must have a higher total.
    This is the standard type of scoresheet in Asia and Oceania."""

    def _get_winner(self):
        aff_total = self.get_total('aff')
        neg_total = self.get_total('neg')
        if aff_total > neg_total:
            return 'aff'
        elif neg_total > aff_total:
            return 'neg'
        else:
            return None


class TiedPointWinsAllowedScoresheet(DeclaredWinnerMixin, ScoresMixin, BaseTwoTeamScoresheet):
    """In this type of scoresheet, teams can win even when their total speaker
    score is equal to the other team. Because this is possible, scoresheets
    must declare a winner. If the declared winner and calculated winner differ
    (e.g. aff has higher score but neg declared), the winner is None."""

    def _get_winner(self):
        aff_total = self.get_total('aff')
        neg_total = self.get_total('neg')
        if aff_total >= neg_total and self.declared_winner == 'aff':
            return 'aff'
        elif neg_total >= aff_total and self.declared_winner == 'neg':
            return 'neg'
        else:
            return None


class LowPointWinsAllowedScoresheet(ScoresMixin, ResultOnlyScoresheet):
    """This is basically a declared winner scoresheet, with scores that don't
    matter as far as the result is concerned."""
    pass


class BPScoresheet(ScoresMixin, BaseScoresheet):

    sides = ['og', 'oo', 'cg', 'co']

    def is_valid(self):
        if not super().is_valid():
            return False
        totals = [self.get_total(side) for side in self.sides]
        return len(set(totals)) == len(totals)

    def rank(self, side):
        if not self.is_valid():
            return None
        totals = [self.get_total(side) for side in self.sides]
        totals.sort(reverse=True)
        side_total = self.get_total(side)
        return totals.index(side_total) + 1

    def ranked_sides(self):
        if not self.is_valid():
            return None
        total_by_side = [(self.get_total(side), side) for side in self.sides]
        total_by_side.sort(reverse=True)
        return [side for total, side in total_by_side]
