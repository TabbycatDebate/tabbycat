"""Scoresheet classes.

The scoresheet classes are responsible for storing a buffer of scores, and
computing basic results like the winners and margin for that scoresheet. They do
not interact with the database and have no concept of team identity---that is
the responsiblity of the debate result classes.

"Position", "side" and "team" take the same meanings as in result.py. However,
since the scoresheet classes don't know about team identities, the word "team"
should not appear in any of them.
"""


class BaseScoresheet:

    uses_declared_winners = False
    uses_scores = False

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

    def winners(self):
        """Returns {'aff'} is the affirmative team won, and {'neg'} if the negative
        team won. `self._get_winners()` must be implemented by subclasses."""
        if not self.is_complete():
            return set()
        return self._get_winners()


class ScoresMixin:
    """Provides functionality for speaker scores.
    Does not do any result calculation, since different scoresheets do this in
    different ways. This class is agnostic to  how many sides there are in a
    debate."""

    uses_scores = True

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


class DeclaredWinnersMixin:
    """Provides functionality for explicit declaration of winner(s)."""

    uses_declared_winners = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.declared_winners = set()

    def is_complete(self):
        return super().is_complete() and self.declared_winners <= set(self.sides) and len(self.declared_winners) == self.number_winners

    def add_declared_winner(self, winner):
        assert winner in self.sides or winner is None, "Declared winner must be one of: " + ", ".join(map(repr, self.sides))
        self.declared_winners.add(winner)

    def set_declared_winners(self, winners):
        winners = set(winners)
        assert winners <= set(self.sides) or len(winners) == 0, "Declared winners must be in: " + ", ".join(map(repr, self.sides))
        self.declared_winners = winners

    def identical(self, other):
        return super().identical(other) and set(self.declared_winners) == set(other.declared_winners)

    def _get_winners(self):
        assert len(self.declared_winners) == self.number_winners, "There can only be this number of winners: %d" % self.number_winners
        return self.declared_winners


class BaseTwoTeamScoresheet(BaseScoresheet):

    sides = ['aff', 'neg']
    number_winners = 1

    def is_valid(self):
        return super().is_valid() and len(self.winners()) == 1

    def rank(self, side):
        rank = 1 if side in self.winners() else 2
        return rank


class ResultOnlyScoresheet(DeclaredWinnersMixin, BaseTwoTeamScoresheet):
    """Winners only, no scores. In this case the scoresheet is basically just
    a shell for a single piece of data (the winners)."""
    pass


class HighPointWinsRequiredScoresheet(ScoresMixin, BaseTwoTeamScoresheet):
    """Draws are not permitted; winning teams must have a higher total.
    This is the standard type of scoresheet in Asia and Oceania."""

    def _get_winners(self):
        aff_total = self.get_total('aff')
        neg_total = self.get_total('neg')
        if aff_total > neg_total:
            return {'aff'}
        elif neg_total > aff_total:
            return {'neg'}
        else:
            return set()


class TiedPointWinsAllowedScoresheet(DeclaredWinnersMixin, ScoresMixin, BaseTwoTeamScoresheet):
    """In this type of scoresheet, teams can win even when their total speaker
    score is equal to the other team. Because this is possible, scoresheets
    must declare a winners. If the declared winners and calculated winners differ
    (e.g. aff has higher score but neg declared), the winners is None."""

    def _get_winners(self):
        aff_total = self.get_total('aff')
        neg_total = self.get_total('neg')
        if aff_total >= neg_total and 'aff' in self.declared_winners:
            return {'aff'}
        elif neg_total >= aff_total and 'neg' in self.declared_winners:
            return {'neg'}
        else:
            return set()


class LowPointWinsAllowedScoresheet(ScoresMixin, ResultOnlyScoresheet):
    """This is basically a declared winners scoresheet, with scores that don't
    matter as far as the result is concerned."""
    pass


class BaseBPScoresheet(BaseScoresheet):
    """This is a stub scoresheet for BP with only its sides as the scoresheet
    class changes by stage."""

    sides = ['og', 'oo', 'cg', 'co']


class BPScoresheet(ScoresMixin, BaseBPScoresheet):

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

    def winners(self):
        return set()


class BPEliminationScoresheet(DeclaredWinnersMixin, BaseBPScoresheet):

    def __init__(self, *args, **kwargs):
        """Initializer for BP elimination scoresheets.
        Create 'num_winners' argument as final rounds have 1 winner and
        not two as with other rounds of the stage."""
        super().__init__(*args, **kwargs)
        self.number_winners = kwargs.get('num_winners') or 2
