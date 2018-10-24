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

    message_id = models.CharField(max_length=254, unique=True, null=True,
        verbose_name="Message-ID") # Technical, Untranslatable term

    recipient = models.ForeignKey('participants.Person', models.SET_NULL, null=True,
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
        ordering = ['-notification__timestamp', '-recipient__name']

    def __str__(self):
        return "%s: %s" % (self.recipient.name, self.notification.get_event_display())


class BulkNotification(models.Model):

    EVENT_TYPE_POINTS = 'p'
    EVENT_TYPE_BALLOT_CONFIRMED = 'c'
    EVENT_TYPE_FEEDBACK_URL = 'f'
    EVENT_TYPE_BALLOT_URL = 'b'
    EVENT_TYPE_URL = 'u'
    EVENT_TYPE_DRAW = 'd'
    EVENT_TYPE_REGISTRATION = 't'
    EVENT_TYPE_MOTIONS = 'm'

    EVENT_TYPE_CHOICES = (
        (EVENT_TYPE_POINTS, _("team points")),
        (EVENT_TYPE_BALLOT_CONFIRMED, _("ballot confirmed")),
        (EVENT_TYPE_FEEDBACK_URL, _("feedback URL")),
        (EVENT_TYPE_BALLOT_URL, _("ballot URL")),
        (EVENT_TYPE_URL, _("landing page URL")),
        (EVENT_TYPE_DRAW, _("draw released")),
        (EVENT_TYPE_REGISTRATION, _("registration")),
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
        ordering = ['-timestamp']

    def __str__(self):
        return "[%s] %s: %s" % (self.tournament.short_name, self.get_event_display(), self.timestamp)


class EmailStatus(models.Model):

    EVENT_TYPE_PROCESSED = 'processed'
    EVENT_TYPE_DROPPED = 'dropped'
    EVENT_TYPE_DEFERRED = 'deferred'
    EVENT_TYPE_DELIVERED = 'delivered'
    EVENT_TYPE_BOUNCED = 'bounce'
    EVENT_TYPE_OPENED = 'open'
    EVENT_TYPE_CLICKED = 'click'
    EVENT_TYPE_UNSUBSCRIBED = 'unsubscribe'
    EVENT_TYPE_SPAM = 'spamreport'
    EVENT_TYPE_ASM_UNSUBSCRIBED = 'group_unsubscribe'
    EVENT_TYPE_ASM_RESUBSCRIBED = 'group_resubscribe'

    EVENT_TYPE_CHOICES = (
        (EVENT_TYPE_PROCESSED, _("Processed")),
        (EVENT_TYPE_DROPPED, _("Dropped")),
        (EVENT_TYPE_DEFERRED, _("Deferred")),
        (EVENT_TYPE_DELIVERED, _("Delivered")),
        (EVENT_TYPE_BOUNCED, _("Bounced")),
        (EVENT_TYPE_OPENED, _("Opened")),
        (EVENT_TYPE_CLICKED, _("Clicked")),
        (EVENT_TYPE_UNSUBSCRIBED, _("Unsubscribed")),
        (EVENT_TYPE_SPAM, _("Marked as spam")),
        (EVENT_TYPE_ASM_UNSUBSCRIBED, _("Unsubscribed from group")),
        (EVENT_TYPE_ASM_RESUBSCRIBED, _("Resubscribed to group"))
    )

    email = models.ForeignKey('notifications.SentMessageRecord', models.CASCADE,
        verbose_name=_("email message"))
    timestamp = models.DateTimeField(auto_now=True,
        verbose_name=_("timestamp"))
    event = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES,
        verbose_name=_("event"))
    data = JSONField(verbose_name=_("context"))

    class Meta:
        verbose_name = _("email status")
        verbose_name_plural = _("email statuses")
        ordering = ['-timestamp']
        get_latest_by = '-timestamp'

    def __str__(self):
        return "%s - %s" % (self.email, self.event)
