import logging
import random
import string
from smtplib import SMTPException

from django.core.mail import get_connection
from django.db import IntegrityError
from django.template import Context

from notifications.models import MessageSentRecord
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


def send_randomised_url_emails(request, tournament, queryset, url_name, url_key_function,
        record_attrname, url_type, subject, message):

    messages = []

    for instance in queryset:
        url_key = url_key_function(instance)
        path = reverse_tournament(url_name, tournament, kwargs={'url_key': url_key})
        url = request.build_absolute_uri(path)

        variables = {'NAME': instance.name, 'URL': url}
        if hasattr(instance, 'team'):
            variables['TEAM'] = instance.team.short_name

        formatted_message = message.render(Context(variables))
        formatted_subject = subject.render(Context(variables))
        messages.append(TournamentEmailMessage(formatted_subject, formatted_message, tournament, None, url_type, instance))

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
        MessageSentRecord.objects.bulk_create([message.as_sent_record() for message in messages])

    return len(messages)
