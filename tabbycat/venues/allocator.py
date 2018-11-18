import itertools
import logging
import random

from munkres import Munkres

from django.db.models import Prefetch

from adjallocation.models import DebateAdjudicator
from draw.models import DebateTeam

from .models import Venue, VenueCategory, VenueConstraint

logger = logging.getLogger(__name__)


def allocate_venues(round, debates=None):
    allocator = NaiveVenueAllocator(round, debates)
    allocator.allocate()


class BaseVenueAllocator:

    def __init__(self, round, debates=None):
        self.round = round
        self.debates = debates or self.get_debate_queryset()

        self.venues = round.active_venues.order_by('-priority').prefetch_related('venuecategory_set')

    def collect_constraints(self):
        """Returns a list of tuples `(debate, constraints)`, where `constraints`
        is a list of constraints. Each list of constraints is sorted by
        descending order of priority. Debates with no constraints are omitted
        from the dict, so each list of constraints is guaranteed not to be
        empty.

        The constraints for each debate are just all of the venue constraints
        relating to the teams, adjudicators, institutions and division of the
        debate."""

        all_constraints = {}
        for vc in VenueConstraint.objects.filter_for_debates(self.debates).select_related('category').prefetch_related('subject', 'category__venues'):
            all_constraints.setdefault(vc.subject, []).append(vc)

        debate_constraints = []

        for debate in self.debates:
            subjects = itertools.chain(
                debate.teams,
                debate.adjudicators.all(),
                [team.institution for team in debate.teams],
                [] if debate.division is None else [debate.division]
            )
            constraints = [vc for subject in subjects for vc in all_constraints.get(subject, [])]

            if len(constraints) > 0:
                constraints.sort(key=lambda x: x.priority, reverse=True)
                debate_constraints.append((debate, constraints))
                logger.info("Constraints on %s: %s", debate, constraints)

        debate_constraints.sort(key=lambda x: x[1][0].priority, reverse=True)

        return debate_constraints

    def collect_dict_constraints(self):
        constraints = self.collect_constraints()
        return {x[0]: x[1] for x in constraints}

    def save_venues(self, debate_venues):
        for debate, venue in debate_venues.items():
            logger.debug("Saving %s for %s", venue, debate)
            debate.venue = venue
            debate.save()


class NaiveVenueAllocator(BaseVenueAllocator):
    """Allocates venues in a draw to satisfy, as best it can, applicable venue
    constraints.

    The algorithm naïvely allocates from the debate with the highest-priority
    constraint to the debate with the lowest-priority constraint, choosing at
    random if more than one is available. This isn't guaranteed to be optimal,
    since a flexible high-priority debate might randomly choose a room demanded
    by a picky low-priority room.
    """

    def get_debate_queryset(self):
        return self.round.debate_set_with_prefetches(speakers=False, institutions=True)

    def allocate(self):
        self._all_venues = list(self.venues)
        self._preferred_venues = self._all_venues[:len(self.debates)]

        # take note of how many venues we expect to be short by (for error checking)
        self._venue_shortage = max(0, len(self.debates) - len(self._all_venues))

        debate_constraints = self.collect_constraints()
        debate_venues = self.allocate_constrained_venues(debate_constraints)

        unconstrained_debates = [d for d in self.debates if d not in debate_venues]
        unconstrained_venues = self.allocate_unconstrained_venues(unconstrained_debates)
        debate_venues.update(unconstrained_venues)

        # this set is only non-empty if there were too few venues overall
        debates_without_venues = [d for d in self.debates if d not in debate_venues]
        if len(debates_without_venues) != self._venue_shortage:
            logger.error("Expected venue shortage %d, but %d debates without venues",
                self._venue_shortage, len(debates_without_venues))
        debate_venues.update({debate: None for debate in debates_without_venues})

        self.save_venues(debate_venues)

    def allocate_constrained_venues(self, debate_constraints):
        """Allocates venues for debates that have one or more constraints on
        them. `debate_constraints` should be

        For each debate, it finds the set of venues that meet all its
        constraints, or if that set is empty, then it satisfies as many
        constraints as it can, with higher-priority constraints taking absolute
        precedence over lower-priority constraints. It then chooses a random
        venue from the preferred venues in that set, or if there are no
        preferred venues, then from all venues in that set.

        It runs through debates in descending order of priority, where the
        priority of a debate is the priority of its highest-priority constraint.
        """

        debate_venues = dict()

        while len(debate_constraints) > 0:
            debate, constraints = debate_constraints.pop(0)

            highest_constraint = constraints.pop(0)
            eligible_venues = set(highest_constraint.category.venues.all()) & set(self._all_venues)

            # If we can't fulfil the highest constraint, bump it down the list.
            if len(eligible_venues) == 0:
                logger.debug("Unfulfilled (highest): %s", highest_constraint)
                if len(constraints) == 0:
                    logger.debug("%s is now unconstrained", debate)
                    continue  # Failed all constraints, debate is now unconstrained
                new_priority = constraints[0].priority
                for i, dc in enumerate(debate_constraints):
                    if new_priority >= dc[1][0].priority:
                        break
                else:
                    i = 0
                debate_constraints.insert(i, (debate, constraints))
                continue

            # If we get this far, we have at least one eligible venue.

            # Find the set of eligible venues satisfying the best set of constraints.
            satisified_constraints = []
            for constraint in constraints:
                if any(sc.subject == constraint.subject for sc in satisified_constraints):
                    continue  # Skip if we've already done a constraint for this subject
                constraint_venues = set(constraint.category.venues.all())
                if eligible_venues.isdisjoint(constraint_venues):
                    logger.debug("Unfilfilled: %s", constraint)
                else:
                    eligible_venues &= constraint_venues
                    satisified_constraints.append(constraint)

            # If no eligible venues are preferred venues, drop the last preferred venue.
            preferred_venues = set(self._preferred_venues)
            if eligible_venues.isdisjoint(preferred_venues):
                logger.debug("No preferred venues available: %s", debate)
                self._preferred_venues = self._preferred_venues[:-1]
            else:
                eligible_venues &= preferred_venues

            # Finally, assign the venue.
            venue = random.choice(list(eligible_venues))
            debate_venues[debate] = venue
            self._all_venues.remove(venue)
            if venue in self._preferred_venues:
                self._preferred_venues.remove(venue)
            logger.debug("Assigning %s to %s", venue, debate)

        return debate_venues

    def allocate_unconstrained_venues(self, debates):
        """Allocates unconstrained venues by randomly shuffling the remaining
        preferred venues."""

        if len(debates) - len(self._preferred_venues) != self._venue_shortage:
            logger.error("preferred venues to unconstrained debates mismatch: "
                "%s preferred venues, %d debates", len(self._preferred_venues), len(debates))
            # we'll still keep going, since zip() stops at the end of the shorter list
        elif len(debates) != len(self._preferred_venues):
            logger.warning("%s preferred venues, %d debates, matches expected venue shortage %s",
                len(self._preferred_venues), len(debates), self._venue_shortage)

        random.shuffle(debates)
        return {debate: venue for debate, venue in zip(debates, self._preferred_venues)}


class BaseHungarianVenueAllocator(BaseVenueAllocator):
    """Base class for venue allocations using the Hungarian algorithm.

    Most of the costs would remain the same between allocators."""

    def __init__(self, round, debates=None):
        super().__init__(round, debates)

        t = self.round.tournament
        self.history_cost = t.pref('venue_history_cost')
        self.constraint_cost = t.pref('venue_constraint_cost')
        self.bad_venue_cost = t.pref('venue_score_cost')

        self.munkres = Munkres()

    def get_debate_queryset(self):
        """For history constraints.

        Get previous debates (with venues & categories) of participants in addition to current ones"""

        return self.round.debate_set.all().select_related('division', 'division__venue_category', 'venue').prefetch_related(
            Prefetch('debateadjudicator_set', queryset=DebateAdjudicator.objects.select_related('adjudicator', 'adjudicator__institution')),
            Prefetch('debateteam_set', queryset=DebateTeam.objects.select_related('team', 'team__institution'))
        )

    def allocate(self):
        self.prev_venues = self.get_previous_venue_categories()
        self.constraints = self.collect_dict_constraints()

        self.max_venue_score = self.venues[0].priority
        self.max_constraint_priority = list(self.constraints.values())[0][0].priority

        cost_matrix = []
        for d in self.debates:
            cost_matrix.append(self.debate_cost_calc(d))

        indices = self.munkres.compute(cost_matrix)

        result = {self.debates[i]: self.venues[j] for i, j in indices}
        self.save_venues(result)

    def get_previous_venue_categories(self):
        debate_prefetch = Prefetch('debateteam_set', queryset=DebateTeam.objects.filter(
            debate__round__seq__lt=self.round.seq, debate__venue__isnull=False, debate__venue__venuecategory__rotate=True).distinct())
        teams = self.round.active_teams.prefetch_related(debate_prefetch)

        prev_team_vc = {}
        for t in teams.all():
            prev_team_vc[t] = []
            for dt in t.debateteam_set.all():
                prev_team_vc[t].extend(dt.debate.venue.venuecategory_set.all())

        self.prev_venue_categories = {}
        for debate in self.debates:
            self.prev_venue_categories[debate] = []

            # Ajudicators are excepted from this constraint
            for dt in debate.debateteam_set.all():
                self.prev_venue_categories[debate].extend(prev_team_vc[dt.team])

    def debate_cost_calc(self, debate):
        venue_costs = []
        for v in self.venues:
            v_cost = 0

            # Constraints
            for c in self.constraints.get(debate, []):
                constraint_venues = c.category.venues.all()

                if v not in constraint_venues:
                    v_cost += c.priority / self.max_constraint_priority * self.constraint_cost

            # Venue "score"
            v_cost += -(v.priority / self.max_venue_score - 1) * self.bad_venue_cost

            venue_costs.append(v_cost)

        return venue_costs


class RotationVenueAllocator(BaseHungarianVenueAllocator):
    """Venue allocator with the Hungarian method.

    Avoids placing teams in the same venue category as in previous debates."""

    def debate_cost_calc(self, debate):
        venue_costs = super().debate_cost_calc(debate)

        # History constraints
        for i, v in enumerate(self.venues):
            for dv in self.prev_venue_categories[debate]:
                venue_costs[i] += int(v in dv.venues.all()) * self.history_cost

        return venue_costs


class StationaryVenueAllocator(BaseHungarianVenueAllocator):
    """Venue allocator with the Hungarian method.

    Avoids placing teams in different venue categories as in previous debates."""

    def debate_cost_calc(self, debate):
        venue_costs = super().debate_cost_calc(debate)

        # History constraints
        for i, v in enumerate(self.venues):
            for dv in self.prev_venue_categories[debate]:
                if v not in dv.venues.all():
                    venue_costs[i] += self.history_cost

        return venue_costs
