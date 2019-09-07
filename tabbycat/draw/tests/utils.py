"""Utilities for draw tests."""


class TestTeam(object):
    """Basic implementation of team interface"""

    def __init__(self, id, inst, points=0, hist=list(), **kwargs):
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

    def seen(self, other):
        return self.hist.count(other.id)
