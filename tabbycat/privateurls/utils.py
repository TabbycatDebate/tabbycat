import logging
import random
import string
from smtplib import SMTPException

from django.core.mail import get_connection
from django.db import IntegrityError

from notifications.models import SentMessageRecord
from notifications.utils import TournamentEmailMessage
from utils.misc import reverse_tournament


logger = logging.getLogger(__name__)


def generate_url_key(length=8):
    """Generates a randomised URL key."""
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.SystemRandom().choice(chars) for _ in range(length))


def populate_url_keys(queryset, length=8, num_attempts=10):
    """Populates the URL key field for every instance in the given QuerySet."""
    for instance in queryset:
        for i in range(num_attempts):
            instance.url_key = generate_url_key(length)
            try:
                instance.save()
            except IntegrityError:
                logger.warning("URL key was not unique, trying again (%d of %d)", i, num_attempts)
                continue
            else:
                break
        else:
            logger.error("Could not generate unique URL for %r after %d tries", instance, num_attempts)


def delete_url_keys(queryset):
    """Deletes URL keys from every instance in the given QuerySet."""
    queryset.update(url_key=None)


def send_randomised_url_emails(request, tournament, participants, subject, message):

    messages = []

    for instance in participants:
        path = reverse_tournament('privateurls-person-index', tournament, kwargs={'url_key': instance.url_key})
        url = request.build_absolute_uri(path)

        variables = {'NAME': instance.name, 'URL': url, 'key': instance.url_key, 'TOURN': str(tournament)}

        messages.append(TournamentEmailMessage(subject, message, tournament, None, SentMessageRecord.EVENT_TYPE_URL, instance, variables))
    try:
        get_connection().send_messages(messages)
    except SMTPException:
        logger.exception("Failed to send randomised URL e-mails")
        raise
    except ConnectionError:
        logger.exception("Connection error sending randomised URL e-mails")
        raise
    else:
        logger.info("Sent %d randomised URL e-mails", len(messages))
        SentMessageRecord.objects.bulk_create([message.as_sent_record() for message in messages])

    return len(messages)
