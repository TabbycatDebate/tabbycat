from smtplib import SMTPException

from asgiref.sync import async_to_sync

from django.conf import settings
from django.core import mail
from django.template import Context, Template
from django.utils.translation import gettext_lazy as _

from tournaments.models import Round
from utils.consumers import TournamentConsumer, WSPublicAccessMixin

from .models import SentMessageRecord
from .utils import (adjudicator_assignment_email_generator, ballots_email_generator,
                    motion_release_email_generator, randomized_url_email_generator, standings_email_generator)


class NotificationQueueConsumer(TournamentConsumer, WSPublicAccessMixin):

    group_prefix = 'notifications'

    NOTIFICATION_GENERATORS = {
        "adj": adjudicator_assignment_email_generator,
        "url": randomized_url_email_generator,
        "ballot": ballots_email_generator,
        "team_points": standings_email_generator,
        "motion": motion_release_email_generator
    }
    NOTIFICATION_EVENTS = {
        "adj": SentMessageRecord.EVENT_TYPE_DRAW,
        "url": SentMessageRecord.EVENT_TYPE_URL,
        "ballot": SentMessageRecord.EVENT_TYPE_BALLOT_CONFIRMED,
        "team_points": SentMessageRecord.EVENT_TYPE_POINTS,
        "motion": SentMessageRecord.EVENT_TYPE_MOTIONS
    }

    def receive_json(self, message, extra):
        async_to_sync(self.channel_layer.group_send)(
            self.group_name(), {
                'type': 'send_notifications',
                'message': message,
                'extra': extra
            }
        )

    def send_notifications(self, event):
        tournament = self.tournament()
        message = event['message']

        from_email = "%s <%s>" % (tournament.short_name, settings.DEFAULT_FROM_EMAIL)
        reply_to = "%s <%s>" % (tournament.pref('reply_to_name'), tournament.pref('reply_to_address')) if tournament.pref('reply_to_address') else None

        subject = Template(tournament.pref(message + "_email_subject"))
        body = Template(tournament.pref(message + "_email_message"))

        data = self.NOTIFICATION_GENERATORS[message](**event['extra'])
        round = Round.objects.get(pk=event['extra']['round_id']) if hasattr(event['extra']['round_id']) else None

        # Prepare messages
        messages = []
        records = []
        for instance, recipient in data:
            context = Context(instance)

            email = mail.EmailMessage(
                subject=subject.render(context), body=body.render(context), from_email=from_email,
                to=[recipient.email], reply_to=[reply_to]
            )
            messages.append(email)
            records.append(
                SentMessageRecord(recipient=recipient, email=self.recipient.email,
                                  event=self.NOTIFICATION_EVENTS[message],
                                  method=SentMessageRecord.METHOD_TYPE_EMAIL,
                                  round=round, tournament=tournament,
                                  context=instance, message=email.as_string())
            )

        # Send messages & record
        try:
            mail.get_connection().send_messages(messages)
        except SMTPException as e:
            self.send_error(e, _("Failed to send e-mails."), message)
            raise
        except ConnectionError as e:
            self.send_error(e, _("Connection error sending e-mails."), message)
            raise
        else:
            SentMessageRecord.objects.bulk_create(records)
