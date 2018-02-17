import logging
from smtplib import SMTPException

from django.core.mail import send_mass_mail
from django.conf import settings

from utils.misc import reverse_tournament

from .models import PrivateUrlSentMailRecord

logger = logging.getLogger(__name__)


def send_randomised_url_emails(request, tournament, queryset, url_name, url_key_function,
        record_attrname, url_type, subject, message):

    messages = []
    records = []

    for instance in queryset:
        url_key = url_key_function(instance)
        email = instance.email

        path = reverse_tournament(url_name, tournament, kwargs={'url_key': url_key})
        url = request.build_absolute_uri(path)

        formatted_subject = subject % {'tournament': tournament.short_name}
        formatted_message = message % {
            'name': instance.name,
            'tournament': tournament.short_name,
            'team': instance.team.short_name if hasattr(instance, 'team') else None,
            'url': url,
        }

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
