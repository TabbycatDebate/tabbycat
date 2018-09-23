"""Utilities for querying and listing conflicts between participants."""

from participants.models import Adjudicator, Team

from .models import (AdjudicatorAdjudicatorConflict, AdjudicatorInstitutionConflict,
                     AdjudicatorTeamConflict, TeamInstitutionConflict)


class ConflictsInfo:
    """Manages information about conflicts between participants.

    The main purpose of this class is to streamline queries about conflicts.
    This class hits the database once, on creation, with one query per type of
    conflict (adjudicator-team, adjudicator-adjudicator, adjudicator-institution
    and adjudicator-team). It then can be used to find efficiently whether
    particular participants conflict, without a need for further SQL queries or
    excessive data processing.

    All queries must relate to teams and adjudicators that were in the QuerySets
    or other iterables that were provided to the constructor.
    """

    def __init__(self, teams=None, adjudicators=None):
        self.teams = teams or Team.objects.none()
        self.adjudicators = adjudicators or Adjudicator.objects.none()
        self._fetch_conflicts_from_db()

    def _fetch_conflicts_from_db(self):
        """Fetches relevant conflicts from the database, based on `self.teams`
        and `self.adjudicators`."""

        # Refresh `self.adjudicator_ids` and `self.team_ids`
        self.adjudicator_ids = {adj.id for adj in self.adjudicators}
        self.team_ids = {team.id for team in self.teams}

        # Adjudicator-team and adjudicator-adjudicator conflicts are stored as
        # sets of primary keys. Primary keys to avoid having to select_related
        # all the teams and adjudicators from the database, and sets so that
        # they're stored in a hash-map structure (for O(1) `x in S` check)
        # rather than an array (O(n)).

        adjteamconflict_instances = AdjudicatorTeamConflict.objects.filter(
            adjudicator__in=self.adjudicators,
            team__in=self.teams,
        ).distinct()
        self.adjteamconflicts = {(c.adjudicator_id, c.team_id) for c in adjteamconflict_instances}

        adjadjconflict_instances = AdjudicatorAdjudicatorConflict.objects.filter(
            adjudicator1__in=self.adjudicators,
            adjudicator2__in=self.adjudicators,
        ).distinct()
        self.adjadjconflicts = set()
        for conflict in adjadjconflict_instances:
            self.adjadjconflicts.add((conflict.adjudicator1_id, conflict.adjudicator2_id))
            self.adjadjconflicts.add((conflict.adjudicator2_id, conflict.adjudicator1_id))

        # Adjudicator-institution and team-institution conflicts are stored as
        # sets, which in turn are in dicts whose keys are the adjudicator/team
        # primary keys. The sets contain the entire institution objects, since
        # it's useful in some contexts to be able to grab institution details
        # quickly from them. They're sets to allow the use of the set
        # intersection operator to check for institution overlap.

        adjinstconflict_instances = AdjudicatorInstitutionConflict.objects.filter(
            adjudicator__in=self.adjudicators,
        ).select_related('institution').distinct()
        self.adjinstconflicts = {adj_id: set() for adj_id in self.adjudicator_ids}
        for conflict in adjinstconflict_instances:
            self.adjinstconflicts[conflict.adjudicator_id].add(conflict.institution)

        teaminstconflict_instances = TeamInstitutionConflict.objects.filter(
            team__in=self.teams,
        ).select_related('institution').distinct()
        self.teaminstconflicts = {team_id: set() for team_id in self.team_ids}
        for conflict in teaminstconflict_instances:
            self.teaminstconflicts[conflict.team_id].add(conflict.institution)

    def personal_conflict_adj_team(self, adj, team):
        assert adj.id in self.adjudicator_ids, "adjudicator not covered"
        assert team.id in self.team_ids, "team not covered"
        return (adj.id, team.id) in self.adjteamconflicts

    def personal_conflict_adj_adj(self, adj1, adj2):
        assert adj1.id in self.adjudicator_ids, "adjudicator 1 not covered"
        assert adj2.id in self.adjudicator_ids, "adjudicator 2 not covered"
        return (adj1.id, adj2.id) in self.adjadjconflicts

    def conflicting_institutions_adj_team(self, adj, team):
        return self.adjinstconflicts[adj.id] & self.teaminstconflicts[team.id]

    def conflicting_institutions_adj_adj(self, adj1, adj2):
        return self.adjinstconflicts[adj1.id] & self.adjinstconflicts[adj2.id]

    def institutional_conflict_adj_team(self, adj, team):
        return not self.adjinstconflicts[adj.id].isdisjoint(self.teaminstconflicts[team.id])

    def institutional_conflict_adj_adj(self, adj1, adj2):
        return not self.adjinstconflicts[adj1.id].isdisjoint(self.adjinstconflicts[adj2.id])

    def conflict_adj_team(self, adj, team):
        return (self.personal_conflict_adj_team(adj, team) or
                self.institutional_conflict_adj_team(adj, team))

    def conflict_adj_adj(self, adj1, adj2):
        return (self.personal_conflict_adj_adj(adj1, adj2) or
                self.institutional_conflict_adj_adj(adj1, adj2))
