from email.utils import formataddr
from time import time
from typing import List, Optional, Tuple

from django.conf import settings
from django.core import mail

from tournaments.models import Tournament

from .models import EmailStatus, SentMessage


def tournament_from_email(tournament: Tournament) -> Tuple[str, Optional[List[str]]]:
    from_email = formataddr((tournament.short_name, settings.DEFAULT_FROM_EMAIL))
    if tournament.pref('reply_to_address'):
        return from_email, [formataddr((tournament.pref('reply_to_name').strip(), tournament.pref('reply_to_address')))]
    return from_email, None


def build_hook_id(bulk_notification_id: int, entity_id: int) -> str:
    return str(bulk_notification_id) + "-" + str(entity_id) + "-" + str(int(time()))[4:]


def send_tracked_emails(messages: List[mail.EmailMultiAlternatives], records: List[SentMessage]) -> None:
    SentMessage.objects.bulk_create(records)
    if not messages:
        return

    connection = mail.get_connection(fail_silently=False)
    failed_events = []

    connection.open()
    for message, record in zip(messages, records):
        try:
            message.extra_headers['X-RECORDID'] = record.id
            connection.send_messages([message])
        except Exception as e:
            failed_events.append(EmailStatus(email=record, event=EmailStatus.EventType.FAILED, data={'error': str(e)}))
    connection.close()

    EmailStatus.objects.bulk_create(failed_events)
