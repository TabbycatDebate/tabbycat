"""Base classes for metric annotators for the standings generator.

Each metric annotator is responsible for computing a particular metric for each
item and annotating the standings with them, for example, in the case of teams,
number of wins (points), or draw strength. Subclasses should be defined in
context-specific files, e.g., teams.py or speakers.py.
"""

import logging

logger = logging.getLogger(__name__)


def metricgetter(items, negate=None):
    """Returns a callable object that fetches each item in `items` from its
    operand's `metrics` attribute, and returns a tuple containing the results.
    The tuple will have the same number for elements as `items`.

    For example:
     - After `f = metricgetter(("a",))`, the call `f(x)` returns `(x.metrics["a"],)`.
     - After `g = metricgetter((4, 9))`, the call `g(x)` returns `(x.metrics[4], x.metrics[9])`.
    """

    if negate is None:

        def metricitemgetter(x):
            return tuple(x.metrics[item] for item in items)

    else:
        assert len(items) == len(negate), "items had %d items but negate had %d" % (len(items), len(negate))
        coeffs = [-1 if neg else 1 for neg in negate]

        def metricitemgetter(x):
            return tuple(coeff * x.metrics[item] for (coeff, item) in zip(coeffs, items))

    return metricitemgetter


class BaseMetricAnnotator:
    """Base class for all metric annotators.

    A metric annotator is a class that adds a metric to a Standings object.
    Subclasses must implement the method `annotate()`. Every annotator
    must add precisely one metric.

    Subclasses must set the `key`, `name` and `abbr` attributes.

    The default constructor does nothing, but subclasses may have constructors
    that initialise themselves with parameters."""

    key = None  # must be set by subclasses
    name = None  # must be set by subclasses
    abbr = None  # must be set by subclasses
    icon = None
    ranked_only = False
    repeatable = False
    listed = True
    ascending = False  # if True, this metric is sorted in ascending order, not descending

    def run(self, queryset, standings, round=None):
        standings.record_added_metric(self.key, self.name, self.abbr, self.icon, self.ascending)
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

    ranked_only = True  # Repeated metrics don't make sense outside the precedence
    repeatable = True

    def __init__(self, index, keys):
        self.index = index
        self.key = self.key_prefix + str(index)
        self.name = self.name_prefix + " " + str(index)
        self.abbr = self.abbr_prefix + str(index)
        self.keys = keys


class QuerySetMetricAnnotator(BaseMetricAnnotator):
    """Base class for annotators that metrics based on conditional aggregations."""

    def get_annotation(self, round):
        raise NotImplementedError("Subclasses of QuerySetMetricAnnotator must implement get_annotation().")

    def get_annotated_queryset(self, queryset, round=None):
        """Returns a QuerySet annotated with the metric given."""
        annotation = self.get_annotation(round=round)
        logger.info("Annotation in %s: %s", self.__class__.__name__, str(annotation))
        self.queryset_annotated = True
        return queryset.annotate(**{self.key: annotation})

    def annotate_with_queryset(self, queryset, standings):
        """Annotates items with the given QuerySet."""
        for item in queryset:
            metric = getattr(item, self.key)
            if metric is None:
                metric = 0
            standings.add_metric(item, self.key, metric)

    def annotate(self, queryset, standings, round=None):
        assert self.queryset_annotated, "get_annotated_queryset() must be run before annotate()"
        self.annotate_with_queryset(queryset, standings)
