import logging
import random

from .models import AdjudicatorVenueConstraint, InstitutionVenueConstraint, TeamVenueConstraint

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
            debates = round.debate_set_with_prefetches(speakers=False)
        self._all_venues = list(round.active_venues.order_by('-priority'))
        self._preferred_venues = self._all_venues[:len(debates)]

        debate_constraints = self.collect_constraints(debates)
        debate_venues = self.allocate_constrained_venues(debate_constraints)

        unconstrained_debates = [d for d in debates if d not in debate_venues]
        unconstrained_venues = self.allocate_unconstrained_venues(unconstrained_debates)
        debate_venues.update(unconstrained_venues)

        self.save_venues(debate_venues)

    def collect_constraints(self, debates):
        """Returns a list of tuples `(debate, constraints)`, where `constraints`
        is a list of constraints. Each list of constraints is sorted by
        descending order of priority. Debates with no constraints are omitted
        from the dict, so each list of constraints is guaranteed not to be
        empty.

        The constraints for each debate are just all of the venue constraints
        relating to the teams, adjudicators, institutions and division of the
        debate."""

        debate_constraints = []

        for debate in debates:
            teams = list(debate.teams)
            adjudicators = [da for da in debate.adjudicators.all()]

            constraints = []
            constraints.extend(TeamVenueConstraint.objects.filter(team__in=teams))
            constraints.extend(AdjudicatorVenueConstraint.objects.filter(adjudicator__in=adjudicators))
            constraints.extend(InstitutionVenueConstraint.objects.filter(institution__team__in=teams))
            if debate.division is not None:
                constraints.extend(debate.division.divisionvenueconstraint_set.all())

            if len(constraints) > 0:
                constraints.sort(key=lambda x: x.priority, reverse=True)
                debate_constraints.append((debate, constraints))
                logger.info("Constraints on {}: {}".format(debate, constraints))

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
            eligible_venues = set(highest_constraint.venue_group.venues) & set(self._all_venues)

            # If we can't fulfil the highest constraint, bump it down the list.
            if len(eligible_venues) == 0:
                logger.debug("Unfilfilled (highest): {}".format(highest_constraint))
                if len(constraints) == 0:
                    logger.debug("{} is now unconstrained".format(debate))
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
                    continue  # Skip if we've already done a constraint for this team/adj/inst/div
                constraint_venues = set(constraint.venue_group.venues)
                if eligible_venues.isdisjoint(constraint_venues):
                    logger.debug("Unfilfilled: {}".format(constraint))
                else:
                    eligible_venues &= constraint_venues
                    satisified_constraints.append(constraint)

            # If no eligible venues are preferred venues, drop the last preferred venue.
            preferred_venues = set(self._preferred_venues)
            if eligible_venues.isdisjoint(preferred_venues):
                logger.debug("No preferred venues available: {}".format(debate))
                self._preferred_venues = self._preferred_venues[:-1]
            else:
                eligible_venues &= preferred_venues

            # Finally, assign the venue.
            venue = random.choice(list(eligible_venues))
            debate_venues[debate] = venue
            self._all_venues.remove(venue)
            if venue in self._preferred_venues:
                self._preferred_venues.remove(venue)
            logger.debug("Assigning {} to {}".format(venue, debate))

        return debate_venues

    def allocate_unconstrained_venues(self, debates):
        """Allocates unconstrained venues by randomly shuffling the remaining
        preferred venues."""

        if len(self._preferred_venues) != len(debates):
            logger.critical("preferred venues to unconstrained debates mismatch: "
                "%s preferred venues, %d debates", len(self._preferred_venues), len(debates))
            # we'll still keep going, since zip() stops at the end of the shorter list

        random.shuffle(debates)
        return {debate: venue for debate, venue in zip(debates, self._preferred_venues)}

    def save_venues(self, debate_venues):
        for debate, venue in debate_venues.items():
            logger.debug("Saving {} for {}".format(venue, debate))
            debate.venue = venue
            debate.save()
