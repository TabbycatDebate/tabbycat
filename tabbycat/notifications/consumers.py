from smtplib import SMTPException

from channels.consumer import SyncConsumer
from django.conf import settings
from django.core import mail
from django.template import Context, Template
from django.utils.translation import gettext_lazy as _

from draw.models import Debate
from tournaments.models import Round, Tournament

from .models import SentMessageRecord
from .utils import (adjudicator_assignment_email_generator, ballots_email_generator,
                    motion_release_email_generator, randomized_url_email_generator, standings_email_generator)


class NotificationQueueConsumer(SyncConsumer):

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

    def email(self, event):
        if 'debate_id' in event['extra']:
            round = Debate.objects.get(pk=event['extra']['debate_id']).round
            t = round.tournament
        elif 'round_id' in event['extra']:
            round = Round.objects.get(pk=event['extra']['round_id'])
            t = round.tournament
        else:
            round = None
            t = Tournament.objects.get(pk=event['extra']['tournament_id'])

        notification_type = event['message']

        from_email = "%s <%s>" % (t.short_name, settings.DEFAULT_FROM_EMAIL)
        reply_to = None
        if t.pref('reply_to_address'):
            reply_to = "%s <%s>" % (t.pref('reply_to_name'), t.pref('reply_to_address'))
        subject = Template(t.pref(notification_type + "_email_subject"))
        body = Template(t.pref(notification_type + "_email_message"))

        data = self.NOTIFICATION_GENERATORS[notification_type](**event['extra'])

        # Prepare messages
        messages = []
        records = []
        for instance, recipient in data:
            context = Context(instance)
            email = mail.EmailMessage(
                subject=subject.render(context), body=body.render(context),
                from_email=from_email, to=[recipient.email], reply_to=[reply_to]
            )
            messages.append(email)
            records.append(
                SentMessageRecord(recipient=recipient, email=recipient.email,
                                  event=self.NOTIFICATION_EVENTS[notification_type],
                                  method=SentMessageRecord.METHOD_TYPE_EMAIL,
                                  round=round, tournament=t,
                                  context=instance, message=email.body)
            )

        # Send messages & record
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
