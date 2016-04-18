"""Standings generator for teams.

The main engine for generating team standings."""

from collections import OrderedDict
from operator import itemgetter
from participants.models import Team
from .base import BaseStandingsGenerator
from .metrics import MetricAnnotator
from .ranking import RankAnnotator
import random
import logging
logger = logging.getLogger(__name__)

class StandingsError(RuntimeError):
    pass


class TeamStandingsGenerator(BaseStandingsGenerator):
    """Class for generating standings. An instance is configured with metrics
    and rankings in the constructor, and an iterable of Team objects is passed
    to its `generate()` method to generate standings. Example:

        generator = TeamStandingsGenerator(('points', 'speaker_score'), ('rank',))
        standings = generator.generate(teams)

    The generate() method returns a TeamStandings object.
    """

    TIEBREAK_FUNCTIONS = BaseStandingsGenerator.TIEBREAK_FUNCTIONS.copy()
    TIEBREAK_FUNCTIONS["shortname"] = lambda x: x.sort(key=lambda y: y.team.short_name)
    TIEBREAK_FUNCTIONS["institution"] = lambda x: x.sort(key=lambda y: y.team.institution.name)

    def _interpret_metrics(self, metrics):
        """Overrides the BaseStandingsGenerator implementation to construct
        who-beat-whom with appropriate information.

        Given a list of metrics, sets:
            - `self.precedence` to a copy of `metrics` with who-beat-whoms numbered
            - `self.metric_annotators` to the appropriate metric annotators
        For example:
            ('points', 'wbw', 'speaks', 'wbw', 'margins')
        sets:
        ```
            self.precedence = ['points', 'wbw1', 'speaks', 'wbw2', 'margins']
            self.metric_annotators = [PointsMetricAnnotator(), WhoBeatWhomMetricAnnotator(1, ('points',)) ...]
        ```
        """
        self.precedence = list()
        self.metric_annotators = list()
        index = 1

        for i, metric in enumerate(metrics):
            if metric == "wbw":
                wbw_keys = tuple(m for m in self.precedence[0:i] if m != "wbw")
                args = (index, wbw_keys)
                index += 1
            else:
                args = ()

            annotator = MetricAnnotator(metric, *args)
            self.metric_annotators.append(annotator)
            self.precedence.append(annotator.key)


