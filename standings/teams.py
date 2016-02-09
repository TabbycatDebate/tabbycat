"""Standings generator for teams.

The main engine for generating team standings."""

from collections import OrderedDict
from operator import itemgetter
from participants.models import Team
from .metrics import MetricAnnotator
from .ranking import RankAnnotator
import random
import logging
logger = logging.getLogger(__name__)

TEAM_STANDING_METRICS_PRESETS = {
    "australs": ('wins', 'speaks_sum'),
    "nz"      : ('wins', 'wbw', 'speaks_sum', 'wbw', 'draw_strength', 'wbw'),
    "wadl"    : ('points', 'wbw', 'margin_avg', 'speaks_avg'),
    "test"    : ('wins', 'wbw', 'draw_strength', 'wbw', 'speaks_sum', 'wbw', 'margin_sum', 'wbw'),
}

class StandingsError(RuntimeError):
    pass

class TeamStandingInfo:
    """Stores standing information for a team.

    This class is designed to be accessed directly by Django templates. Its
    `metrics` and `rankings` attributes support item lookup, so may be accessed
    like this:

                  Django template               Python code
        Points:   {{ tsi.metrics.points }}      tsi.metrics["points"]
        Rank:     {{ tsi.rankings.rank }}       tsi.rankings["rank"]

    The `itermetrics()` and `iterrankings()` methods return iterators over the
    values of `metrics` and `rankings` respectively, in the order specified by
    `standings.metric_keys`. For example:

    Django template:

        {# Assuming the header row was rendered as in TeamStandings: #}
        {% for tsi in standings.standings %}
          <tr>
            {% for metric in tsi.itermetrics %}
              <td>{{ metric }}</td>
            {% endfor %}
          </tr>
        {% endfor %}

    Python code:

        for tsi in standings.standings:
            for metric, value in zip(standings.metric_info, tsi.itermetrics()):
                print("{0}: {1}".format(metric["name"], value))

    Note that no order is guaranteed when iterating over `metrics.values()` or
    `rankings.values()`. Use `itermetrics()` and `iterrankings()` instead.
    """

    def __init__(self, standings, team):
        self.standings = standings

        if isinstance(team, int):
            self.team_id = team
            self._team = None
        elif hasattr(team, 'id'):
            self.team_id = team.id
            self._team = team
        else:
            raise TypeError("'team' should be a object with 'id' attribute or an integer")

        self.metrics = dict()
        self.rankings = dict()

        class TeamStandingInfoMetricLists:
            """Supports item lookup only. Finds all metrics that start with the
            requested metric name and have a numeric suffix, and returns a list
            of them, sorted by the numeric suffix. For example, if a
            `TeamStandingInfo` object `tsi` has metrics `wbw1`, `wbw3`, `wbw4`,
            then `tsi.metric_lists["wbw"]` returns `[tsi.metrics["wbw1"],
            tsi.metrics["wbw3"], tsi.metrics["wbw4"]]`."""
            def __getitem__(this, key):
                metrics = [k for k in self.metrics.keys() if k.startswith(key) and k[len(key):].isdigit()]
                metrics.sort()
                return [self.metrics[m] for m in metrics]
        self.metric_lists = TeamStandingInfoMetricLists()

    @property
    def team(self):
        if not self._team:
            self._team = Team.objects.get(id=self.team_id)
        return self._team

    def add_metric(self, name, value):
        if name in self.metrics:
            raise ValueError("There is already a metric {!r} for this team".format(name))
        self.metrics[name] = value

    def add_ranking(self, name, value):
        if name in self.rankings:
            raise ValueError("There is already a ranking {!r} for this team".format(name))
        self.rankings[name] = value

    def itermetrics(self):
        for key in self.standings.metric_keys:
            yield self.metrics[key]

    def iterrankings(self):
        for key in self.standings.ranking_keys:
            yield self.rankings[key]

class TeamStandings:
    """Presents all information about the team standings requested. Returned
    by `TeamStandingsGenerator`.

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

    The `standings` property returns a list of `TeamStandingInfo` objects. For
    information on how to iterate over them, see the docstring for
    `TeamStandingInfo`.
    """

    _SPEC_FIELDS = ("key", "name", "abbr", "glyphicon")

    def __init__(self, teams):
        self.infos = {team: TeamStandingInfo(self, team) for team in teams}
        self.ranked = False

        self.metric_keys = list()
        self.ranking_keys = list()
        self._metric_specs = list()
        self._ranking_specs = list()

    @property
    def standings(self):
        assert self.ranked, "sort() must be called before accessing standings"
        return self._standings

    def __len__(self):
        return len(self.standings)

    def __iter__(self):
        """Returns an iterator that iterates over constituent TeamStandingInfo
        objects in ranked order. Raises AttributeError if rankings have not yet
        been generated."""
        return iter(self.standings)

    def infoview(self):
        return self.infos.values()

    def metrics_info(self):
        for spec in self._metric_specs:
            yield dict(zip(self._SPEC_FIELDS, spec))

    def rankings_info(self):
        for spec in self._ranking_specs:
            yield dict(zip(self._SPEC_FIELDS, spec))

    def get_team_list(self):
        return [s.team for s in self.standings]

    def get_team_standing(self, team):
        try:
            return self.infos[team]
        except KeyError:
            raise ValueError("The team {!r} isn't in these standings.")

    def record_added_metric(self, key, name, abbr, glyphicon):
        self.metric_keys.append(key)
        self._metric_specs.append((key, name, abbr, glyphicon))

    def record_added_ranking(self, key, name, abbr, glyphicon):
        self.ranking_keys.append(key)
        self._ranking_specs.append((key, name, abbr, glyphicon))

    def add_metric_to_team(self, team, key, value):
        assert not self.ranked, "Can't add metrics once TeamStandings object is sorted"
        self.get_team_standing(team).add_metric(key, value)

    def sort(self, precedence, tiebreak_func=None):
        self._standings = list(self.infos.values())
        if tiebreak_func:
            tiebreak_func(self._standings)
        self._standings.sort(key=lambda x: itemgetter(*precedence)(x.metrics), reverse=True)
        self.ranked = True


class TeamStandingsGenerator:
    """Class for generating standings. An instance is configured with metrics
    and rankings in the constructor, and an iterable of Team objects is passed
    to its `generate()` method to generate standings. Example:

        generator = TeamStandingsGenerator(('points', 'speaker_score'), ('rank',))
        standings = generator.generate(teams)

    The generate() method returns a TeamStandings object.
    """

    DEFAULT_OPTIONS = {
        "tiebreak": "random",
    }

    TIEBREAK_FUNCTIONS = {
        "random"     : random.shuffle,
        "shortname"  : lambda x: x.sort(key=lambda y: y.team.short_name),
        "institution": lambda x: x.sort(key=lambda y: y.team.institution.name)
    }

    def __init__(self, metrics, rankings, **options):

        # Set up options dictionary
        self.options = self.DEFAULT_OPTIONS.copy()
        for key in options:
            if key not in self.options:
                raise ValueError("Unrecognized option: {0}".format(key))
        self.options.update(options)

        # Set up annotators
        self._interpret_metrics(metrics)
        self._interpret_rankings(rankings)
        self._check_annotators(self.metric_annotators, "metric")
        self._check_annotators(self.ranking_annotators, "ranking")

    def generate(self, queryset, round=None):
        """Generates standings for the teams in queryset. Returns a
        TeamStandings object.

        `queryset` can be a QuerySet or Manager object, and should return just
            those teams of interest for these standings.
        `round`, if specified, is the round for which to generate the standings.
            (That is, rounds after `round` are excluded from the standings.)
        """

        standings = TeamStandings(queryset)

        for annotator in self.metric_annotators:
            annotator.annotate(queryset, standings, round)

        standings.sort(self.precedence, self._tiebreak_func)

        for annotator in self.ranking_annotators:
            annotator.annotate(standings)

        return standings

    def _interpret_metrics(self, metrics):
        """Given a list of metrics, sets:
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
                self.precedence.append(metric)
                args = ()

            annotator = MetricAnnotator(metric, *args)
            self.metric_annotators.append(annotator)
            self.precedence.append(annotator.key)

    def _check_annotators(self, annotators, type_str):
        """Checks the given list of annotators to ensure there are no conflicts.
        A conflict occurs if two annotators would add annotations of the same
        name."""
        names = list()
        for annotator in annotators:
            names.append(annotator.key)
        if len(names) != len(set(names)):
            raise StandingsError("The same {} would be added twice:\n{!r}".format(type_str, names))

    def _interpret_rankings(self, rankings):
        """Given a list of rankings, sets `self.ranking_annotators` to the
        appropriate ranking annotators."""
        self.ranking_annotators = list()

        for ranking in rankings:
            self.ranking_annotators.append(RankAnnotator(ranking, self.precedence))


    @property
    def _tiebreak_func(self):
        return self.TIEBREAK_FUNCTIONS[self.options["tiebreak"]]
