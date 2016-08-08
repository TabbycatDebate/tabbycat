"""Base classes for rank annotators for the standings generator.

Each rank annotator is responsible for computing a particular type of ranking
for each team and annotating team standings with them. The most obvious example
is the basic ranking from first to last (taking into account equal rankings),
but there are other "types" of ranks, for example, ranks within brackets
("subranks") or divisions ("division ranks").
"""

import logging
from itertools import groupby

from .metrics import metricgetter

logger = logging.getLogger(__name__)


class BaseRankAnnotator:
    """Base class for all rank annotators.

    A rank annotator is a class that adds rankings to a TeamStandings object.
    Subclasses must implement the method `annotate()`.

    Subclasses must also set the `key`, `name` and `abbr` attributes, either as
    class attributes or object attributes. The `glyphicon` attribute is
    optional.

     - `name` is a name for display in the user interface
     - `abbr` is used instead of `name` when there is not enough space for `name`
     - `glyphicon`, optional, is the name of a glyphicon to be used if possible

    The default constructor does nothing, but subclasses may have constructors
    that initialise themselves with parameters."""

    key = None  # Must be set by subclasses
    name = None  # Must be set by subclasses
    abbr = None  # Must be set by subclasses
    glyphicon = None

    def run(self, standings):
        standings.record_added_ranking(self.key, self.name, self.abbr, self.glyphicon)
        self.annotate(standings.rank_eligible)

    def annotate(self, standings):
        """Annotates the given `standings` by calling `add_ranking()` on every
        `TeamStandingInfo` object in `standings`.

        `standings` is a `TeamStandings` object.
        """
        raise NotImplementedError("BaseRankAnnotator subclasses must implement annotate()")


class BasicRankAnnotator(BaseRankAnnotator):

    key = "rank"
    name = "rank"
    abbr = "Rk"
    glyphicon = "signal"

    def __init__(self, metrics):
        self.rank_key = metricgetter(*metrics)

    def annotate(self, standings):
        rank = 1
        for key, group in groupby(standings, key=self.rank_key):
            group = list(group)
            for info in group:
                info.add_ranking("rank", (rank, len(group) > 1))
            rank += len(group)


class BaseRankWithinGroupAnnotator(BaseRankAnnotator):
    """Base class for ranking annotators that rank within groups."""

    def annotate(self, standings):
        filtered = [tsi for tsi in standings if self.group_key(tsi) is not None]
        by_group = sorted(filtered, key=self.group_key)
        for key, group in groupby(by_group, key=self.group_key):
            rank_in_group = 1
            for _, subgroup in groupby(group, self.rank_key):
                subgroup = list(subgroup)
                for tsi in subgroup:
                    tsi.add_ranking(self.key, (rank_in_group, len(subgroup) > 1))
                rank_in_group += len(subgroup)


class SubrankAnnotator(BaseRankWithinGroupAnnotator):

    key = "subrank"
    name = "subrank"
    abbr = "SubR"

    def __init__(self, metrics):
        self.group_key = metricgetter(metrics[0])
        self.rank_key = metricgetter(*metrics[1:])


class DivisionRankAnnotator(BaseRankWithinGroupAnnotator):

    key = "division_rank"
    name = "division rank"
    abbr = "DivR"

    def __init__(self, metrics):
        self.group_key = lambda x: x.team.division_id
        self.rank_key = metricgetter(*metrics)


class RankFromInstitutionAnnotator(BaseRankWithinGroupAnnotator):

    key = "institution"
    name = "rank from institution"
    abbr = "InstR"

    def __init__(self, metrics):
        self.group_key = lambda x: x.team.institution_id
        self.rank_key = metricgetter(*metrics)
