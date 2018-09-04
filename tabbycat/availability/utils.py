import logging

from django.contrib.contenttypes.models import ContentType
from django.db.models import Prefetch

from availability.models import RoundAvailability
from participants.models import Adjudicator, Team
from venues.models import Venue

logger = logging.getLogger(__name__)


def annotate_availability(queryset, round):
    """Annotates each instance the queryset with attribute:
        'available', True if there is a RoundAvailability for the instance in the given round,
    and if `round.prev` exists:
        'prev_available', True if there is a RoundAvailability for the instance in the previous round.
    """

    queryset = queryset.prefetch_related(Prefetch('round_availabilities',
            queryset=RoundAvailability.objects.filter(round=round), to_attr='availability'))
    if round.prev:
        queryset = queryset.prefetch_related(Prefetch('round_availabilities',
                queryset=RoundAvailability.objects.filter(round=round.prev), to_attr='prev_availability'))

    for instance in queryset:
        instance.available = len(instance.availability) > 0
        if round.prev:
            instance.prev_available = len(instance.prev_availability) > 0

    return queryset


def set_availability(queryset, round):
    """Sets the availabilities for the given round to those instances in the
    queryset."""
    ids = [x['id'] for x in queryset.values('id')]
    set_availability_by_id(queryset.model, ids, round)


def set_availability_by_id(model, ids, round):
    """Sets the availabilities for the given round to those IDs in the given list `ids`,
    those being ids of the model (e.g. Adjudicator)."""

    if model not in [Adjudicator, Team, Venue]:
        logger.error("Bad model in set_availability_by_id: %s", model.__class__.__name__, stack_info=True)
        return  # do nothing

    contenttype = ContentType.objects.get_for_model(model)

    ids = set(map(int, ids))
    existing = set(a['object_id'] for a in
        RoundAvailability.objects.filter(
            content_type=contenttype, round=round).values('object_id'))
    logger.debug("%s IDs to set: %s", model._meta.verbose_name.title(), ids)
    logger.debug("Existing %s IDs: %s", model._meta.verbose_name, existing)

    # Delete existing availabilities that should no longer be set
    delete = existing.difference(ids)
    logger.debug("%s IDs to delete: %s", model._meta.verbose_name.title(), delete)
    RoundAvailability.objects.filter(content_type=contenttype, round=round, object_id__in=delete).delete()

    # Add new availabilities
    new = ids.difference(existing)
    logger.debug("%s IDs to create: %s", model._meta.verbose_name.title(), new)
    RoundAvailability.objects.bulk_create([RoundAvailability(content_type=contenttype, round=round, object_id=id) for id in new])


def activate_all(round):
    set_availability(round.tournament.team_set, round)
    set_availability(round.tournament.relevant_adjudicators, round)
    set_availability(round.tournament.relevant_venues, round)
