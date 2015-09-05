from collections import OrderedDict
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

        self.metrics = OrderedDict()
        self.rankings = OrderedDict()

    @property
    def team(self):
        if not self._team:
            self._team = Team.objects.get(id=self.team_id)
        return self._team

    def _add_attribute(self, name, value):
        if hasattr(self, name):
            raise ValueError("This StandingInfo already has an attribute {!r}".format(name))
        setattr(self, name, value)

    def add_metric(self, name, value):
        self.metrics[name] = value
        self._add_attribute(name, value)

    def add_ranking(self, name, value):
        self.rankings[name] = value
        self._add_attribute(name, value)


class TeamStandings:
    """Presents all information about the team standings requested. Returned
    by TeamStandingsGenerator."""

    def __init__(self, tournament):
        self.tournament = tournament
        self.standings = list()

    def __iter__(self):
        return iter(self.standings)

    def get_team_standing(self, team):
        pass

    def get_team_metric(self, team, metric):
        pass


class TeamStandingsGenerator:

    def __init__(self, metrics, rankings):
        pass

    def generate(self, queryset, all_queryset=None):
        if all_queryset is None:
            all_queryset = queryset
