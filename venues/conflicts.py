
def  _constraints_satisfied(constraints, venue):
    """Returns True if either there are no constraints, or one constraint has
    been meet. Returns False otherwise. `constraints` must be a query set."""
    return not constraints.exists() or constraints.filter(venue_group__venue=venue).exists()

def venue_conflicts(debate):
    """Returns a list of unfulfilled venue constraints for a debate.
    A venue constraint is unfulfilled if, for a given participant, *none* of its
    constraints were met.

    This function hits the database twice for each team and once for each adjudicator."""

    conflicts = []
    venue = debate.venue

    for team in debate.teams:
        constraints = team.teamvenueconstraint_set
        if not _constraints_satisfied(constraints, venue):
            conflicts.append("Venue does not meet constraints of team {}".format(team.short_name))
        constraints = team.institution.institutionvenueconstraint_set
        if not _constraints_satisfied(constraints, venue):
            conflicts.append("Venue does not meet constraints of institution {} ({})".format(team.institution.code, team.short_name))

    for _, adjudicator in debate.adjudicators:
        constraints = adjudicator.adjudicatorvenueconstraint_set
        if not _constraints_satisfied(constraints, venue):
            conflicts.append("Venue does not meet constraints of adjudicator {}".format(adjudicator.name))

    return conflicts
