import logging
from smtplib import SMTPException

from django.conf import settings
from django.core import mail
from django.template import Context, Template

from draw.utils import send_mail_to_adjs
from privateurls.utils import send_randomised_url_emails
from results.utils import send_ballot_receipt_emails_to_adjudicators
from tournaments.utils import send_standings_emails

from .models import SentMessageRecord

logger = logging.getLogger(__name__)


class TournamentEmailMessage(mail.EmailMessage):
    def __init__(self, subject, body, tournament=None, round=None, event=None, person=None, fields=None,
                 connection=None, headers={}, cc=None, bcc=None, attachments=None):

        self.person = person
        self.emails = [self.person.email]

        self.tournament = tournament
        self.round = round

        self.event = event
        self.headers = headers

        self.fields = fields
        self.context = Context(fields)
        self.subject = subject.render(self.context)
        self.body = body.render(self.context)

        self.from_email = "%s <%s>" % (self.tournament.short_name, settings.DEFAULT_FROM_EMAIL)
        self.reply_to = None
        if self.tournament.pref('reply_to_address') != "":
            self.reply_to = ["%s <%s>" % (self.tournament.pref('reply_to_name'), self.tournament.pref('reply_to_address'))]

        super().__init__(self.subject, self.body, self.from_email, self.emails, bcc, connection, attachments,
            self.headers, cc, self.reply_to)

    def as_sent_record(self):
        return SentMessageRecord(recipient=self.person, email=self.person.email,
                                 event=self.event, method=SentMessageRecord.METHOD_TYPE_EMAIL,
                                 round=self.round, tournament=self.tournament,
                                 context=self.fields, message=self.message().as_string())


class EmailMessageGenerator:
    function = None

    subject = None
    message = None

    def __init__(self, tournament=None):
        self.tournament = tournament

    def get_subject(self):
        return Template(self.tournament.pref(self.subject))

    def get_message(self):
        return Template(self.tournament.pref(self.message))

    def run(self, **kwargs):
        messages = self.function(self.get_subject(), self.get_message(), **kwargs)

        try:
            mail.get_connection().send_messages(messages)
        except SMTPException:
            logger.exception("Failed to send e-mails.")
            raise
        except ConnectionError:
            logger.exception("Connection error sending e-mails.")
            raise
        else:
            SentMessageRecord.objects.bulk_create([message.as_sent_record() for message in messages])

        return len(messages)


class AdjudicatorAssignmentEmailGenerator(EmailMessageGenerator):
    function = send_mail_to_adjs

    subject = 'adj_email_subject_line'
    message = 'adj_email_message'


class RandomizedURLEmailGenerator(EmailMessageGenerator):
    function = send_randomised_url_emails

    def __init__(self, subject, message, tournament=None):
        self.subject = subject
        self.message = message

        super().__init__(tournament)

    def get_subject(self):
        return Template(self.subject)

    def get_message(self):
        return Template(self.message)


class BallotEmailGenerator(EmailMessageGenerator):
    function = send_ballot_receipt_emails_to_adjudicators

    subject = 'ballot_email_subject'
    message = 'ballot_email_message'


class StandingsEmailGenerator(EmailMessageGenerator):
    function = send_standings_emails

    subject = 'team_points_email_subject'
    message = 'team_points_email_message'
