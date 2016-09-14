from django.contrib.contenttypes.models import ContentType

from participants.models import Adjudicator, Institution, Team
from venues.models import VenueConstraint


def venue_conflicts_display(debates):
    """Returns a dict mapping elements (debates) in `debates` to a list of
    strings of explaining unfulfilled venue constraints for participants that
    debate. A venue constraint (or more precisely, a set of venue constraints
    relating to a single participant) is "unfulfilled" if the relevant
    participant had constraints and *none* of their constraints were met."""

    constraints = {}
    for vc in VenueConstraint.objects.filter_for_debates(debates):
        constraints.setdefault((vc.subject_content_type_id, vc.subject_id), []).append(vc)

    def _constraints_satisfied(instance, venue):
        key = (ContentType.objects.get_for_model(instance).id, instance.id)
        if key not in constraints:
            return True
        return any(constraint.venue_group_id == venue.group_id for constraint in constraints[key])

    conflict_messages = {debate: [] for debate in debates}
    for debate in debates:
        venue = debate.venue
        if venue is None:
            continue

        for team in debate.teams:
            if not _constraints_satisfied(team, venue):
                conflict_messages[debate].append("Venue does not meet constraints of {}".format(team.short_name))
            if not _constraints_satisfied(team.institution, venue):
                conflict_messages[debate].append("Venue does not meet constraints of institution {} ({})".format(team.institution.code, team.short_name))

        for adjudicator in debate.adjudicators.all():
            if not _constraints_satisfied(adjudicator, venue):
                conflict_messages[debate].append("Venue does not meet constraints of {}".format(adjudicator.name))

    return conflict_messages
