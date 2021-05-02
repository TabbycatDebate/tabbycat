"""Utilities for querying and listing conflicts and history between
participants."""
import logging
from itertools import combinations, product

from adjallocation.models import (AdjudicatorAdjudicatorConflict, AdjudicatorInstitutionConflict,
                     AdjudicatorTeamConflict, TeamInstitutionConflict)
from draw.models import Debate
from participants.models import Adjudicator, Team

logger = logging.getLogger(__name__)


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

    Although the attributes `self.adjteamconflicts`, `self.adjadjconflicts`,
    etc. aren't marked as such, they should be treated a private implementation
    detail that is subject to change. Callers should rely exclusively on
    methods of the class to access conflict information.
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
        # rather than an array (O(n)). Adjudicator pairs are stored both ways
        # round, i.e. under both `(adj1.id, adj2.id)` and `(adj2.id, adj1.id)`.

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

        teaminstconflict_instances = TeamInstitutionConflict.objects.filter(
            team__in=self.teams,
        ).select_related('institution').distinct()
        self.teaminstconflicts = {team_id: set() for team_id in self.team_ids}
        for conflict in teaminstconflict_instances:
            if conflict.team_id in self.teaminstconflicts:
                self.teaminstconflicts[conflict.team_id].add(conflict.institution)
            else:
                logger.warning("Couldnt add conflict for team ID %s to \
                                institution %s" % (conflict.team_id, conflict.institution))

        adjinstconflict_instances = AdjudicatorInstitutionConflict.objects.filter(
            adjudicator__in=self.adjudicators,
        ).select_related('institution').distinct()
        self.adjinstconflicts = {adj_id: set() for adj_id in self.adjudicator_ids}
        for conflict in adjinstconflict_instances:
            if conflict.adjudicator_id in self.adjinstconflicts:
                self.adjinstconflicts[conflict.adjudicator_id].add(conflict.institution)
            else:
                logger.warning("Couldnt add conflict for adjudicator ID %s to \
                                institution %s" % (conflict.adjudicator_id, conflict.institution))

    def personal_conflict_adj_team(self, adj, team):
        """Returns True if the adjudicator and team personally conflict."""
        assert adj.id in self.adjudicator_ids, "adjudicator not covered"
        assert team.id in self.team_ids, "team not covered"
        return (adj.id, team.id) in self.adjteamconflicts

    def personal_conflict_adj_adj(self, adj1, adj2):
        """Returns True if the two adjudicators personally conflict."""
        assert adj1.id in self.adjudicator_ids, "adjudicator 1 not covered"
        assert adj2.id in self.adjudicator_ids, "adjudicator 2 not covered"
        return (adj1.id, adj2.id) in self.adjadjconflicts

    def conflicting_institutions_adj_team(self, adj, team):
        """Returns a set of institutions that the adjudicator and team share."""
        return self.adjinstconflicts[adj.id] & self.teaminstconflicts[team.id]

    def conflicting_institutions_adj_adj(self, adj1, adj2):
        """Returns a set of institutions that the two adjudicators share."""
        return self.adjinstconflicts[adj1.id] & self.adjinstconflicts[adj2.id]

    def institutional_conflict_adj_team(self, adj, team):
        """Returns True if the adjudicator and team share at least one institution."""
        return not self.adjinstconflicts[adj.id].isdisjoint(self.teaminstconflicts[team.id])

    def institutional_conflict_adj_adj(self, adj1, adj2):
        """Returns True if the two adjudicators share at least one institution."""
        return not self.adjinstconflicts[adj1.id].isdisjoint(self.adjinstconflicts[adj2.id])

    def conflict_adj_team(self, adj, team):
        """Returns True if the adjudicator and team conflict."""
        return (self.personal_conflict_adj_team(adj, team) or
                self.institutional_conflict_adj_team(adj, team))

    def conflict_adj_adj(self, adj1, adj2):
        """Returns True if the two adjudicators conflict."""
        return (self.personal_conflict_adj_adj(adj1, adj2) or
                self.institutional_conflict_adj_adj(adj1, adj2))

    def serialized_by_participant(self):
        """Returns a tuple of two dicts, mapping primary keys of teams and
        adjudicators respectively to a three-key dict
            {'team': [], 'adjudicator': [], 'institution': []}
        where each list contains single-key dicts {'id': id} containing the
        primary key of conflicting objects."""

        teams = {team_id: {'team': [], 'adjudicator': [], 'institution': []}
                 for team_id in self.team_ids}
        adjudicators = {adj_id: {'team': [], 'adjudicator': [], 'institution': []}
                        for adj_id in self.adjudicator_ids}

        for adj_id, team_id in self.adjteamconflicts:
            teams[team_id]['adjudicator'].append({'id': adj_id})
            adjudicators[adj_id]['team'].append({'id': team_id})

        for adj1_id, adj2_id in self.adjadjconflicts:
            adjudicators[adj1_id]['adjudicator'].append({'id': adj2_id})

        for team_id, institutions in self.teaminstconflicts.items():
            teams[team_id]['institution'] = [{'id': inst.id} for inst in institutions]

        for adj_id, institutions in self.adjinstconflicts.items():
            adjudicators[adj_id]['institution'] = [{'id': inst.id} for inst in institutions]

        return teams, adjudicators


class HistoryInfo:
    """Manages information about past encounters between participants prior to
    (and not including) a given round. The object stores information about all
    teams and adjudicators who participated in any round prior to the given
    round.

    The main purpose of this class is to streamline queries about history. This
    class hits the database once, on creation, with queries for
    `DebateAdjudicator` and `DebateTeam`. It then can be used to find
    efficiently whether particular participants have seen each other, without a
    need for further SQL queries or excessive data processing.

    Although the attributes `self.adjteamhistories` and  `self.adjadjhistories`
    aren't marked as such, they should be treated a private implementation
    detail that is subject to change. Callers should rely exclusively on
    methods of the class to access history information.
    """

    def __init__(self, round, teams=None, adjudicators=None):
        self.round = round
        self.tournament = round.tournament
        self._fetch_histories_from_db()

    def _fetch_histories_from_db(self):
        """Fetches history information from the database, based on `self.teams`
        and `self.adjudicators`."""

        # The prefetches don't need `.select_related('adjudicator')` and
        # `.select_related('team')`, because we only deal with the primary keys
        # of adjudicators and teams.

        debates = Debate.objects.filter(
            round__tournament=self.tournament,
            round__seq__lt=self.round.seq,
        ).prefetch_related(
            'debateadjudicator_set',
            'debateteam_set',
        ).select_related('round')

        # Histories are stored in a dict, where keys are (adj.id, team.id) or
        # (adj1.id, adj2.id) tuples, and values are lists of `seq` integers
        # denoting the rounds where the participants saw each other. For
        # example, if `Adjudicator(id=33)` saw `Team(id=25)` in rounds 3 and 5,
        # then `self.adjteamhistories[(33, 25)] = [3, 5]`. They're stored in a
        # dict to allow for O(1) lookup for adj-team or adj1-adj2 pairs.
        #
        # Adjudicator pairs are stored both ways round, i.e., under both
        # `(adj1.id, adj2.id)` and `(adj2.id, adj1.id)`. If a pair of
        # participants has not seen each other, they are not in the dict at all;
        # an empty list is *not* stored to indicate a lack of encounter.

        self.adjteamhistories = {}
        self.adjadjhistories = {}

        for debate in debates:
            r = debate.round.seq

            for da, dt in product(debate.debateadjudicator_set.all(), debate.debateteam_set.all()):
                pair = (da.adjudicator_id, dt.team_id)
                self.adjteamhistories.setdefault(pair, []).append(r)

            for da1, da2 in combinations(debate.debateadjudicator_set.all(), 2):
                pair = (da1.adjudicator_id, da2.adjudicator_id)
                self.adjadjhistories.setdefault(pair, []).append(r)

    def seen_adj_team(self, adj, team):
        """Returns True if the adjudicator has seen this team in the history
        covered by this object."""
        return (adj.id, team.id) in self.adjteamhistories

    def seen_adj_adj(self, adj1, adj2):
        """Returns True if the adjudicators have judged together in the history
        covered by this object."""
        return (adj1.id, adj2.id) in self.adjadjhistories

    def serialized_by_participant(self):
        """Returns a tuple of two dicts, mapping primary keys of teams and
        adjudicators respectively to a two-key dict
            {'team': [], 'adjudicator': []}
        where each list contains two-key dicts
            {'ago': ago, 'id': id}
        containing how long ago the participants saw each other, and the
        primary key of the other participant.
        """

        teams = {}
        adjudicators = {}
        now = self.round.seq

        for (adj_id, team_id), rseqs in self.adjteamhistories.items():
            history = adjudicators.setdefault(adj_id, {'team': [], 'adjudicator': []})
            history['team'].extend([{'id': team_id, 'ago': now - r} for r in rseqs])

            history = teams.setdefault(team_id, {'team': [], 'adjudicator': []})
            history['adjudicator'].extend([{'id': adj_id, 'ago': now - r} for r in rseqs])

        for (adj1_id, adj2_id), rseqs in self.adjadjhistories.items():
            history = adjudicators.setdefault(adj1_id, {'team': [], 'adjudicator': []})
            history['adjudicator'].extend([{'id': adj2_id, 'ago': now - r} for r in rseqs])

        # Need to reverse the order so the second adj also has a record
        for (adj2_id, adj1_id), rseqs in self.adjadjhistories.items():
            history = adjudicators.setdefault(adj1_id, {'team': [], 'adjudicator': []})
            history['adjudicator'].extend([{'id': adj2_id, 'ago': now - r} for r in rseqs])

        return teams, adjudicators
