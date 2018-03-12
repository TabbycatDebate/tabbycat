import datetime
import logging
import random
import string

from django.db import IntegrityError

from .models import DebateIdentifier, Event, PersonIdentifier, VenueIdentifier

logger = logging.getLogger(__name__)


def generate_identifier(length=6):
    """Generates a random identifier and saves it to the database."""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.SystemRandom().choice(chars) for _ in range(length))


IDENTIFIER_CLASSES = {
    'participants.Person': PersonIdentifier,
    'draw.Debate': DebateIdentifier,
    'venues.Venue': VenueIdentifier,
}


def generate_identifiers(queryset, length=6, num_attempts=10):
    """Generates identifiers for every instance in the given QuerySet."""
    klass = IDENTIFIER_CLASSES[queryset.model._meta.label]
    attr = klass.instance_attr

    for instance in queryset:
        identifier = generate_identifier(length=length)
        for i in range(num_attempts):
            try:
                klass.objects.create(identifier=identifier, **{attr: instance})
            except IntegrityError:
                logger.warning("Identifier was not unique, trying again (%d of %d", i, num_attempts)
                continue
            else:
                break
        else:
            logger.error("Could not generate unique identifier for %r after %d tries", instance, num_attempts)


def delete_identifiers(queryset):
    klass = IDENTIFIER_CLASSES[queryset.model._meta.label]
    attr = klass.instance_attr
    klass.objects.filter(**{attr + '__in': queryset}).delete()


def get_unexpired_checkins(tournament):
    start = datetime.timedelta(hours=tournament.pref('checkin_window'))
    time_window = datetime.datetime.now() - start
    events = Event.objects.filter(tournament=tournament,
                                  time__gte=time_window).select_related('identifier')
    return events
