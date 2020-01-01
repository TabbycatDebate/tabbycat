import json
from smtplib import SMTPException
import random

from channels.consumer import SyncConsumer
from django.conf import settings
from django.core import mail
from django.template import Context, Template
from django.utils.translation import gettext_lazy as _
from html2text import html2text

from draw.models import Debate
from tournaments.models import Round, Tournament

from .models import BulkNotification, SentMessage
from .utils import (adjudicator_assignment_email_generator, ballots_email_generator,
                    motion_release_email_generator, randomized_url_email_generator,
                    standings_email_generator, team_draw_email_generator, team_speaker_email_generator)


class NotificationQueueConsumer(SyncConsumer):

    NOTIFICATION_GENERATORS = {
        BulkNotification.EVENT_TYPE_ADJ_DRAW: adjudicator_assignment_email_generator,
        BulkNotification.EVENT_TYPE_URL: randomized_url_email_generator,
        BulkNotification.EVENT_TYPE_BALLOT_CONFIRMED: ballots_email_generator,
        BulkNotification.EVENT_TYPE_POINTS: standings_email_generator,
        BulkNotification.EVENT_TYPE_MOTIONS: motion_release_email_generator,
        BulkNotification.EVENT_TYPE_TEAM_REG: team_speaker_email_generator,
        BulkNotification.EVENT_TYPE_TEAM_DRAW: team_draw_email_generator
    }

    def _send(self, event, messages, records):
        try:
            mail.get_connection().send_messages(messages)
        except SMTPException as e:
            self.send_error(e, _("Failed to send e-mails."), event)
            raise
        except ConnectionError as e:
            self.send_error(e, _("Connection error sending e-mails."), event)
            raise
        else:
            SentMessage.objects.bulk_create(records)

    def _get_from_fields(self, t):
        from_email = "%s <%s>" % (t.short_name, settings.DEFAULT_FROM_EMAIL)
        reply_to = None
        if t.pref('reply_to_address'):
            reply_to = "%s <%s>" % (t.pref('reply_to_name'), t.pref('reply_to_address'))

            return from_email, [reply_to] # Django wants the reply_to as an array
        return from_email, reply_to # Shouldn't have array of None

    def email(self, event):
        # Get database objects
        if 'debate_id' in event['extra']:
            round = Debate.objects.get(pk=event['extra']['debate_id']).round
            t = round.tournament
        elif 'round_id' in event['extra']:
            round = Round.objects.get(pk=event['extra']['round_id'])
            t = round.tournament
        else:
            round = None
            t = Tournament.objects.get(pk=event['extra']['tournament_id'])

        from_email, reply_to = self._get_from_fields(t)
        notification_type = event['message']

        subject = Template(event['subject'])
        html_body = Template(event['body'])

        data = self.NOTIFICATION_GENERATORS[notification_type](to=event['send_to'], **event['extra'])

        # Prepare messages

        # Ballot receipts are grouped by round in the same BulkNotification
        bulk_notification = BulkNotification.objects.none()
        if notification_type is BulkNotification.EVENT_TYPE_BALLOT_CONFIRMED:
            bulk_notification, c = BulkNotification.objects.get_or_create(event=BulkNotification.EVENT_TYPE_BALLOT_CONFIRMED, round=round, tournament=t)
        else:
            bulk_notification = BulkNotification.objects.create(event=notification_type, round=round, tournament=t)

        messages = []
        records = []
        for instance, recipient in data:
            hook_id = str(bulk_notification.id) + "-" + str(recipient.id) + "-" + str(random.randint(1000,9999))
            recipient_to = "%s <%s>" % (recipient.name, recipient.email)
            context = Context(instance)
            body = html_body.render(context)
            email = mail.EmailMultiAlternatives(
                subject=subject.render(context), body=html2text(body),
                from_email=from_email, to=[recipient_to], reply_to=reply_to,
                headers={'X-SMTPAPI': json.dumps({'unique_args': {'hook-id': hook_id}})} # SendGrid-specific 'hook-id'
            )
            email.attach_alternative(body, "text/html")
            messages.append(email)

            raw_message = email.message()
            records.append(
                SentMessage(recipient=recipient, email=recipient.email,
                            method=SentMessage.METHOD_TYPE_EMAIL,
                            context=instance, message=raw_message,
                            message_id=raw_message['Message-ID'], hook_id=hook_id,
                            notification=bulk_notification)
            )

        self._send(event, messages, records)

    def email_custom(self, event):
        messages = []
        records = []

        t = Tournament.objects.get(id=event['tournament'])
        from_email, reply_to = self._get_from_fields(t)

        bulk_notification = BulkNotification.objects.create(tournament=t)
        for pk, address in event['send_to']:
            hook_id = str(bulk_notification.id) + "-" + str(pk) + "-" + str(random.randint(1000,9999))
            email = mail.EmailMultiAlternatives(
                subject=event['subject'], body=html2text(event['body']),
                from_email=from_email, to=[address], reply_to=reply_to,
                headers={'X-SMTPAPI': json.dumps({'unique_args': {'hook-id': hook_id}})} # SendGrid-specific 'hook-id'
            )
            email.attach_alternative(event['body'], "text/html")
            messages.append(email)

            raw_message = email.message()
            records.append(
                SentMessage(recipient_id=pk, email=address,
                            method=SentMessage.METHOD_TYPE_EMAIL,
                            tournament=t, messsage=raw_message,
                            message_id=raw_message['Message-ID'], hook_id=hook_id,
                            notification=bulk_notification)
            )

        self._send(event, messages, records)
