from collections import OrderedDict
from operator import itemgetter
from participants.models import Team
from .metrics import METRIC_ANNOTATORS, WhoBeatWhomMetricAnnotator, WhoBeatWhomDisplayMetricAnnotator
import random

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

    @property
    def team(self):
        if not self._team:
            self._team = Team.objects.get(id=self.team_id)
        return self._team

    def add_metric(self, name, value):
        if name in metrics:
            raise KeyError("There is already a metric {!r} for this team", name)
        self.metrics[name] = value

    def add_ranking(self, name, value):
        if name in ranking:
            raise KeyError("There is already a ranking {!r} for this team", name)
        self.rankings[name] = value


class TeamStandings:
    """Presents all information about the team standings requested. Returned
    by `TeamStandingsGenerator`."""

    def __init__(self, teams):
        self.infos = {team: TeamStandingInfo(team) for team in teams}
        self.ranked = False

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

    def add_metric(self, team, key, value):
        assert not self.ranked, "Can't add metrics once TeamStandings object is sorted"
        self.get_team_standing(team).add_metric(key, value)

    def add_ranking(self, team, key, value):
        assert self.ranked, "Can't add rankings before TeamStandings object is sorted"
        self.get_team_standing(team).add_ranking(key, value)

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
        "random": random.shuffle,
        "alpha" : lambda x: x.sort(key=lambda y: y.team.short_name),
    }

    def __init__(self, metrics, rankings, **options):

        # Set up options dictionary
        self.options = DEFAULT_OPTIONS.copy()
        for key in options:
            if key not in self.options:
                raise ValueError("Unrecognized option: {0}".format(key))
        self.options.update(options)

        # Set up metric annotators
        self._interpret_metrics(metrics)

        # Set up ranking annotators

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
        counter = 1

        for i, metric in enumerate(metrics):
            if metric == "wbw":
                self.precedence.append("wbw" + str(counter))
                wbw_keys = tuple(m for m in precedence[0:i] if m != "wbw")
                self.metric_annotators.append(WhoBeatWhomMetricAnnotator(counter, wbw_keys))
                counter += 1
            else:
                self.precedence.append(metric)
                self.metric_annotators.append(METRIC_ANNOTATORS[metric]())

        if "wbw" in metrics:
            self.metric_annotators.append(WhoBeatWhomDisplayMetricAnnotator())

    def _interpret_rankings(self, rankings):


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

        standings = TeamStandings()

        for annotator in self.metric_annotators:
            annotator(queryset, standings, round)

        standings.sort(self.precedence, self._tiebreak_func)

        for annotator in self.ranking_annotators:
            annotator(standings)
