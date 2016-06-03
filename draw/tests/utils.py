"""Utilities for draw tests."""


class TestTeam(object):
    """Basic implementation of team interface"""

    def __init__(self, id, inst, points=None, hist=list(), **kwargs):
        self.id = id
        self.institution = inst
        self.points = points
        try:
            self.hist = list(hist)
        except TypeError:
            self.hist = (hist,)
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return "<Team {0} of {1} ({2:#x})>".format(self.id, self.institution, hash(self))

    def break_rank_for_category(self, category):
        return self.points

    def seen(self, other):
        return self.hist.count(other.id)


class TestRound(object):
    """Basic implementation of round interface for break rounds + round robins"""

    def __init__(self, break_size):
        self.break_size = break_size

    def break_size(self):
        return self.break_size

    def break_category(self):
        return "NA"
