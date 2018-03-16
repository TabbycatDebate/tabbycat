import logging

from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError, transaction
from django.db.models import Prefetch
from django.utils.translation import gettext as _

from availability.models import RoundAvailability
from checkins.utils import get_unexpired_checkins
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


def single_checkin(instance, events, value_string):
    instance.checked_icon = ''
    instance.checked_in = False
    instance.checked_tooltip = _('Not checked-in')
    identifier = instance.checkin_identifier
    if identifier:
        instance.time = next((e['time'] for e in events if e['identifier__barcode'] == identifier.barcode), None)
        if instance.time:
            instance.checked_in = True
            instance.checked_icon = 'check'
            instance.checked_tooltip = _('Checked-in at %s') % instance.time.strftime('%H:%M')
    return instance


def multi_checkin(team, events, value_string, substantives):
    team.checked_icon = ''
    team.checked_in = False
    team.checked_tooltip = ''

    for speaker in team.speaker_set.all():
        speaker = single_checkin(speaker, events, value_string)
        if speaker.checked_in:
            team.checked_tooltip += _("%s checked-in at %s. ") % (speaker.name, speaker.time.strftime('%H:%M'))
        else:
            team.checked_tooltip += _("%s is missing. ") % speaker.name

    check_ins = sum(s.checked_in for s in team.speaker_set.all())
    if check_ins >= substantives:
        team.checked_in = True
        team.checked_icon = 'check'
    elif check_ins == substantives - 1:
        team.checked_in = True
        team.checked_icon = 'shuffle'

    return team


def get_checkins(queryset, t, value_string):
    events = get_unexpired_checkins(t).values('time', 'identifier__barcode')
    substantives = t.pref('substantive_speakers')
    for instance in queryset:
        if hasattr(instance, 'use_institution_prefix'):
            instance = multi_checkin(instance, events, value_string, substantives)
        else:
            instance = single_checkin(instance, events, value_string)

    return queryset


def set_availability(queryset, round):
    """Sets the availabilities for the given round to those instances in the
    queryset."""
    ids = [x['id'] for x in queryset.values('id')]
    set_availability_by_id(queryset.model, ids, round)


@transaction.atomic
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

    # By wrapping this block in atomic() it will either all commit or all be
    # rolled back in the case of an error. Note that here we are catching the
    # exception on the presumption that 'bad' data from the front end (i.e. out
    # of sync with database state) should fail but having it fail silently
    # could be an issue
    try:
        with transaction.atomic():
            # Delete existing availabilities that should no longer be set
            delete = existing.difference(ids)
            logger.debug("%s IDs to delete: %s", model._meta.verbose_name.title(), delete)
            RoundAvailability.objects.filter(content_type=contenttype, round=round, object_id__in=delete).delete()

            # Add new availabilities
            new = ids.difference(existing)
            logger.debug("%s IDs to create: %s", model._meta.verbose_name.title(), new)
            RoundAvailability.objects.bulk_create([RoundAvailability(content_type=contenttype, round=round, object_id=id) for id in new])
    except IntegrityError:
        logger.exception("IntegrityError updating round availabilities")


def activate_all(round):
    set_availability(round.tournament.team_set, round)
    set_availability(round.tournament.relevant_adjudicators, round)
    set_availability(round.tournament.relevant_venues, round)
