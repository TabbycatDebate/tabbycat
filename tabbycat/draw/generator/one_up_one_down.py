class OneUpOneDownSwapper(object):

    DEFAULT_OPTIONS = {
        "exclude_penalty"    : -1e10,
        "avoid_history"      : True,
        "avoid_institution"  : True,
        "history_penalty"    : 1e3,
        "institution_penalty": 1,
    }

    def __init__(self, **kwargs):
        for key, value in self.DEFAULT_OPTIONS.items():
            if key in kwargs and kwargs[key] is not None:
                setattr(self, key, kwargs[key])
            else:
                setattr(self, key, value)

        if not self.avoid_history:
            self.history_penalty = 0
        if not self.avoid_institution:
            self.institution_penalty = 0

        self._score = None
        self._swaps = None

    @staticmethod
    def dp(data):
        """'data' is a list of integers.  Returns a 2-tuple.
        The second item is the indices of the elements in data that have the
        maximum possible sum, subject to the constraint that you can't pick two
        adjacent elements. Note that negative elements will never be included,
        since they always reduce the sum so it is better to exclude them.  (The
        constraint does not say that you must pick every other element.) For
        example, if 'data' is a list of "swap scores", this would return a list
        of indices of the optimal swap combinations. The first item is the
        maximum possible sum so obtained."""

        n = len(data) + 1

        # 'state' is the cumulative sum of the relevant elements.
        # 'action' elements are 1 if this integer should be included, and 0 if
        # not, except that a 1 is nullified if the integer immediately following
        # it is included (i.e. a non-nullified 1).  We keep nullified 1s in the
        # list because they might become non-nullified again if another 1 is
        # added to the end of a number of consecutive 1s.
        state = [0] * (n + 1)
        action = [0] * (n + 1)

        # If we "activate" this element, then we must consequentially exclude the
        # previous element.  Given that, we would improve the cumulative sum if,
        # and only if, adding this element to the cumulative sum as of *two*
        # elements ago (to form the potential cumulative sum of this element)
        # would beat the cumulative sum as of last element.
        for i in range(2, n+1):
            if (state[i-2] + data[i-2]) > state[i-1]:
                action[i] = 1
                state[i] = state[i-2] + data[i-2]
            else:
                action[i] = 0
                state[i] = state[i-1]

        j = n
        k = []
        # while j >= 0:
        #    L.insert(0, j)
        #    j -= (action[j] + 1)
        # return state[n], L

        # Now go back through the list starting at the end (since a 1 nullifies
        # the 1 immediately preceding, assuming the former is not itself
        # nullified).
        while j >= 2:
            if action[j]:
                k.insert(0, j-2)  # Insert index corresponding to start of swap
            j -= (action[j] + 1)
        return state[n], k

    def score_swap(self, debate1, debate2):
        """Returns an integer representing the improvement from swapping the
        teams in these two debates.  The higher the integer, the more you want to
        do the swap."""
        (a1, n1) = debate1
        (a2, n2) = debate2
        inst = (a1.institution == n1.institution and a1.institution is not None,
                a2.institution == n2.institution and a2.institution is not None)
        hist = (a1.seen(n1), a2.seen(n2))

        if not ((inst[0] or inst[1]) and self.avoid_institution) and \
                (sum(hist) == 0 and self.avoid_history):
            return self.exclude_penalty

        inst_swap = (a1.institution == n2.institution,
                     a2.institution == n1.institution)
        hist_swap = (a1.seen(n2), a2.seen(n1))

        # Definitely don't swap if you'd have more history conflicts by swapping
        if self.avoid_history and sum(hist_swap) > sum(hist):
            return self.exclude_penalty

        def badness(i, h):
            return i.count(True) * self.institution_penalty + sum(h) \
                * self.history_penalty

        # Discount by 1e-3 so that, if there are two otherwise-equivalent
        # swap combinations, fewer swaps is preferred to more swaps
        return badness(inst, hist) - badness(inst_swap, hist_swap) - 1e-3

    @staticmethod
    def one_up_down_swap(draw, i):
        m1 = (draw[i][0], draw[i+1][1])
        m2 = (draw[i+1][0], draw[i][1])
        draw[i] = m1
        draw[i+1] = m2

    def run(self, draw):
        """'draw' is a list of 2-tuples of Teams [(aff, neg), (aff, neg)...]
        representing the entire draw"""

        # Find a list of integers representing how much better you get by
        # executing the each team with the team below.
        swap_scores = [(self.score_swap(draw[i], draw[i+1])) for i in range(len(draw) - 1)]

        # Adjust scores so that if there are two equivalent ways to resolve a
        # conflict, swaps higher in the ranking are preferred to those lower.
        for i, score in enumerate(swap_scores):
            if score > 0:
                swap_scores[i] += (len(swap_scores) - i) * 1e-6

        best_score, best_swaps = self.dp(swap_scores)
        for s in best_swaps:
            self.one_up_down_swap(draw, s)

        self._score = best_score
        self._swaps = best_swaps

        return draw

    @property
    def score(self):
        if self._score is None:
            raise AttributeError("run() hasn't been called yet")
        return self._score

    @property
    def swaps(self):
        if self._swaps is None:
            raise AttributeError("run() hasn't been called yet")
        return self._swaps
