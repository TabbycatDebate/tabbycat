from collections import defaultdict, Counter
from itertools import chain
import random

from participants.models import Team
from tournaments.models import Round
from standings.teams import TeamStandingsGenerator

from .models import Debate, DebateTeam, TeamPositionAllocation
from .generator import DrawGenerator

OPTIONS_TO_CONFIG_MAPPING = {
    "avoid_institution": "draw_rules__avoid_same_institution",
    "avoid_history": "draw_rules__avoid_team_history",
    "history_penalty": "draw_rules__team_history_penalty",
    "institution_penalty": "draw_rules__team_institution_penalty",
    "side_allocations": "draw_rules__draw_side_allocations",
    "avoid_conflicts": "draw_rules__draw_avoid_conflicts",
    "odd_bracket"     : "draw_rules__draw_odd_bracket",
    "pairing_method"  : "draw_rules__draw_pairing_method",
}

TPA_MAP = {TeamPositionAllocation.POSITION_AFFIRMATIVE: "aff",
           TeamPositionAllocation.POSITION_NEGATIVE: "neg"}


def DrawManager(round, active_only=True):
    klass = DRAW_MANAGER_CLASSES[round.draw_type]
    return klass(round, active_only)


class BaseDrawManager:
    """Creates, modifies and retrieves relevant Debate objects relating to a draw."""

    relevant_options = ["avoid_institution", "avoid_history", "history_penalty", "institution_penalty", "side_allocations"]

    def __init__(self, round, active_only=True):
        self.round = round
        self.debate_set = round.debate_set
        self.active_only = active_only

    def get_teams(self):
        return self.round.active_teams.all() if self.active_only else self.round.tournament.team_set.all()

    def _populate_aff_counts(self, teams):
        if self.round.prev:
            prev_seq = self.round.prev.seq
            for team in teams:
                team.aff_count = team.get_aff_count(prev_seq)
        else:
            for team in teams:
                team.aff_count = 0

    def _populate_team_position_allocations(self, teams):
        tpas = dict()
        for tpa in self.round.teampositionallocation_set.all():
            tpas[tpa.team] = TPA_MAP[tpa.position]
        for team in teams:
            if team in tpas:
                team.allocated_side = tpas[team]

    def _assign_venues(self, pairings):
        """Returns a dict whose keys are elements of `pairings` and whose values
        are the venues that should be assigned to each pairing. For those
        pairings that have associated venue groups, the venue is guaranteed to
        be in that group. If no suitable venue can be found for a pairing, no
        venue will be assigned to it, and that pairing will not be in the
        returned dict.

        The algorithm used for venue assignment is designed to achieve two
        objectives:
          - Pairings with associated venue groups must be assigned venues in
            those groups, and
          - Subject to that constrain, all venue assignments must be random.

        In particular, this means that pairings with associated venue groups
        should not always get high-priority rooms as a side effect of the
        algorithm.

        The algorithm is as follows:
         1. Figure out how many pairings are associated with each venue group,
            and how many pairings do not have venue constraints ("unconstrained
            pairings").
         2. Form a list of venues that will be used, by:
             a. first, for each venue group, taking as many venues as there are
                associated pairings, highest priority first,
             b. then, from all remaining venues, taking as many venues as there
                are unconstrained pairings, highest priority first. Note that
                venues added here may be in venue groups that were considered in
                (a), but weren't of sufficiently high priority during step (a).
         3. Group the list of venues by venue group, regardless of whether they
            were added in step (a) or (b).
         4. For each venue group, generate a list of venues that will be used
            for the associated pairings, by choosing at random the appropriate
            number of venues from the grouped venues list. Note that these will
            not necessarily be the same rooms taken in step 2(a): this is by
            design, so that unconstrained pairings don't all end up with the
            low-priority rooms chosen in 2(b). Assign a venue to each pairing.
         5. Gather the leftover venues, and assign one to each unconstrained
            pairing.
        """

        def groupdict(iterable, key): # helper function, like groupby() by does not require pre-sorting
            results = defaultdict(list)
            for item in iterable:
                results[key(item)].append(item)
            return results

        # Step 1
        pairings = [p for p in pairings if Team.TYPE_BYE not in [t.type for t in p.teams]] # filter out byes
        constrained_pairings = groupdict(pairings, lambda p: p.venue_group)
        unconstrained_pairings = constrained_pairings[None]
        del constrained_pairings[None]
        pairing_counts = Counter([p.venue_group for p in constrained_pairings])

        # Step 2(a)
        venues_by_group = groupdict(self.round.active_venues.order_by('-priority'), lambda v: v.group)
        venues_for_use = list()
        for vg, count in pairing_counts.items():
            venues_in_group = venues_by_group.get(vg, [])
            venues_for_use.extend(venues_in_group[:count])
            venues_in_group[:count] = [] # remove from bank

        # Step 2(b)
        leftover_venues = sorted(chain(*venues_by_group.values()), key=lambda v: -v.priority)
        unconstrained_count = len(unconstrained_pairings)
        venues_for_use.extend(leftover_venues[:unconstrained_count])

        # Step 3
        random.shuffle(venues_for_use)
        venues_by_group = groupdict(venues_for_use, lambda v: v.group)
        assignments = dict()

        # Step 4
        for vg, pairings_group in constrained_pairings:
            venues_in_group = venues_by_group.get(vg, [])
            group_assignments = dict(zip(pairings_group, venues_in_group))
            assignments.update(group_assignments)
            venues_in_group[:len(group_assignments)] = [] # remove from bank

        # Step 5
        leftover_venues = list(chain(*venues_by_group.values()))
        random.shuffle(leftover_venues)
        assignments.update(dict(zip(unconstrained_pairings, leftover_venues)))

        return assignments

    def _make_debates(self, pairings):
        random.shuffle(pairings)  # to avoid IDs indicating room ranks
        venues = self._assign_venues(pairings)

        for pairing in pairings:
            debate = Debate(round=self.round)
            debate.venue = venues.get(pairing, None)
            debate.division = pairing.division
            debate.bracket = pairing.bracket
            debate.room_rank = pairing.room_rank
            debate.flags = ",".join(pairing.flags)  # comma-separated list
            debate.save()

            DebateTeam(debate=debate, team=pairing.teams[0], position=DebateTeam.POSITION_AFFIRMATIVE).save()
            DebateTeam(debate=debate, team=pairing.teams[1], position=DebateTeam.POSITION_NEGATIVE).save()

    def delete(self):
        self.debate_set.all().delete()

    def create(self):
        """Generates a draw and populates the database with it."""

        if self.round.draw_status != Round.STATUS_NONE:
            raise RuntimeError("Tried to create a draw on round that already has a draw")

        self.delete()

        teams = self.get_teams()
        self._populate_aff_counts(teams)
        self._populate_team_position_allocations(teams)

        options = dict()
        for key in self.relevant_options:
            options[key] = self.round.tournament.preferences[OPTIONS_TO_CONFIG_MAPPING[key]]
        if options["side_allocations"] == "manual-ballot":
            options["side_allocations"] = "balance"

        drawer = DrawGenerator(self.draw_type, teams, self.round, results=None, **options)
        pairings = drawer.generate()
        self._make_debates(pairings)
        self.round.draw_status = Round.STATUS_DRAFT
        self.round.save()


class RandomDrawManager(BaseDrawManager):
    draw_type = "random"
    relevant_options = BaseDrawManager.relevant_options + ["avoid_conflicts"]


class ManualDrawManager(BaseDrawManager):
    draw_type = "manual"


class PowerPairedDrawManager(BaseDrawManager):
    draw_type = "power_paired"
    relevant_options = BaseDrawManager.relevant_options + ["avoid_conflicts", "odd_bracket", "pairing_method"]

    def get_teams(self):
        metrics = self.round.tournament.pref('team_standings_precedence')
        generator = TeamStandingsGenerator(metrics, ('rank', 'subrank'), tiebreak="random")
        standings = generator.generate(super().get_teams(), round=self.round.prev)

        ranked = []
        for standing in standings:
            team = standing.team
            team.points = next(standing.itermetrics())
            ranked.append(team)

        return ranked


class RoundRobinDrawManager(BaseDrawManager):
    draw_type = "round_robin"


DRAW_MANAGER_CLASSES = {
    Round.DRAW_RANDOM: RandomDrawManager,
    Round.DRAW_POWERPAIRED: PowerPairedDrawManager,
    Round.DRAW_ROUNDROBIN: RoundRobinDrawManager,
    Round.DRAW_MANUAL: ManualDrawManager,
}
