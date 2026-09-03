import json
import logging
from dataclasses import asdict
from email.utils import formataddr
from typing import Any, Dict, List, Type, Union

from channels.consumer import SyncConsumer
from django.core import mail
from django.template import Context, Template
from html2text import html2text

from draw.models import Debate
from participants.models import Person
from tournaments.models import Round, Tournament

from .email_tracking import build_hook_id, send_tracked_emails, tournament_from_email
from .models import BulkNotification, EmailStatus, SentMessage
from .utils import (AdjudicatorAssignmentEmailGenerator, BallotsEmailGenerator, InstitutionCustomEmailGenerator,
                    InstitutionRegistrationEmailGenerator, MotionReleaseEmailGenerator, NotificationContextGenerator,
                    RandomizedUrlEmailGenerator, SlotsAllocatedEmailGenerator, StandingsEmailGenerator,
                    TeamDrawEmailGenerator, TeamSpeakerEmailGenerator)

logger = logging.getLogger(__name__)


class NotificationQueueConsumer(SyncConsumer):

    NOTIFICATION_GENERATORS: Dict[BulkNotification.EventType, Type[NotificationContextGenerator]] = {
        BulkNotification.EventType.ADJ_DRAW: AdjudicatorAssignmentEmailGenerator,
        BulkNotification.EventType.URL: RandomizedUrlEmailGenerator,
        BulkNotification.EventType.BALLOTS_CONFIRMED: BallotsEmailGenerator,
        BulkNotification.EventType.POINTS: StandingsEmailGenerator,
        BulkNotification.EventType.MOTIONS: MotionReleaseEmailGenerator,
        BulkNotification.EventType.TEAM_REG: TeamSpeakerEmailGenerator,
        BulkNotification.EventType.TEAM_DRAW: TeamDrawEmailGenerator,
        BulkNotification.EventType.INSTITUTION_REG: InstitutionRegistrationEmailGenerator,
        BulkNotification.EventType.SLOTS_ALLOCATED: SlotsAllocatedEmailGenerator,
        BulkNotification.EventType.INSTITUTION_CUSTOM: InstitutionCustomEmailGenerator,
        BulkNotification.EventType.CUSTOM: NotificationContextGenerator,
    }

    def email(self, event: Dict[str, Union[str, BulkNotification.EventType, List[int], Dict[str, Any]]]) -> None:
        # Get database objects
        if 'debate_id' in event['extra']:
            debate = Debate.objects.select_related('round__tournament').get(pk=event['extra'].pop('debate_id'))
            event['extra']['debate'] = debate
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

        from_email, reply_to = tournament_from_email(t)
        notification_type = event['message']

        subject = Template(event['subject'])
        html_body = Template(event['body'])

        recipients = Person.objects.filter(pk__in=event['send_to'] or [], email__isnull=False).exclude(email='')
        contexts = self.NOTIFICATION_GENERATORS[notification_type].generate(to=recipients, **event['extra'])

        # Prepare messages

        # Ballot receipts are grouped by round in the same BulkNotification
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
        for instance, recipient in contexts:
            hook_id = build_hook_id(bulk_notification.id, recipient.id)
            data = None
            try:
                data = asdict(instance)
                data['USER'] = recipient.name

                context = Context(data)
                body = html_body.render(context)
                email = mail.EmailMultiAlternatives(
                    subject=subject.render(context), body=html2text(body),
                    from_email=from_email, to=[formataddr((recipient.name.strip(), recipient.email))],
                    reply_to=reply_to, headers={
                        'X-SMTPAPI': json.dumps({'unique_args': {'hook-id': hook_id}}),  # SendGrid-specific 'hook-id'
                    },
                )
                email.attach_alternative(body, "text/html")
                raw_message = email.message()
            except Exception as e:
                logger.warning("Failed to prepare email for recipient %s", recipient.id, exc_info=True)
                failed_record = SentMessage.objects.create(
                    recipient=recipient, email=recipient.email, method=SentMessage.METHOD_TYPE_EMAIL,
                    context=data, hook_id=hook_id, notification=bulk_notification,
                )
                EmailStatus.objects.create(
                    email=failed_record, event=EmailStatus.EventType.FAILED, data={'error': str(e)},
                )
                continue

            messages.append(email)
            records.append(
                SentMessage(recipient=recipient, email=recipient.email,
                            method=SentMessage.METHOD_TYPE_EMAIL,
                            context=data, message_id=raw_message['Message-ID'],
                            hook_id=hook_id, notification=bulk_notification))

        send_tracked_emails(messages, records)
