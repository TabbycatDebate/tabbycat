from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class SentMessage(models.Model):

    METHOD_TYPE_EMAIL = 'e'
    METHOD_TYPE_SMS = 's'
    METHOD_TYPE_CHOICES = (
        (METHOD_TYPE_EMAIL, _("email")),
        (METHOD_TYPE_SMS, _("SMS")),
    )

    message_id = models.CharField(max_length=254, unique=True, null=True,
        verbose_name="Message-ID") # Technical, Untranslatable term
    hook_id = models.CharField(max_length=16, unique=True, blank=True, null=True,
        verbose_name="Hook-ID")

    recipient = models.ForeignKey('participants.Person', models.SET_NULL, null=True,
        verbose_name=_("recipient"))
    method = models.CharField(max_length=1, choices=METHOD_TYPE_CHOICES,
        verbose_name=_("method"))

    email = models.EmailField(null=True,
        verbose_name=_("email"))
    context = models.JSONField(blank=True, null=True,
        verbose_name=_("context"))

    notification = models.ForeignKey('notifications.BulkNotification', models.CASCADE,
        verbose_name=_("notification"))
    timestamp = models.DateTimeField(auto_now_add=True,
        verbose_name=_("timestamp"))

    class Meta:
        verbose_name = _("sent message")
        verbose_name_plural = _("sent messages")

    def __str__(self):
        return "%s (%s) %s" % (self.recipient, self.email, self.notification.get_event_display())


class BulkNotification(models.Model):

    class EventType(models.TextChoices):
        POINTS = 'p', _("team points")
        BALLOTS_CONFIRMED = 'c', _("ballot confirmed")
        FEEDBACK_URL = 'f', _("feedback URL")
        BALLOT_URL = 'b', _("ballot URL")
        URL = 'u', _("landing page URL")
        ADJ_DRAW = 'd', _("adjudicator draw released")
        TEAM_REG = 't', _("team registration")
        ADJ_REG = 'a', _("adjudicator registration")
        MOTIONS = 'm', _("motion(s) released")
        TEAM_DRAW = 'r', _("team draw released")
        CUSTOM = '', _("custom message")

    event = models.CharField(max_length=20, choices=EventType.choices,
        verbose_name=_("event"))
    timestamp = models.DateTimeField(auto_now_add=True,
        verbose_name=_("timestamp"))

    tournament = models.ForeignKey('tournaments.Tournament', models.CASCADE,
        verbose_name=_("tournament"))
    round = models.ForeignKey('tournaments.Round', models.CASCADE, blank=True, null=True,
        verbose_name=_("round"))

    subject_template = models.TextField(null=True,
        verbose_name=_("subject template"))
    body_template = models.TextField(null=True,
        verbose_name=_("body template"))

    class Meta:
        verbose_name = _("bulk notification")
        verbose_name_plural = _("bulk notifications")
        ordering = ['-timestamp']

    def __str__(self):
        return "[%s] %s: %s" % (
            self.tournament.short_name,
            self.get_event_display(),
            timezone.localtime(self.timestamp).isoformat(),
        )


class EmailStatus(models.Model):
    class EventType(models.TextChoices):
        PROCESSED = 'processed', _("Processed")
        DROPPED = 'dropped', _("Dropped")
        DEFERRED = 'deferred', _("Deferred")
        DELIVERED = 'delivered', _("Delivered")
        BOUNCED = 'bounce', _("Bounced")
        OPENED = 'open', _("Opened")
        CLICKED = 'click', _("Clicked")
        UNSUBSCRIBED = 'unsubscribe', _("Unsubscribed")
        SPAM = 'spamreport', _("Marked as spam")
        ASM_UNSUBSCRIBED = 'group_unsubscribe', _("Unsubscribed from group")
        ASM_RESUBSCRIBED = 'group_resubscribe', _("Resubscribed to group")

    email = models.ForeignKey('notifications.SentMessage', models.CASCADE,
        verbose_name=_("email message"))
    timestamp = models.DateTimeField(auto_now_add=True,
        verbose_name=_("timestamp"))
    event = models.CharField(max_length=20, choices=EventType.choices,
        verbose_name=_("event"))
    data = models.JSONField(blank=True, null=True,
        verbose_name=_("context"))

    class Meta:
        verbose_name = _("email status")
        verbose_name_plural = _("email statuses")
        ordering = ['-timestamp']
        get_latest_by = '-timestamp'

    def __str__(self):
        return "%s - %s" % (self.email, self.event)
