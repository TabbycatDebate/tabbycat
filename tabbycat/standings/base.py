"""Base class for standings generators."""

from operator import itemgetter
import random
import logging

from .metrics import RepeatedMetricAnnotator

logger = logging.getLogger(__name__)


class StandingsError(RuntimeError):
    pass


class StandingInfo:
    """Stores standing information for an instance of a model.

    This class is designed to be accessed directly by Django templates. Its
    `metrics` and `rankings` attributes support item lookup, so may be accessed
    like this:

                  Django template                Python code
        Points:   {{ info.metrics.points }}      info.metrics["points"]
        Rank:     {{ info.rankings.rank }}       info.rankings["rank"]

    The `itermetrics()` and `iterrankings()` methods return iterators over the
    values of `metrics` and `rankings` respectively, in the order specified by
    `standings.metric_keys`. For example:

    Django template:

        {# Assuming the header row was rendered as in BaseStandings: #}
        {% for info in standings.standings %}
          <tr>
            {% for metric in info.itermetrics %}
              <td>{{ metric }}</td>
            {% endfor %}
          </tr>
        {% endfor %}

    Python code:

        for info in standings.standings:
            for metric, value in zip(standings.metric_info, info.itermetrics()):
                print("{0}: {1}".format(metric["name"], value))

    Note that no order is guaranteed when iterating over `metrics.values()` or
    `rankings.values()`. Use `itermetrics()` and `iterrankings()` instead.

    Note that a ranking is not guaranteed to exist, and won't exist when the
    instance is ineligible for a rank. In this case, `info.rankings[key]` will
    results in a KeyError, and `iterrankings()` will return `(None, False)`.
    Python code should be prepared to handle this scenario. Django templates
    should use {{ ranking|default:"n/a" }} to handle the `None`.
    """

    def __init__(self, standings, instance):
        self.standings = standings
        self.instance_id = instance.id
        self.instance = instance
        self.model_verbose_name = self.instance.__class__._meta.verbose_name.lower()

        # set more naturally-named attribute for instance, e.g., `self.team` if it is a Team
        setattr(self, self.instance.__class__.__name__.lower(), self.instance)

        self.metrics = dict()
        self.rankings = dict()

    def __repr__(self):
        return "<StandingInfo for {}>".format(str(self.instance))

    def add_metric(self, name, value):
        if name in self.metrics:
            raise ValueError("There is already a metric {!r} for this {}".format(name, self.model_verbose_name))
        self.metrics[name] = value

    def add_ranking(self, name, value):
        if name in self.rankings:
            raise ValueError("There is already a ranking {!r} for this {}".format(name, self.model_verbose_name))
        self.rankings[name] = value

    def itermetrics(self):
        for key in self.standings.metric_keys:
            yield self.metrics[key]

    def iterrankings(self):
        for key in self.standings.ranking_keys:
            try:
                yield self.rankings[key]
            except KeyError:
                yield (None, False)

    def get_ranking(self, key, default=None):
        """Returns the numeric rank (without equality information), or None (or
        the value provided in `default`) if there is no ranking associated with
        this key."""
        try:
            return self.rankings[key][0]
        except KeyError:
            return default


class Standings:
    """Presents all information about the standings requested. Returned
    by `BaseStandingsGenerator`.

    This class is designed to be accessed directly by Django templates. The
    `metrics_info` method returns an iterator yielding dictionaries with keys
    "key", "name", "abbr" and "glyphicon". For example:

    Django template:

        <tr>
          {% for metric in standings.metrics_info %}
            <td>{{ metric.name }}</td>
          {% endfor %}
        </tr>

    Python code:

        for metric in standings.metric_info:
            print("Key is {0}, name is {1}".format(metric["key"], metric["name"]))

    The `rankings_info` attribute behaves similarly.

    The `standings` property returns a list of `BaseStandingInfo` objects. For
    information on how to iterate over them, see the docstring for
    `BaseStandingInfo`.
    """

    _SPEC_FIELDS = ("key", "name", "abbr", "glyphicon")

    def __init__(self, instances, rank_filter=None):
        self.infos = {instance: StandingInfo(self, instance) for instance in instances}
        self.ranked = False
        self.rank_filter = rank_filter
        self._rank_limit = None

        self.metric_keys = list()
        self.ranking_keys = list()
        self._metric_specs = list()
        self._ranking_specs = list()

    @property
    def standings(self):
        assert self.ranked, "sort() must be called before accessing standings"
        return self._standings

    @property
    def rank_eligible(self):
        assert self.ranked, "sort() must be called before accessing standings"
        if self.rank_filter:
            return filter(self.rank_filter, self._standings)
        else:
            return self._standings

    def __len__(self):
        return len(self.standings)

    def __iter__(self):
        """Returns an iterator that iterates over constituent BaseStandingInfo
        objects in ranked order. Raises AttributeError if rankings have not yet
        been generated."""
        if self._rank_limit:
            return self.iteruntil(self._rank_limit)
        else:
            return iter(self.standings)

    def iteruntil(self, rank_limit, key="rank"):
        """Stops iterating when the rank exceeds `rank_limit`. If there isn't a
        "rank" ranking for any particular StandingInfo, it acts as if the rank
        were zero. Therefore, if the standings haven't been annotated with a
        "rank", then this will end up iterating through the entire standings.
        If `key` is specified, it is used instead of "rank"."""
        for info in self.standings:
            if info.get_ranking(key, 0) > rank_limit:
                break
            yield info

    def infoview(self):
        return self.infos.values()

    def metrics_info(self):
        for spec in self._metric_specs:
            yield dict(zip(self._SPEC_FIELDS, spec))

    def rankings_info(self):
        for spec in self._ranking_specs:
            yield dict(zip(self._SPEC_FIELDS, spec))

    def get_instance_list(self):
        return [s.instance for s in self.standings]

    def get_standing(self, instance):
        try:
            return self.infos[instance]
        except KeyError:
            raise ValueError("{!r} isn't in these standings.".format(instance))

    def get_standings(self, instances):
        try:
            return [self.infos[instance] for instance in instances]
        except KeyError as e:
            raise ValueError("{!r} isn't in these standings.".format(e.args[0]))

    def record_added_metric(self, key, name, abbr, glyphicon):
        self.metric_keys.append(key)
        self._metric_specs.append((key, name, abbr, glyphicon))

    def record_added_ranking(self, key, name, abbr, glyphicon):
        self.ranking_keys.append(key)
        self._ranking_specs.append((key, name, abbr, glyphicon))

    def add_metric(self, instance, key, value):
        assert not self.ranked, "Can't add metrics once standings object is sorted"
        self.get_standing(instance).add_metric(key, value)

    def sort(self, precedence, tiebreak_func=None):
        self._standings = list(self.infos.values())

        if tiebreak_func:
            tiebreak_func(self._standings)

        try:
            self._standings.sort(key=lambda x: itemgetter(*precedence)(x.metrics), reverse=True)
        except TypeError:
            for info in self.infos.values():
                logger.info("%30s %s", info.instance, itemgetter(*precedence)(info.metrics))
            raise

        if self.rank_filter:
            self._standings.sort(key=self.rank_filter, reverse=True)

        self.ranked = True

    def filter(self, include_filter):
        self.infos = {instance: info for instance, info in self.infos.items() if include_filter(info)}

    def set_rank_limit(self, rank_limit):
        """Sets the rank limit on these standings. This doesn't affect the data
        held by a Standings instance, but if the rank limit is set, then when
        the standings are iterated over, the iteration stops once the rank limit
        is exceeded. For example, if the rank limit is set to 10, then iterating
        over the standings will only produce the top ten speakers (including
        those tied on 10th)."""
        self._rank_limit = rank_limit


class BaseStandingsGenerator:

    DEFAULT_OPTIONS = {
        "tiebreak": "random",
        "rank_filter": None,
        "include_filter": None,  # not currently used by other code
    }

    TIEBREAK_FUNCTIONS = {
        "random"     : random.shuffle,
    }

    metric_annotator_classes = {}
    ranking_annotator_classes = {}

    def __init__(self, metrics, rankings, extra_metrics=(), **options):

        # Set up options dictionary
        self.options = self.DEFAULT_OPTIONS.copy()
        for key in options:
            if key not in self.options:
                raise ValueError("Unrecognized option: {0}".format(key))
        self.options.update(options)

        # Set up annotators
        self._interpret_metrics(metrics, extra_metrics)
        self._interpret_rankings(rankings)
        self._check_annotators(self.metric_annotators, "metric")
        self._check_annotators(self.ranking_annotators, "ranking")

    def generate(self, queryset, round=None):
        """Generates standings for the objects in queryset. Returns a
        Standings object.

        `queryset` can be a QuerySet or Manager object, and should return just
            those objects of interest for these standings.
        `round`, if specified, is the round for which to generate the standings.
            (That is, rounds after `round` are excluded from the standings.)
        """

        standings = Standings(queryset, rank_filter=self.options["rank_filter"])

        for annotator in self.metric_annotators:
            logger.debug("Running metric annotator: %s", annotator.name)
            annotator.run(queryset, standings, round)
        logger.debug("Metric annotators done.")

        if self.options["include_filter"]:
            standings.filter(self.options["include_filter"])

        standings.sort(self.precedence, self._tiebreak_func)

        for annotator in self.ranking_annotators:
            logger.debug("Running ranking annotator: %s", annotator.name)
            annotator.run(standings)
        logger.debug("Ranking annotators done.")

        return standings

    def _check_annotators(self, annotators, type_str):
        """Checks the given list of annotators to ensure there are no conflicts.
        A conflict occurs if two annotators would add annotations of the same
        name."""
        names = list()
        for annotator in annotators:
            names.append(annotator.key)
        if len(names) != len(set(names)):
            raise StandingsError("The same {} would be added twice:\n{!r}".format(type_str, names))

    def _interpret_metrics(self, metrics, extra_metrics):
        """Given a list of metric keys, sets:
            - `self.precedence` to a copy of `metrics` with repeated metric annotators numbered
            - `self.metric_annotators` to the appropriate metric annotators
        For example:
            ('points', 'wbw', 'speaks', 'wbw', 'margins')
        sets:
        ```
            self.precedence = ['points', 'wbw1', 'speaks', 'wbw2', 'margins']
            self.metric_annotators = [PointsMetricAnnotator(), WhoBeatWhomMetricAnnotator(1, ('points',)) ...]
        ```

        The metrics in `extra_metrics` also have their annotators added to
        `self.metric_annotators`, but their keys are not added to
        `self.precedence`.
        """
        self.precedence = list()
        self.metric_annotators = list()
        repeated_metric_indices = {}

        all_metrics = [(m, True) for m in metrics] + [(m, False) for m in extra_metrics]

        for i, (metric, ranked) in enumerate(all_metrics):
            klass = self.metric_annotator_classes[metric]

            if issubclass(klass, RepeatedMetricAnnotator):
                earlier_keys = tuple(m for m in self.precedence[0:i] if m != metric)
                index = repeated_metric_indices.setdefault(metric, 1)
                args = (index, earlier_keys)
                repeated_metric_indices[metric] += 1
            else:
                args = ()

            annotator = klass(*args)
            self.metric_annotators.append(annotator)

            if ranked:
                self.precedence.append(annotator.key)

    def _interpret_rankings(self, rankings):
        """Given a list of rankings, sets `self.ranking_annotators` to the
        appropriate ranking annotators."""
        self.ranking_annotators = list()

        for ranking in rankings:
            klass = self.ranking_annotator_classes[ranking]
            annotator = klass(self.precedence)
            self.ranking_annotators.append(annotator)

    @property
    def _tiebreak_func(self):
        return self.TIEBREAK_FUNCTIONS[self.options["tiebreak"]]

    @classmethod
    def get_metric_choices(cls, ranked_only=True):
        choices = []
        for key, annotator in cls.metric_annotator_classes.items():
            if not ranked_only and annotator.ranked_only:
                continue
            if hasattr(annotator, 'choice_name'):
                choice_name = annotator.choice_name.capitalize()
            else:
                choice_name = annotator.name.capitalize()
            choices.append((key, choice_name))
        choices.sort(key=lambda x: x[1])
        return choices
