import json
import logging
from email.utils import formataddr
from time import sleep, time
from typing import List, Optional, Tuple

from anymail.exceptions import AnymailAPIError
from django.conf import settings
from django.core import mail

from tournaments.models import Tournament

from .models import EmailStatus, SentMessage

logger = logging.getLogger(__name__)

# Seconds to wait before retrying a send that the email provider rate-limited
RATE_LIMIT_RETRY_DELAYS = (1, 2, 4)

# Statuses from AnymailStatus that mean the provider won't send the message
REFUSED_SEND_STATUSES = {'invalid', 'rejected', 'failed'}

# Normalized Anymail tracking event types, mapped to the statuses we record.
# Event types not listed here (e.g. 'autoresponded', 'unknown') are ignored.
ANYMAIL_EVENT_TYPES = {
    'queued': EmailStatus.EventType.PROCESSED,
    'sent': EmailStatus.EventType.PROCESSED,
    'rejected': EmailStatus.EventType.DROPPED,
    'failed': EmailStatus.EventType.FAILED,
    'bounced': EmailStatus.EventType.BOUNCED,
    'deferred': EmailStatus.EventType.DEFERRED,
    'delivered': EmailStatus.EventType.DELIVERED,
    'opened': EmailStatus.EventType.OPENED,
    'clicked': EmailStatus.EventType.CLICKED,
    'complained': EmailStatus.EventType.SPAM,
    'unsubscribed': EmailStatus.EventType.UNSUBSCRIBED,
}


def tournament_from_email(tournament: Tournament) -> Tuple[str, Optional[List[str]]]:
    from_email = formataddr((tournament.short_name, settings.DEFAULT_FROM_EMAIL))
    if tournament.pref('reply_to_address'):
        return from_email, [formataddr((tournament.pref('reply_to_name').strip(), tournament.pref('reply_to_address')))]
    return from_email, None


def build_hook_id(bulk_notification_id: int, entity_id: int) -> str:
    return str(bulk_notification_id) + "-" + str(entity_id) + "-" + str(int(time()))[4:]


def uses_anymail() -> bool:
    return settings.EMAIL_BACKEND.startswith('anymail.')


def add_hook_id(message: mail.EmailMultiAlternatives, hook_id: Optional[str]) -> None:
    if hook_id is None:
        return
    if uses_anymail():
        # Anymail passes metadata to the provider, which returns it in tracking events
        message.metadata = {'hook_id': hook_id}
    else:
        message.extra_headers['X-SMTPAPI'] = json.dumps({'unique_args': {'hook-id': hook_id}})  # SendGrid-specific 'hook-id'


def send_with_retry(connection, message: mail.EmailMultiAlternatives) -> None:
    for delay in RATE_LIMIT_RETRY_DELAYS:
        try:
            connection.send_messages([message])
            return
        except AnymailAPIError as e:
            if e.status_code != 429:
                raise
            logger.info("Email provider rate limit reached, retrying in %d seconds", delay)
            sleep(delay)
    connection.send_messages([message])


def get_esp_message_id(message: mail.EmailMultiAlternatives) -> Optional[str]:
    status = getattr(message, 'anymail_status', None)
    if status is None or status.message_id is None:
        return None
    if isinstance(status.message_id, set):
        # Some providers assign one ID per recipient; we only send to one recipient
        return str(next(iter(status.message_id))) if len(status.message_id) == 1 else None
    return str(status.message_id)


def send_tracked_emails(messages: List[mail.EmailMultiAlternatives], records: List[SentMessage]) -> None:
    SentMessage.objects.bulk_create(records)
    if not messages:
        return

    connection = mail.get_connection(fail_silently=False)
    failed_events = []
    sent_records = []

    connection.open()
    for message, record in zip(messages, records):
        try:
            message.extra_headers['X-RECORDID'] = str(record.id)
            add_hook_id(message, record.hook_id)
            send_with_retry(connection, message)
        except Exception as e:
            failed_events.append(EmailStatus(email=record, event=EmailStatus.EventType.FAILED, data={'error': str(e)}))
            continue

        record.esp_message_id = get_esp_message_id(message)
        if record.esp_message_id is not None:
            sent_records.append(record)

        refused = (getattr(getattr(message, 'anymail_status', None), 'status', None) or set()) & REFUSED_SEND_STATUSES
        if refused:
            failed_events.append(EmailStatus(email=record, event=EmailStatus.EventType.FAILED,
                data={'error': "Refused by email provider: %s" % ", ".join(sorted(refused))}))
    connection.close()

    SentMessage.objects.bulk_update(sent_records, ['esp_message_id'])
    EmailStatus.objects.bulk_create(failed_events)


def record_tracking_event(sender, event, esp_name: str, **kwargs) -> None:
    """Receiver for Anymail's tracking signal, which fires on webhook calls from the email provider."""
    status = ANYMAIL_EVENT_TYPES.get(event.event_type)
    if status is None:
        return

    record = None
    hook_id = (event.metadata or {}).get('hook_id')
    if hook_id:
        record = SentMessage.objects.filter(hook_id=hook_id).first()
    if record is None and event.message_id:
        record = SentMessage.objects.filter(esp_message_id=event.message_id).first()
    if record is None:
        return

    data = {
        'esp': esp_name,
        'event': event.event_type,
        'event_id': event.event_id,
        'timestamp': event.timestamp.isoformat() if event.timestamp else None,
        'recipient': event.recipient,
        'reject_reason': event.reject_reason,
        'description': event.description,
        'mta_response': event.mta_response,
    }
    EmailStatus.objects.create(email=record, event=status,
                               data={key: value for key, value in data.items() if value is not None})
