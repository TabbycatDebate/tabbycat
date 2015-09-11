"""Rank annotators for the standings generator.

Each rank annotator is responsible for computing a particular type of ranking
for each team and annotating team standings with them. The most obvious example
is the basic ranking from first to last (taking into account equal rankings),
but there are other "types" of ranks, for example, ranks within brackets
("subranks") or divisions ("division ranks").
"""

from .metrics import metricgetter
from itertools import groupby
from operator import attrgetter
import logging
logger = logging.getLogger(__name__)

registry = {
    "basic"    : BasicRankAnnotator,
    "subrank"  : SubrankAnnotator,
    "division" : DivisionRankAnnotator,
}

def RankAnnotator(name, *args, **kwargs):
    """Factory function. Returns an instance of an appropriate subclass of
    BaseRankAnnotator, with the given arguments passed to the constructor."""
    klass = registry[name]
    return klass(*args, **kwargs)


class BaseRankAnnotator:
    """Base class for all rank annotators.

    A rank annotator is a class that adds rankings to a TeamStandings object.
    It has one method that subclasses must implement: `annotate()`.

    The default constructor does nothing, but subclasses may have constructors
    that initialise themselves with parameters."""

    adds = NotImplemented

    def annotate(self, standings):
        """Annotates the given `standings` by calling `add_ranking()` on every
        `TeamStandingInfo` object in `standings`.

        `standings` is a `TeamStandings` object.
        """
        raise NotImplementedError("BaseMetricAnnotator subclasses must implement annotate()")


class BasicRankAnnotator(BaseRankAnnotator):

    adds = ["rank", "rank_eq"]

    def __init__(self, metrics):
        self.key = metricgetter(*metrics)

    def annotate(self, standings):
        rank = 1
        for key, group in groupby(standings, key=self.key):
            group = list(group)
            for tsi in group:
                tsi.add_ranking("rank", rank)
                tsi.add_ranking("rank_eq", len(group) > 1)
            rank += len(group)


class SubrankAnnotator(BaseRankAnnotator):

    adds = ["subrank", "subrank_eq"]

    def __init__(self, rank_metrics, subrank_metrics):
        self.group_key = metricgetter(*rank_metrics)
        self.subrank_key = metricgetter(*subrank_metrics)

    def annotate(self, standings):
        for key, group in groupby(standings, key=self.group_key):
            subrank = 1
            for subkey, subgroup in groupby(group, self.subrank_key):
                subgroup = list(subgroup)
                for tsi in subgroup:
                    tsi.add_ranking("subrank", subrank)
                    tsi.add_ranking("subrank_eq", len(subgroup) > 1)
                subrank += len(subgroup)


class DivisionRankAnnotator(BaseRankAnnotator):

    adds = ["division_rank", "division_rank_eq"]

    def __init__(self, metrics):
        self.key = metricgetter(*metrics)

    def annotate(self, standings):
        by_division = sorted(standings, key=attrgetter('division'))
        for division, division_teams in groupby(by_division, key=attrgetter('division')):
            rank = 1
            for key, group in groupby(division_teams, self.key):
                group = list(group)
                for tsi in group:
                    tsi.add_ranking("division_rank", rank)
                    tsi.add_ranking("division_rank_eq", len(group) > 1)
                rank += len(group)
