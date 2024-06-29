"""Scoresheet classes.

The scoresheet classes are responsible for storing a buffer of scores, and
computing basic results like the winners and margin for that scoresheet. They do
not interact with the database and have no concept of team identity---that is
the responsiblity of the debate result classes.

"Position", "side" and "team" take the same meanings as in result.py. However,
since the scoresheet classes don't know about team identities, the word "team"
should not appear in any of them.
"""

from draw.types import DebateSide


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
        """Returns {DebateSide.AFF} is the affirmative team won, and {DebateSide.NEG} if the negative
        team won. `self._get_winners()` must be implemented by subclasses."""
        if not self.is_complete():
            return set()
        return self._get_winners()

    def add_declared_winner(self, winner):
        pass

    def set_declared_winners(self, winners):
        pass


class ScoresMixin:
    """Provides functionality for speaker scores.
    Does not do any result calculation, since different scoresheets do this in
    different ways. This class is agnostic to  how many sides there are in a
    debate."""

    uses_scores = True

    def __init__(self, positions, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.positions = positions
        self.criteria = kwargs.get('criteria', [])
        self.scores = {side: dict.fromkeys(self.positions, None) for side in self.sides}
        self.speaker_ranks = {side: dict.fromkeys(self.positions, None) for side in self.sides}
        self.criteria_scores = {side: {pos: dict.fromkeys(self.criteria, 0) for pos in self.positions} for side in self.sides}

    def is_complete(self):
        if len(self.criteria) == 0:
            scores_complete = all(self.scores[s][p] is not None for s in self.sides
                    for p in self.positions)
        else:
            scores_complete = True
        return super().is_complete() and scores_complete

    def set_score(self, side, position, score):
        if len(self.criteria) == 0:
            self.scores[side][position] = score

    def get_score(self, side: str, position: int):
        if len(self.criteria) > 0:
            return sum(score * type(score)(criterion.weight) for criterion, score in self.criteria_scores[side][position].items())
        return self.scores[side][position]

    def set_speaker_rank(self, side, position, score):
        self.speaker_ranks[side][position] = score

    def get_speaker_rank(self, side: str, position: int) -> int:
        return self.speaker_ranks[side][position]

    def set_criterion_score(self, side: str, position: int, criterion, score):
        self.criteria_scores[side][position][criterion] = score

    def get_criterion_score(self, side: str, position: int, criterion):
        return self.criteria_scores[side][position][criterion]

    def get_total(self, side):
        scores = [self.get_score(side, p) for p in self.positions]
        if None in scores:
            return None
        return sum(scores)

    def identical(self, other):
        return super().identical(other) and self.scores == other.scores and self.speaker_ranks == other.speaker_ranks


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

    sides = [DebateSide.AFF, DebateSide.NEG]
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
        aff_total = self.get_total(DebateSide.AFF)
        neg_total = self.get_total(DebateSide.NEG)
        if aff_total > neg_total:
            return {DebateSide.AFF}
        elif neg_total > aff_total:
            return {DebateSide.NEG}
        else:
            return set()


class TiedPointWinsAllowedScoresheet(DeclaredWinnersMixin, ScoresMixin, BaseTwoTeamScoresheet):
    """In this type of scoresheet, teams can win even when their total speaker
    score is equal to the other team. Because this is possible, scoresheets
    must declare a winners. If the declared winners and calculated winners differ
    (e.g. aff has higher score but neg declared), the winners is None."""

    def _get_winners(self):
        aff_total = self.get_total(DebateSide.AFF)
        neg_total = self.get_total(DebateSide.NEG)
        if aff_total >= neg_total and DebateSide.AFF in self.declared_winners:
            return {DebateSide.AFF}
        elif neg_total >= aff_total and DebateSide.NEG in self.declared_winners:
            return {DebateSide.NEG}
        else:
            return set()


class LowPointWinsAllowedScoresheet(ScoresMixin, ResultOnlyScoresheet):
    """This is basically a declared winners scoresheet, with scores that don't
    matter as far as the result is concerned."""
    pass


class BasePolyScoresheet(BaseScoresheet):
    """This is a stub scoresheet for >2-team formats with only its sides as the scoresheet
    class changes by stage."""

    def __init__(self, sides, *args, **kwargs):
        self.sides = sides
        super().__init__(*args, **kwargs)


class PolyScoresheet(ScoresMixin, BasePolyScoresheet):

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
            return []
        total_by_side = [(self.get_total(side), side) for side in self.sides]
        total_by_side.sort(reverse=True)
        return [side for total, side in total_by_side]

    def winners(self):
        return set()


class PolyNoWinScoresheet(ScoresMixin, BasePolyScoresheet):

    def is_valid(self):
        return super().is_valid()

    def rank(self, side):
        return None

    def ranked_sides(self):
        return []

    def winners(self):
        return set()


class PolyEliminationScoresheet(DeclaredWinnersMixin, BasePolyScoresheet):

    def __init__(self, *args, **kwargs):
        """Initializer for BP elimination scoresheets.
        Create 'num_winners' argument as final rounds have 1 winner and
        not two as with other rounds of the stage."""
        super().__init__(*args, **kwargs)
        self.number_winners = kwargs.get('num_winners') or 2
