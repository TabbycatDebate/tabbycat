import logging
import random
import string
from smtplib import SMTPException

from django.core.mail import send_mass_mail
from django.conf import settings
from django.db import IntegrityError

from utils.misc import reverse_tournament

from .models import PrivateUrlSentMailRecord

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
    records = []

    for instance in queryset:
        url_key = url_key_function(instance)
        email = instance.email

        path = reverse_tournament(url_name, tournament, kwargs={'url_key': url_key})
        url = request.build_absolute_uri(path)

        formatted_subject = subject
        formatted_message = message.replace('%name', instance.name).replace('%url', url)
        if hasattr(instance, 'team'):
            formatted_message = formatted_message.replace('%team', instance.team.short_name)

        messages.append((formatted_subject, formatted_message, settings.DEFAULT_FROM_EMAIL, [email]))

        record = PrivateUrlSentMailRecord(email=email, url_key=url_key, url_type=url_type)
        setattr(record, record_attrname, instance)
        records.append(record)

    try:
        send_mass_mail(messages, fail_silently=False)
    except SMTPException:
        logger.exception("Failed to send randomised URL e-mails")
        raise
    except ConnectionError:
        logger.exception("Connection error sending randomised URL e-mails")
        raise
    else:
        logger.info("Sent %d randomised URL e-mails", len(messages))
        PrivateUrlSentMailRecord.objects.bulk_create(records)

    return len(messages)
