from django.conf import settings
from django.core import mail
from django.template import Context

from .models import SentMessageRecord


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
