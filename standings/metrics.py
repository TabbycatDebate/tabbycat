"""Base classes for metric annotators for the standings generator.

Each metric annotator is responsible for computing a particular metric for each
team and annotating team standings with them, for example, number of wins
(points), or draw strength. Subclasses should be defined in context-specific
files, e.g., teams.py or speakers.py.
"""

from operator import itemgetter

import random
import logging
logger = logging.getLogger(__name__)

def metricgetter(*items):
    """Returns a callable object that fetches `item` from its operand's
    `metrics` attribute. If multiple items are specified, returns a tuple.
    For example:
     - After `f = metricgetter("a")`, the call `f(x)` returns `x.metrics["a"]`.
     - After `g = metricgetter(4, 9)`, the call `g(x)` returns `(x.metrics[4], x.metrics[9])`.
    """
    return lambda x: itemgetter(*items)(x.metrics)


class BaseMetricAnnotator:
    """Base class for all metric annotators.

    A metric annotator is a class that adds a metric to a TeamStandings object.
    Subclasses must implement the method `annotate()`. Every annotator
    must add precisely one metric.

    Subclasses must set the `key`, `name` and `abbr` attributes.

    The default constructor does nothing, but subclasses may have constructors
    that initialise themselves with parameters."""

    key = None # must be set by subclasses
    name = None # must be set by subclasses
    abbr = None # must be set by subclasses
    glyphicon = None

    def run(self, queryset, standings, round=None):
        standings.record_added_metric(self.key, self.name, self.abbr, self.glyphicon)
        self.annotate(queryset, standings, round)

    def annotate(self, queryset, standings, round=None):
        """Annotates the given `standings` by calling `add_metric()` on every
        `TeamStandingInfo` object in `standings`.

        `queryset` is the queryset of teams.
        `standings` is a `TeamStandings` object.
        `round`, if specified, is a `Round` object that is assumed to be in the
            relevant tournament.
        """
        raise NotImplementedError("BaseMetricAnnotator subclasses must implement annotate()")


class RepeatedMetricAnnotator(BaseMetricAnnotator):
    """Base class for metric annotators that can be used multiple times.

    Subclasses should set the `key_prefix`, `name_prefix` and `abbr_prefix`
    class attributes, and use the `key` attribute when adding metrics in
    implementing `annotate()`."""

    def __init__(self, index, keys):
        self.index = index
        self.key = self.key_prefix + str(index)
        self.name = self.name_prefix + " " + str(index)
        self.abbr = self.abbr_prefix + str(index)
        self.keys = keys

