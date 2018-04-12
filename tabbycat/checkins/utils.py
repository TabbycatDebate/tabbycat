import datetime
import logging
import random
import string

from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext as _

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


def get_unexpired_checkins(tournament, window_preference):
    if not window_preference:
        time_window = datetime.datetime.fromtimestamp(0)  # Unix start
    else:
        start = datetime.timedelta(hours=tournament.pref(window_preference))
        time_window = datetime.datetime.now() - start

    events = Event.objects.filter(tournament=tournament,
        time__gte=time_window).select_related('identifier').order_by('time')
    return events


def create_identifiers(model_to_make, items_to_check):
    kind = model_to_make.instance_attr
    for item in list(items_to_check):
        try:
            model_to_make.objects.get(**{kind: item})
        except ObjectDoesNotExist:
            model_to_make.objects.create(**{kind: item})
    return


def single_checkin(instance, events):
    instance.checked_icon = ''
    instance.checked_in = False
    try:
        identifier = instance.checkin_identifier
        instance.checked_tooltip = _('Not checked-in (barcode %s)') % identifier.barcode
    except ObjectDoesNotExist:
        identifier = None
        instance.checked_tooltip = _('Not checked-in; no barcode assigned')

    if identifier:
        instance.time = next((e['time'] for e in events if e['identifier__barcode'] == identifier.barcode), None)
        if instance.time:
            instance.checked_in = True
            instance.checked_icon = 'check'
            instance.checked_tooltip = _('Checked-in at %s') % instance.time.strftime('%H:%M')
    return instance


def multi_checkin(team, events, t):
    team.checked_icon = ''
    team.checked_in = False
    team.checked_tooltip = ''

    for speaker in team.speaker_set.all():
        speaker = single_checkin(speaker, events)
        if speaker.checked_in:
            team.checked_tooltip += _("%s checked-in at %s. ") % (speaker.name, speaker.time.strftime('%H:%M'))
        else:
            team.checked_tooltip += _("%s is missing. ") % speaker.name

    check_ins = sum(s.checked_in for s in team.speaker_set.all())
    substantives = t.pref('substantive_speakers')
    if check_ins >= substantives:
        team.checked_in = True
        team.checked_icon = 'check'
    elif check_ins == substantives - 1:
        team.checked_in = True
        team.checked_icon = 'shuffle'

    return team


def get_checkins(queryset, t, window_preference):
    events = get_unexpired_checkins(t, window_preference).values('time', 'identifier__barcode')
    for instance in queryset:
        if hasattr(instance, 'use_institution_prefix'):
            instance = multi_checkin(instance, events, t)
        else:
            instance = single_checkin(instance, events)

    return queryset
