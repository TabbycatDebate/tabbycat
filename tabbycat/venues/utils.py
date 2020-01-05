from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext as _

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

    def _add_constraint_message(debate, instance, venue, success_message, failure_message, message_args):
        key = (ContentType.objects.get_for_model(instance).id, instance.id)
        if key not in constraints:
            return
        for constraint in constraints[key]:
            if constraint.category in venue.venuecategory_set.all():
                message_args['category'] = constraint.category.name
                conflict_messages[debate].append(("success", success_message % message_args))
                return
        else:
            conflict_messages[debate].append(("danger", failure_message % message_args))

    conflict_messages = {debate: [] for debate in debates}
    for debate in debates:
        venue = debate.venue
        if venue is None:
            continue

        for team in debate.teams:
            _add_constraint_message(debate, team, venue,
                _("Room constraint of %(name)s met (%(category)s)"),
                _("Room does not meet any constraint of %(name)s"),
                {'name': team.short_name})

            if team.institution is not None:
                _add_constraint_message(debate, team.institution, venue,
                    _("Room constraint of %(team)s met (%(category)s, via institution %(institution)s)"),
                    _("Room does not meet any constraint of institution %(institution)s (%(team)s)"),
                    {'institution': team.institution.code, 'team': team.short_name})

        for adjudicator in debate.adjudicators.all():
            _add_constraint_message(debate, adjudicator, venue,
                _("Room constraint of %(name)s met (%(category)s)"),
                _("Room does not meet any constraint of %(name)s"),
                {'name': adjudicator.name})

    return conflict_messages
