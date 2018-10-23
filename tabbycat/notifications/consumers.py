from smtplib import SMTPException

from channels.consumer import SyncConsumer
from django.conf import settings
from django.core import mail
from django.template import Context, Template
from django.utils.translation import gettext_lazy as _

from draw.models import Debate
from tournaments.models import Round, Tournament

from .models import BulkNotification, SentMessageRecord
from .utils import (adjudicator_assignment_email_generator, ballots_email_generator,
                    motion_release_email_generator, randomized_url_email_generator,
                    standings_email_generator, team_speaker_email_generator)


class NotificationQueueConsumer(SyncConsumer):

    NOTIFICATION_GENERATORS = {
        BulkNotification.EVENT_TYPE_DRAW: adjudicator_assignment_email_generator,
        BulkNotification.EVENT_TYPE_URL: randomized_url_email_generator,
        BulkNotification.EVENT_TYPE_BALLOT_CONFIRMED: ballots_email_generator,
        BulkNotification.EVENT_TYPE_POINTS: standings_email_generator,
        BulkNotification.EVENT_TYPE_MOTIONS: motion_release_email_generator,
        BulkNotification.EVENT_TYPE_TEAM: team_speaker_email_generator
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
            SentMessageRecord.objects.bulk_create(records)

    def _get_from_fields(self, t):
        from_email = "%s <%s>" % (t.short_name, settings.DEFAULT_FROM_EMAIL)
        reply_to = None
        if t.pref('reply_to_address'):
            reply_to = "%s <%s>" % (t.pref('reply_to_name'), t.pref('reply_to_address'))

        # Django wants the reply_to as an array
        return from_email, [reply_to]

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
        body = Template(event['body'])

        data = self.NOTIFICATION_GENERATORS[notification_type](to=event['send_to'], **event['extra'])

        # Prepare messages
        bulk_notification = BulkNotification.objects.create(event=notification_type, round=round, tournament=t)
        messages = []
        records = []
        for instance, recipient in data:
            context = Context(instance)
            email = mail.EmailMessage(
                subject=subject.render(context), body=body.render(context),
                from_email=from_email, to=[recipient.email], reply_to=reply_to
            )
            raw_message = email.message()
            messages.append(email)
            records.append(
                SentMessageRecord(recipient=recipient, email=recipient.email,
                                  method=SentMessageRecord.METHOD_TYPE_EMAIL,
                                  context=instance, message=raw_message,
                                  message_id=raw_message['Message-ID'],
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
            email = mail.EmailMessage(
                subject=event['subject'], body=event['message'],
                from_email=from_email, to=[address], reply_to=reply_to
            )
            raw_message = email.message()
            messages.append(email)
            records.append(
                SentMessageRecord(
                    recipient_id=pk, email=address,
                    method=SentMessageRecord.METHOD_TYPE_EMAIL,
                    tournament=t, messsage=raw_message,
                    message_id=raw_message['Message-ID'],
                    notification=bulk_notification)
            )

        self._send(event, messages, records)
