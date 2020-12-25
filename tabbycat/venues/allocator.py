import itertools
import logging
import random

from draw.models import Debate

from .models import VenueConstraint

logger = logging.getLogger(__name__)


def allocate_venues(round, debates=None):
    allocator = VenueAllocator()
    allocator.allocate(round, debates)


class VenueAllocator:
    """Allocates venues in a draw to satisfy, as best it can, applicable venue
    constraints.

    The algorithm naïvely allocates from the debate with the highest-priority
    constraint to the debate with the lowest-priority constraint, choosing at
    random if more than one is available. This isn't guaranteed to be optimal,
    since a flexible high-priority debate might randomly choose a room demanded
    by a picky low-priority room.
    """

    def allocate(self, round, debates=None):
        if debates is None:
            debates = round.debate_set_with_prefetches(speakers=False, institutions=True)
        self._all_venues = list(round.active_venues.order_by('-priority'))
        self._preferred_venues = self._all_venues[:len(debates)]

        # take note of how many venues we expect to be short by (for error checking)
        self._venue_shortage = max(0, len(debates) - len(self._all_venues))

        debate_constraints = self.collect_constraints(debates)
        debate_venues = self.allocate_constrained_venues(debate_constraints)

        unconstrained_debates = [d for d in debates if d not in debate_venues]
        unconstrained_venues = self.allocate_unconstrained_venues(unconstrained_debates)
        debate_venues.update(unconstrained_venues)

        # this set is only non-empty if there were too few venues overall
        debates_without_venues = [d for d in debates if d not in debate_venues]
        if len(debates_without_venues) != self._venue_shortage:
            logger.error("Expected venue shortage %d, but %d debates without venues",
                self._venue_shortage, len(debates_without_venues))
        debate_venues.update({debate: None for debate in debates_without_venues})

        self.save_venues(debate_venues)

    def collect_constraints(self, debates):
        """Returns a list of tuples `(debate, constraints)`, where `constraints`
        is a list of constraints. Each list of constraints is sorted by
        descending order of priority. Debates with no constraints are omitted
        from the dict, so each list of constraints is guaranteed not to be
        empty.

        The constraints for each debate are just all of the venue constraints
        relating to the teams, adjudicators, and institutions of the debate."""

        all_constraints = {}
        for vc in VenueConstraint.objects.filter_for_debates(debates).prefetch_related('subject'):
            all_constraints.setdefault(vc.subject, []).append(vc)

        debate_constraints = []

        for debate in debates:
            subjects = itertools.chain(
                debate.teams,
                debate.adjudicators.all(),
                [team.institution for team in debate.teams],
            )
            constraints = [vc for subject in subjects for vc in all_constraints.get(subject, [])]

            if len(constraints) > 0:
                constraints.sort(key=lambda x: x.priority, reverse=True)
                debate_constraints.append((debate, constraints))
                logger.info("Constraints on %s: %s", debate, constraints)

        debate_constraints.sort(key=lambda x: x[1][0].priority, reverse=True)

        return debate_constraints

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

    def save_venues(self, debate_venues):
        for debate, venue in debate_venues.items():
            debate.venue = venue
        Debate.objects.bulk_update(debate_venues.keys(), ['venue'])
