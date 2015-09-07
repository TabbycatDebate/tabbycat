from collections import OrderedDict
from operator import itemgetter
from participants.models import Team

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
        if self.ranked:
            return self._standings
        else:
            raise AttributeError("TeamStandings.standings can't be accessed before sort() is called.")

    def __iter__(self):
        """Returns an iterator that iterates over constituent TeamStandingInfo
        objects in ranked order. Raises AttributeError if rankings have not yet
        been generated."""
        if self.ranked:
            return iter(self.standings)
        else:
            raise AttributeError("TeamStandings can't be iterated before sort() is called. Use infoview() for a dictview instead.")

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
        if self._sorted:
            raise RuntimeError("Can't add metrics once TeamStandings object is sorted")
        self.get_team_standing(team).add_metric(key, value)

    def add_ranking(self, team, key, value):
        if not self._sorted:
            raise RuntimeError("Can't add rankings before TeamStandings object is sorted")
        self.get_team_standing(team).add_ranking(key, value)

    def sort(self, metrics):
        key = lambda x: itemgetter(*metrics)(x.metrics)
        self._standings = sorted(self.infos.values(), key=key)
        self.ranked = True


class TeamStandingsGenerator:

    DEFAULT_OPTIONS = {
        "last_resort": "random",
    }

    def __init__(self, metrics, rankings, **options):

        # set up options dictionary
        self.options = DEFAULT_OPTIONS.copy()
        for key in options:
            if key not in self.options:
                raise ValueError("Unrecognized option: {0}".format(key))
        self.options.update(options)



    def apply_annotation(self, queryset):
        pass

    def generate(self, queryset):
        """Generates standings for the teams in queryset.

        'queryset' can be a QuerySet or Manager object, and should return just
        those teams of interest for these standings.
        """

        if all_queryset is None:
            all_queryset = queryset

        standings = TeamStandings()

