"""Standings generator.

The main engine for generating team standings."""

from collections import OrderedDict
from operator import itemgetter
from participants.models import Team
from .metrics import MetricAnnotator
from .ranking import RankAnnotator
import random

class StandingsError(RuntimeError):
    pass

class TeamStandingInfo:
    """Stores standing information for a team."""

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
            raise KeyError("There is already a metric {!r} for this team", name)
        self.metrics[name] = value

    def add_ranking(self, name, value):
        if name in self.ranking:
            raise KeyError("There is already a ranking {!r} for this team", name)
        self.rankings[name] = value


class TeamStandings:
    """Presents all information about the team standings requested. Returned
    by `TeamStandingsGenerator`."""

    def __init__(self, teams):
        self.infos = {team: TeamStandingInfo(team) for team in teams}
        self.ranked = False

        self.metrics_added = list()
        self.rankings_added = list()
        self.general_added = list()

    @property
    def standings(self):
        assert self.ranked, "sort() must be called before accessing standings"
        return self._standings

    def __iter__(self):
        """Returns an iterator that iterates over constituent TeamStandingInfo
        objects in ranked order. Raises AttributeError if rankings have not yet
        been generated."""
        return iter(self.standings)

    def infoview(self):
        return self.infos.values()

    def get_team_list(self):
        return [s.team for s in self.standings]

    def get_team_standing(self, team):
        try:
            return self.infos[team]
        except KeyError:
            raise ValueError("The team {!r} isn't in these standings.")

    def add_metric_to_team(self, team, key, value):
        assert not self.ranked, "Can't add metrics once TeamStandings object is sorted"
        self.get_team_standing(team).add_metric(key, value)

    def sort(self, precedence, tiebreak_func=None):
        self._standings = list(self.infos.values())
        if tiebreak_func:
            tiebreak_func(self._standings)
        self._standings.sort(key=lambda x: itemgetter(*precedence)(x.metrics))
        self.ranked = True


class TeamStandingsGenerator:

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
        self.options = DEFAULT_OPTIONS.copy()
        for key in options:
            if key not in self.options:
                raise ValueError("Unrecognized option: {0}".format(key))
        self.options.update(options)

        # Set up annotators
        self._interpret_metrics(metrics)
        self._interpret_rankings(rankings)
        self._check_annotators(self.metric_annotators, "metric")
        self._check_annotators(self.ranking_annotators, "ranking")

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
                wbw_keys = tuple(m for m in precedence[0:i] if m != "wbw")
                args = (index, wbw_keys)
                index += 1
            else:
                self.precedence.append(metric)
                args = ()

            annotator = MetricAnnotator(metric, *args)
            self.metric_annotators.append(annotator)
            self.precedence.extend(annotator.adds)

    def _check_annotators(self, annotators, type_str):
        """Checks the given list of annotators to ensure there are no conflicts.
        A conflict occurs if two annotators would add annotations of the same
        name."""
        names = list()
        for annotator in annotators:
            names.extend(annotator.adds)
        if len(names) != len(set(names)):
            raise StandingsError("The same {} would be added twice:\n{!r}".format(type_str, names))

    def _interpret_rankings(self, rankings):
        """Given a list of rankings, sets `self.ranking_annotators` to the
        appropriate ranking annotators."""
        self.ranking_annotators = list()

        for ranking in enumerate(rankings):
            self.ranking_annotators.append(RankAnnotator(ranking))


    @property
    def _tiebreak_func(self):
        return self.TIEBREAK_FUNCTIONS[self.options["tiebreak"]]

    def generate(self, queryset, round=None):
        """Generates standings for the teams in queryset.

        `queryset` can be a QuerySet or Manager object, and should return just
            those teams of interest for these standings.
        `round`, if specified, is the round for which to generate the standings.
            (That is, rounds after `round` are excluded from the standings.)
        """

        standings = TeamStandings(queryset)

        for annotator in self.metric_annotators:
            annotator(queryset, standings, round)

        standings.sort(self.precedence, self._tiebreak_func)

        for annotator in self.ranking_annotators:
            annotator(standings)

        return standings