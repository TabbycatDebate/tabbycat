"""Base classes for metric annotators for the standings generator.

Each metric annotator is responsible for computing a particular metric for each
item and annotating the standings with them, for example, in the case of teams,
number of wins (points), or draw strength. Subclasses should be defined in
context-specific files, e.g., teams.py or speakers.py.
"""

from operator import itemgetter

from django.db.models.expressions import RawSQL

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

    A metric annotator is a class that adds a metric to a Standings object.
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
        `StandingInfo` object in `standings`.

        `queryset` is the queryset on which the standings are produced.
        `standings` is a `Standings` object.
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


class QuerySetMetricAnnotator(BaseMetricAnnotator):
    """Base class for annotators that metrics based on conditional aggregations."""

    @staticmethod
    def get_annotation_metric_query_str():
        raise NotImplementedError("Subclasses of QuerySetMetricAnnotator must implement get_annotation_metric_query_str().")

    def get_annotation_metric_query_args(self):
        raise NotImplementedError("Subclasses of QuerySetMetricAnnotator must implement get_annotation_metric_query_args().")

    @classmethod
    def get_annotated_queryset(cls, queryset, column_name, *args, **kwargs):
        """Returns a QuerySet annotated with the metric given. All positional
        arguments from the third onwards, and all keyword arguments, are passed
        to get_annotation_metric_query_str()."""
        query = cls.get_annotation_metric_query_str(*args, **kwargs)
        logger.info("Running query in {}: {}".format(cls.__name__, query))
        sql = RawSQL(query, ())
        return queryset.annotate(**{column_name: sql}).distinct()

    def annotate_with_queryset(self, queryset, standings, round=None):
        """Annotates items with the given QuerySet, using the "metric" field."""
        for item in queryset:
            if item.metric is None:
                logger.warning("Metric {metric!r} for {item} was None, setting to 0".format(
                        metric=self.key, item=item))
                item.metric = 0
            standings.add_metric(item, self.key, item.metric)

    def annotate(self, queryset, standings, round=None):
        args = self.get_annotation_metric_query_args(round)
        queryset = self.get_annotated_queryset(queryset, "metric", *args)
        self.annotate_with_queryset(queryset, standings, round)
