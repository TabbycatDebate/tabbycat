import logging
import random
import time
from collections import Counter
from math import log2
from statistics import pvariance

import munkres
from django.utils.translation import gettext as _

from .common import BaseBPDrawGenerator, DrawUserError
from .pairing import BPPairing

logger = logging.getLogger(__name__)


class BPHungarianDrawGenerator(BaseBPDrawGenerator):
    """Power-paired draw for BP based on the Hungarian algorithm.
    With default options, this is WUDC-compliant.

    Options:
        "pullup" - How pull-ups are distributed. Permitted values:

            "anywhere" - Pull-up teams may be paired into any room in the entire
                         bracket.

            "one_room" - All pull-up teams must be paired into the same room.
                         This room is then the lowest room in the bracket, sort
                         of functioning as an intermediate bracket, except that
                         any team from the brackets above and below may be
                         paired into it. Not WUDC-compliant.

        "position_cost" - How position costs are assigned. Permitted values:

            "simple"   - Cost is the number of times the team has already been
                         in that position, less the number of times the team has
                         been in its least frequent position.

            "entropy"  - Rényi entropy, C = n[2 - H_α(p)], where p is the
                         empirical distribution associated with the position
                         history of the team, H_α(p) is the Rényi entropy of
                         order α thereof, and n is the number of rounds the team
                         has competed in). See the "renyi_order" option below.

            "variance" - The population variance of multiplicities in the
                         history.

        "exponent" - (float) The value returned by the cost function is raised
                     to this power. Higher exponents place more weight on
                     reducing larger problems, i.e., highly uneven position
                     histories. Most tournaments should use a value between 2.0
                     and 5.0.

        "renyi_order" - (float) The order of the Rényi entropy used, often
                        denoted by α. The case α = 1.0 yields Shannon entropy;
                        α = 0.0 Hartley entropy; α = 2.0 collision entropy.

        "assignment_method" - Algorithm used to solve the assignment problem.
                              Permitted values:

            "hungarian"             - Hungarian algorithm, with no randomness.
                                      Not WUDC-compliant.

            "hungarian_preshuffled" - Hungarian algorithm, with the rows and
                                      columns of the cost matrix permuted
                                      randomly beforehand.
    """

    requires_even_teams = True
    requires_prev_result = False

    DEFAULT_OPTIONS = {
        "pullup"           : "anywhere",
        "position_cost"    : "entropy",
        "renyi_order"      : 1.0,
        "exponent"         : 4.0,
        "assignment_method": "hungarian_preshuffled",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.check_teams_for_attribute("points")
        self.check_teams_for_attribute("side_history")
        self.munkres = munkres.Munkres()

    def generate(self):
        self._rooms = self.define_rooms([team.points for team in self.teams])
        self._costs = self.generate_cost_matrix(self._rooms)
        self._indices = self.solve_assignment(self._costs)
        self._draw = self.make_pairings(self._rooms, self._indices)

        self.annotate_team_flags(self._draw)  # operates in-place
        return self._draw

    # Defining rooms

    DEFINE_ROOM_FUNCTIONS = {
        "anywhere": "_define_rooms_anywhere",
        "one_room": "_define_rooms_one_room",
    }

    def define_rooms(self, points):
        """Given a list of team point values (one for each team), returns a list
        of 2-tuples `(level, allowed)`, where `level` is the level of the
        bracket, and `allowed` is a set of team point values that are allowed to
        be in that room."""
        function = self.get_option_function("pullup", self.DEFINE_ROOM_FUNCTIONS)
        return function(points)

    @staticmethod
    def _define_rooms_anywhere(points):
        """Defines rooms so that pull-up teams can go anywhere in the next
        bracket up."""
        counts = Counter(points)
        rooms = []
        allowed = set()
        nteams = 0
        level = None
        pullups_needed = 0
        for p in sorted(counts.keys(), reverse=True):
            if pullups_needed < counts[p]: # complete the bracket
                if pullups_needed:
                    allowed.add(p)
                    counts[p] -= pullups_needed
                    nteams += pullups_needed
                assert nteams % 4 == 0
                rooms += [(level, allowed)] * (nteams // 4)
                nteams = 0
                allowed = set()
                level = None

            # add this entire bracket to the bracket
            if counts[p] > 0:
                allowed.add(p)
                if level is None:
                    level = p
            nteams += counts[p]
            pullups_needed = (-nteams) % 4

        assert nteams % 4 == 0
        rooms += [(level, allowed)] * (nteams // 4)

        return rooms

    @staticmethod
    def _define_rooms_one_room(points):
        """Defines rooms so that all pull-up teams are in the same room."""
        points = sorted(points, reverse=True)
        rooms = zip(*([iter(points)] * 4))
        return [(max(r), set(r)) for r in rooms]

    # Cost matrix

    POSITION_COST_FUNCTIONS = {
        "simple" : "_position_cost_simple",
        "variance": "_position_cost_variance",
    }

    @staticmethod
    def get_entropy_position_cost_function(α):  # noqa: N803
        if α == 1.0:
            logger.info("Using Shannon entropy (α = 1)")
            return BPHungarianDrawGenerator._position_cost_shannon_entropy
        elif α == 0.0:
            logger.info("Using min-entropy (α = 0)")
            return BPHungarianDrawGenerator._position_cost_min_entropy
        elif α > 0.0:
            logger.info("Using Rényi entropy with α = %f", α)
            return BPHungarianDrawGenerator._get_position_cost_renyi_entropy_function(α)
        else:
            raise DrawUserError(_("The Rényi order can't be negative, and it's currently set "
                "to %(alpha)f.") % {'alpha': α})

    def get_position_cost_function(self):
        """Extension of self.get_option_function() that includes special
        handling for the "entropy" option."""
        if self.options["position_cost"] == "entropy":
            α = self.options["renyi_order"]  # noqa: N806
            return self.get_entropy_position_cost_function(α)
        else:  # fall back to general implementation
            return self.get_option_function("position_cost", self.POSITION_COST_FUNCTIONS)

    @staticmethod
    def _update_history(pos, history):
        new_history = history.copy()
        new_history[pos] += 1
        return new_history

    @staticmethod
    def _position_cost_simple(pos, history):
        return history[pos]

    @staticmethod
    def _position_cost_variance(pos, history):
        history = BPHungarianDrawGenerator._update_history(pos, history)
        return pvariance(history)

    @staticmethod
    def _position_cost_shannon_entropy(pos, history):
        history = BPHungarianDrawGenerator._update_history(pos, history)
        n = sum(history)
        probs = [p/n for p in history]
        selfinfo = [0 if p == 0 else -p*log2(p) for p in probs]
        return (2 - sum(selfinfo)) * n

    @staticmethod
    def _position_cost_min_entropy(pos, history):
        history = BPHungarianDrawGenerator._update_history(pos, history)
        return (2 - log2(sum(p > 0 for p in history))) * sum(history)

    @staticmethod
    def _get_position_cost_renyi_entropy_function(α):  # noqa: N803
        def _position_cost_renyi_entropy(pos, history):
            history = BPHungarianDrawGenerator._update_history(pos, history)
            n = sum(history)
            probs = [p/n for p in history]
            return (2 - log2(sum([p ** α for p in probs])) / (1 - α)) * n
        return _position_cost_renyi_entropy

    def generate_cost_matrix(self, rooms):
        """Returns a cost matrix for the tournament.
        Rows (inner lists) are teams, in the same order as in `self.teams`.
        Columns (elements) are positions in rooms, ordered first by room in the
        order returned by `rooms`, then in speaking order (OG, OO, CG, CO).
        Rules:
         - if the team (given its points) is not allowed in the room, use
           DISALLOWED.
         - otherwise, for each position, use the position cost for that position
           (for a team with that position history).
        """
        nteams = len(self.teams)
        cost = self.get_position_cost_function()
        exponent = self.options["exponent"]

        costs = []
        for team in self.teams:
            row = []
            for level, allowed in rooms:
                if team.points not in allowed:
                    row.extend([munkres.DISALLOWED] * 4)
                else:
                    row.extend([cost(pos, team.side_history) ** exponent for pos in range(4)])
            assert len(row) == nteams
            costs.append(row)

        assert len(costs) == nteams
        return costs

    # Assignment algorithms

    ASSIGNMENT_ALGORITHM_FUNCTIONS = {
        "hungarian"            : "_assign_hungarian",
        "hungarian_preshuffled": "_assign_hungarian_preshuffled",
    }

    def solve_assignment(self, costs):
        """Solves the assignment problem presented by the cost matrix `costs`.
        Returns a list of indices (row, col) describing the optimal assignment.
        """
        function = self.get_option_function("assignment_method", self.ASSIGNMENT_ALGORITHM_FUNCTIONS)
        start = time.perf_counter()
        logger.info("Running assignment algorithm for %d teams...", len(costs))
        indices = function(costs)
        total_cost = sum(costs[i][j] for i, j in indices)
        elapsed = time.perf_counter() - start
        logger.info("Assignment took %.2f seconds, total cost: %f", elapsed, total_cost)
        return indices

    def _assign_hungarian(self, costs):
        return self.munkres.compute(costs)

    def _assign_hungarian_preshuffled(self, costs):
        n = len(costs)
        K = random.sample(range(n), n)             # noqa: N806
        J = random.sample(range(n), n)             # noqa: N806
        C = [[costs[i][j] for j in J] for i in K]  # noqa: N806
        indices = self.munkres.compute(C)
        return [(K[i], J[j]) for i, j in indices]

    # Make pairings

    def make_pairings(self, rooms, indices):
        """Creates the BPPairing objects. Also flags pull-up rooms."""
        teams_in_room = [[None, None, None, None] for i in range(len(indices) // 4)]
        for t, r in indices:
            teams_in_room[r // 4][r % 4] = self.teams[t]

        pairings = []
        for i, ((level, allowed), teams) in enumerate(zip(rooms, teams_in_room), start=1):
            points_in_room = set(team.points for team in teams)
            if not all([x in allowed for x in points_in_room]):
                logger.error("Teams with points %s in room that should only have %s", allowed, points_in_room)
            pairing = BPPairing(teams=teams, bracket=level, room_rank=i)
            pairings.append(pairing)

            for team in teams:
                if team.points < max(points_in_room):
                    self.add_team_flag(team, "pullup")

        return pairings
