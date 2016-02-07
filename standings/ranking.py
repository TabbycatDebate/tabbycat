"""Rank annotators for the standings generator.

Each rank annotator is responsible for computing a particular type of ranking
for each team and annotating team standings with them. The most obvious example
is the basic ranking from first to last (taking into account equal rankings),
but there are other "types" of ranks, for example, ranks within brackets
("subranks") or divisions ("division ranks").

Note: There's a registry at the bottom of the file. If you add a new
RankAnnotator subclass, be sure to add it to the registry.
"""

from .metrics import metricgetter
from itertools import groupby
from operator import attrgetter
import logging
logger = logging.getLogger(__name__)

def RankAnnotator(name, *args, **kwargs):
    """Factory function. Returns an instance of an appropriate subclass of
    BaseRankAnnotator, with the given arguments passed to the constructor."""
    klass = registry[name]
    return klass(*args, **kwargs)


class BaseRankAnnotator:
    """Base class for all rank annotators.

    A rank annotator is a class that adds rankings to a TeamStandings object.
    Subclasses must implement the method `annotate_teams()`.

    Subclasses must also set the `key`, `name` and `abbr` attributes, either as
    class attributes or object attributes. The `glyphicon` attribute is
    optional.

     - `name` is a name for display in the user interface
     - `abbr` is used instead of `name` when there is not enough space for `name`
     - `glyphicon`, optional, is the name of a glyphicon to be used if possible

    The default constructor does nothing, but subclasses may have constructors
    that initialise themselves with parameters."""

    key = NotImplemented
    name = NotImplemented
    abbr = NotImplemented
    glyphicon = None

    def annotate(self, standings):
        standings.record_added_ranking(self.key, self.name, self.abbr, self.glyphicon)
        self.annotate_teams(standings)

    def annotate_teams(self, standings):
        """Annotates the given `standings` by calling `add_ranking()` on every
        `TeamStandingInfo` object in `standings`.

        `standings` is a `TeamStandings` object.
        """
        raise NotImplementedError("BaseMetricAnnotator subclasses must implement annotate()")


class BasicRankAnnotator(BaseRankAnnotator):

    key = "rank"
    name = "rank"
    abbr = "Rk"
    glyphicon = "signal"

    def __init__(self, metrics):
        self.rank_key = metricgetter(*metrics)

    def annotate_teams(self, standings):
        rank = 1
        for key, group in groupby(standings, key=self.rank_key):
            group = list(group)
            for tsi in group:
                tsi.add_ranking("rank", (rank, len(group) > 1))
            rank += len(group)


class SubrankAnnotator(BaseRankAnnotator):

    key = "subrank"
    name = "subrank"
    abbr = "SubR"

    def __init__(self, metrics):
        self.group_key = metricgetter(metrics[0])
        self.subrank_key = metricgetter(*metrics[1:])

    def annotate_teams(self, standings):
        for key, group in groupby(standings, key=self.group_key):
            subrank = 1
            for subkey, subgroup in groupby(group, self.subrank_key):
                subgroup = list(subgroup)
                for tsi in subgroup:
                    tsi.add_ranking("subrank", (subrank, len(subgroup) > 1))
                subrank += len(subgroup)


class DivisionRankAnnotator(BaseRankAnnotator):

    key = "division_rank"
    name = "division rank"
    abbr = "DivR"

    def __init__(self, metrics):
        self.rank_key = metricgetter(*metrics)

    def annotate_teams(self, standings):
        division_key = lambda x: x.team.division.name
        by_division = sorted(standings, key=division_key)
        for division, division_teams in groupby(by_division, key=division_key):
            rank = 1
            for key, group in groupby(division_teams, self.rank_key):
                group = list(group)
                for tsi in group:
                    tsi.add_ranking("division_rank", (rank, len(group) > 1))
                rank += len(group)


registry = {
    "rank"     : BasicRankAnnotator,
    "subrank"  : SubrankAnnotator,
    "division" : DivisionRankAnnotator,
}

