from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import gettext_lazy as _


class SentMessageRecord(models.Model):

    METHOD_TYPE_EMAIL = 'e'
    METHOD_TYPE_SMS = 's'
    METHOD_TYPE_CHOICES = (
        (METHOD_TYPE_EMAIL, _("email")),
        (METHOD_TYPE_SMS, _("SMS")),
    )

    message_id = models.EmailField(unique=True, null=True,
        verbose_name="Message-ID") # Technical, Untranslatable term

    recipient = models.ForeignKey('participants.Person', models.CASCADE,
        verbose_name=_("recipient"))
    method = models.CharField(max_length=1, choices=METHOD_TYPE_CHOICES,
        verbose_name=_("method"))

    email = models.EmailField(null=True,
        verbose_name=_("email"))
    context = JSONField(blank=True, null=True,
        verbose_name=_("context"))
    message = models.TextField(null=True,
        verbose_name=_("message"))

    notification = models.ForeignKey('notifications.BulkNotification', models.CASCADE,
        verbose_name=_("notification"))

    class Meta:
        verbose_name = _("sent message")
        verbose_name_plural = _("sent messages")
        ordering = ['notification__timestamp']

    def __str__(self):
        return "%s: %s" % (self.recipient.name, self.notification.get_event_display())


class BulkNotification(models.Model):

    EVENT_TYPE_POINTS = 'p'
    EVENT_TYPE_BALLOT_CONFIRMED = 'c'
    EVENT_TYPE_FEEDBACK_URL = 'f'
    EVENT_TYPE_BALLOT_URL = 'b'
    EVENT_TYPE_URL = 'u'
    EVENT_TYPE_DRAW = 'd'
    EVENT_TYPE_TEAM = 't'
    EVENT_TYPE_MOTIONS = 'm'

    EVENT_TYPE_CHOICES = (
        (EVENT_TYPE_POINTS, _("team points")),
        (EVENT_TYPE_BALLOT_CONFIRMED, _("ballot confirmed")),
        (EVENT_TYPE_FEEDBACK_URL, _("feedback URL")),
        (EVENT_TYPE_BALLOT_URL, _("ballot URL")),
        (EVENT_TYPE_URL, _("landing page URL")),
        (EVENT_TYPE_DRAW, _("draw released")),
        (EVENT_TYPE_TEAM, _("team registration")),
        (EVENT_TYPE_MOTIONS, _("motion(s) released"))
    )

    event = models.CharField(max_length=1, choices=EVENT_TYPE_CHOICES, blank=True,
        verbose_name=_("event"))
    timestamp = models.DateTimeField(auto_now=True,
        verbose_name=_("timestamp"))

    tournament = models.ForeignKey('tournaments.Tournament', models.CASCADE,
        verbose_name=_("tournament"))
    round = models.ForeignKey('tournaments.Round', models.CASCADE, blank=True, null=True,
        verbose_name=_("round"))

    class Meta:
        verbose_name = _("bulk notification")
        verbose_name_plural = _("bulk notifications")
        ordering = ['timestamp']

    def __str__(self):
        return "[%s] %s: %s" % (self.tournament.short_name, self.get_event_display(), self.timestamp)


class EmailStatus(models.Model):
    email = models.ForeignKey('notifications.SentMessageRecord', models.CASCADE,
        verbose_name=_("email message"))
    timestamp = models.DateTimeField(auto_now=True,
        verbose_name=_("timestamp"))
    event = models.CharField(max_length=20,
        verbose_name=_("event"))
    data = JSONField(verbose_name=_("context"))

    class Meta:
        verbose_name = _("email status")
        verbose_name_plural = _("email statuses")
        ordering = ['timestamp']

    def __str__(self):
        return "%s - %s" % (self.email, self.event)
