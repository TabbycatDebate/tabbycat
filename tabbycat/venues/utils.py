from django.contrib.contenttypes.models import ContentType

from venues.models import VenueConstraint


def venue_conflicts_display(debates):
    """Returns a dict mapping elements (debates) in `debates` to a list of
    strings of explaining unfulfilled venue constraints for participants that
    debate. A venue constraint (or more precisely, a set of venue constraints
    relating to a single participant) is "unfulfilled" if the relevant
    participant had constraints and *none* of their constraints were met."""

    constraints = {}
    for vc in VenueConstraint.objects.filter_for_debates(debates).select_related('category'):
        constraints.setdefault((vc.subject_content_type_id, vc.subject_id), []).append(vc)

    def _add_constraint_message(debate, instance_name, instance, venue):
        key = (ContentType.objects.get_for_model(instance).id, instance.id)
        if key not in constraints:
            return
        for constraint in constraints[key]:
            if constraint.category in venue.venueconstraintcategory_set.all():
                conflict_messages[debate].append(("success", "Venue constraint of {name} ({category}) met".format(
                        name=instance_name, category=constraint.category.name)))
                return
        else:
            conflict_messages[debate].append(("danger", "Venue does not meet any constraint of {name}".format(
                    name=instance_name)))

    conflict_messages = {debate: [] for debate in debates}
    for debate in debates:
        venue = debate.venue
        if venue is None:
            continue

        for team in debate.teams:
            _add_constraint_message(debate, team.short_name, team, venue)
            _add_constraint_message(debate, "institution {} ({})".format(team.institution.code, team.short_name),
                    team.institution, venue)


            # if not _constraints_satisfied(team, venue):
            #     conflict_messages[debate].append("Venue does not meet constraints of {}".format(team.short_name))
            # if not _constraints_satisfied(team.institution, venue):
            #     conflict_messages[debate].append("Venue does not meet constraints of institution {} ({})".format(team.institution.code, team.short_name))

        for adjudicator in debate.adjudicators.all():
            _add_constraint_message(debate, adjudicator.name, adjudicator, venue)
            # if not _constraints_satisfied(adjudicator, venue):
                # conflict_messages[debate].append("Venue does not meet constraints of {}".format(adjudicator.name))

    return conflict_messages
