import json
import random
from dataclasses import asdict
from email.utils import formataddr
from typing import Any, Callable, Dict, List, Optional, Tuple, TYPE_CHECKING, Union

from channels.consumer import SyncConsumer
from django.conf import settings
from django.core import mail
from django.template import Context, Template
from html2text import html2text

from draw.models import Debate
from participants.models import Person
from tournaments.models import Round, Tournament

from .models import BulkNotification, SentMessage
from .utils import (adjudicator_assignment_email_generator, ballots_email_generator, EmailContextData,
                    motion_release_email_generator, randomized_url_email_generator,
                    standings_email_generator, team_draw_email_generator, team_speaker_email_generator)

if TYPE_CHECKING:
    from django.db.models import QuerySet, Model


class NotificationQueueConsumer(SyncConsumer):

    NOTIFICATION_GENERATORS: Dict[BulkNotification.EventType, Union[
        Callable[['QuerySet[Person]', str, 'Model'], List[Tuple[EmailContextData, Person]]],
        Callable[['QuerySet[Person]', 'Model'], List[Tuple[EmailContextData, Person]]],
    ]]
    NOTIFICATION_GENERATORS = {
        BulkNotification.EventType.ADJ_DRAW: adjudicator_assignment_email_generator,
        BulkNotification.EventType.URL: randomized_url_email_generator,
        BulkNotification.EventType.BALLOTS_CONFIRMED: ballots_email_generator,
        BulkNotification.EventType.POINTS: standings_email_generator,
        BulkNotification.EventType.MOTIONS: motion_release_email_generator,
        BulkNotification.EventType.TEAM_REG: team_speaker_email_generator,
        BulkNotification.EventType.TEAM_DRAW: team_draw_email_generator,
    }

    def _send(self, event, messages, records) -> None:
        mail.get_connection().send_messages(messages)
        SentMessage.objects.bulk_create(records)

    def _get_from_fields(self, t: Tournament) -> Tuple[str, Optional[List[str]]]:
        from_email = formataddr((t.short_name, settings.DEFAULT_FROM_EMAIL))
        if t.pref('reply_to_address'):
            return from_email, [formataddr((t.pref('reply_to_name'), t.pref('reply_to_address')))]
        return from_email, None  # Shouldn't have array of None

    def email(self, event: Dict[str, Union[str, BulkNotification.EventType, List[int], Dict[str, Any]]]) -> None:
        # Get database objects
        if 'debate_id' in event['extra']:
            event['extra']['debate'] = Debate.objects.select_related('round', 'round__tournament').get(pk=event['extra'].pop('debate_id'))
            round = event['extra']['debate'].round
            t = round.tournament
        elif 'round_id' in event['extra']:
            round = Round.objects.select_related('tournament').get(pk=event['extra'].pop('round_id'))
            event['extra']['round'] = round
            t = round.tournament
        else:
            round = None
            t = Tournament.objects.get(pk=event['extra'].pop('tournament_id'))
            event['extra']['tournament'] = t

        from_email, reply_to = self._get_from_fields(t)
        notification_type = event['message']

        subject = Template(event['subject'])
        html_body = Template(event['body'])

        recipients = Person.objects.filter(pk__in=event['send_to'] or [], email__isnull=False).exclude(email='')
        data = self.NOTIFICATION_GENERATORS[notification_type](to=recipients, **event['extra'])

        # Prepare messages

        # Ballot receipts are grouped by round in the same BulkNotification
        bulk_notification = BulkNotification.objects.none()
        creation_kwargs = {
            'round': round,
            'tournament': t,
            'subject_template': event['subject'],
            'body_template': event['body'],
        }
        if notification_type is BulkNotification.EventType.BALLOTS_CONFIRMED:
            bulk_notification, c = BulkNotification.objects.get_or_create(
                event=BulkNotification.EventType.BALLOTS_CONFIRMED, **creation_kwargs)
        else:
            bulk_notification = BulkNotification.objects.create(event=notification_type, **creation_kwargs)

        messages = []
        records = []
        for instance, recipient in data:
            instance = asdict(instance)

            hook_id = str(bulk_notification.id) + "-" + str(recipient.id) + "-" + str(random.randint(1000, 9999))
            context = Context(instance)
            body = html_body.render(context)
            email = mail.EmailMultiAlternatives(
                subject=subject.render(context), body=html2text(body),
                from_email=from_email, to=[formataddr((recipient.name, recipient.email))],
                reply_to=reply_to, headers={
                    'X-SMTPAPI': json.dumps({'unique_args': {'hook-id': hook_id}}),  # SendGrid-specific 'hook-id'
                },
            )
            email.attach_alternative(body, "text/html")
            messages.append(email)

            raw_message = email.message()
            records.append(
                SentMessage(recipient=recipient, email=recipient.email,
                            method=SentMessage.METHOD_TYPE_EMAIL,
                            context=instance, message_id=raw_message['Message-ID'],
                            hook_id=hook_id, notification=bulk_notification))

        self._send(event, messages, records)

    def email_custom(self, event: Dict[str, Union[str, int, List[Person]]]) -> None:
        messages = []
        records = []

        t = Tournament.objects.get(id=event['tournament'])
        from_email, reply_to = self._get_from_fields(t)

        recipients = Person.objects.filter(pk__in=event['send_to'], email__isnull=False).exclude(email='')

        bulk_notification = BulkNotification.objects.create(tournament=t, subject_template=event['subject'], body_template=event['body'])
        for recipient in recipients:
            hook_id = str(bulk_notification.id) + "-" + str(recipient.pk) + "-" + str(random.randint(1000, 9999))
            email = mail.EmailMultiAlternatives(
                subject=event['subject'], body=html2text(event['body']),
                from_email=from_email, to=[formataddr((recipient.name, recipient.email))],
                reply_to=reply_to, headers={
                    'X-SMTPAPI': json.dumps({'unique_args': {'hook-id': hook_id}}),  # SendGrid-specific 'hook-id'
                },
            )
            email.attach_alternative(event['body'], "text/html")
            messages.append(email)

            raw_message = email.message()
            records.append(
                SentMessage(recipient=recipient, email=recipient.email,
                            method=SentMessage.METHOD_TYPE_EMAIL,
                            message_id=raw_message['Message-ID'], hook_id=hook_id,
                            notification=bulk_notification))

        self._send(event, messages, records)
