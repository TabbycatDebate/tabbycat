class Allocator(object):
    def __init__(self, debates, adjudicators):
        self.debates = list(debates)
        self.adjudicators = adjudicators

    def allocate(self):
        raise NotImplementedError


