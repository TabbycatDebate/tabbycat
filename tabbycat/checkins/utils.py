import datetime
import logging
import random
import string

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils import timezone
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


def delete_identifiers(queryset):
    klass = IDENTIFIER_CLASSES[queryset.model._meta.label]
    attr = klass.instance_attr
    return klass.objects.filter(**{attr + '__in': queryset}).delete()


def get_unexpired_checkins(tournament, window_preference_type):
    filters = Q(tournament=tournament)
    if window_preference_type:
        start = datetime.timedelta(hours=tournament.pref(window_preference_type))
        time_window = timezone.now() - start
        filters &= Q(time__gte=time_window)

    return Event.objects.filter(filters).select_related('identifier').order_by('time')


def create_identifiers(model_to_make, items_to_check):
    kind = model_to_make.instance_attr
    identifiers_to_make = items_to_check.filter(checkin_identifier__isnull=True)

    for item in identifiers_to_make:
        model_to_make.objects.create(**{kind: item})

    return


def single_checkin(instance, events):
    instance.checked_icon = ''
    instance.checked_in = False
    try:
        identifier = instance.checkin_identifier
        instance.barcode = identifier.barcode
        instance.checked_tooltip = _("Not checked in (barcode %(barcode)s)") % {'barcode': identifier.barcode}
    except ObjectDoesNotExist:
        identifier = None
        instance.barcode = None
        instance.checked_tooltip = _("Not checked in; no barcode assigned")

    if identifier:
        instance.time = next((e['time'] for e in events if e['identifier__barcode'] == identifier.barcode), None)
        if instance.time:
            instance.checked_in = True
            instance.checked_icon = 'check'
            instance.checked_tooltip = _("checked in at %(time)s") % {'time': instance.time.strftime('%H:%M')}
    return instance


def multi_checkin(team, events, t):
    team.checked_icon = ''
    team.checked_in = False
    tooltips = []

    for speaker in team.speaker_set.all():
        speaker = single_checkin(speaker, events)
        if speaker.checked_in:
            tooltip = _("%(speaker)s checked in at %(time)s.") % {'speaker': speaker.name, 'time': speaker.time.strftime('%H:%M')}
        else:
            tooltip = _("%(speaker)s is missing.") % {'speaker': speaker.name}
        tooltips.append(tooltip)

    team.checked_tooltip = " ".join(tooltips)

    check_ins = sum(s.checked_in for s in team.speaker_set.all())
    nsubstantives = t.pref('substantive_speakers')
    if check_ins >= nsubstantives:
        team.checked_in = True
        team.checked_icon = 'check'
    elif check_ins == nsubstantives - 1:
        team.checked_in = True
        team.checked_icon = 'shuffle'

    return team


def get_checkins(queryset, t, window_preference_type):
    events = get_unexpired_checkins(t, window_preference_type).values(
        'time', 'identifier__barcode')
    for instance in queryset:
        if hasattr(instance, 'use_institution_prefix'):
            instance = multi_checkin(instance, events, t)
        else:
            instance = single_checkin(instance, events)

    return queryset
