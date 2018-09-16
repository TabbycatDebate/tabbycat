from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import gettext_lazy as _


class SentMessageRecord(models.Model):

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

    METHOD_TYPE_EMAIL = 'e'
    METHOD_TYPE_SMS = 's'
    METHOD_TYPE_CHOICES = (
        (METHOD_TYPE_EMAIL, _("email")),
        (METHOD_TYPE_SMS, _("SMS")),
    )

    recipient = models.ForeignKey('participants.Person', models.CASCADE,
        verbose_name=_("recipient"))
    event = models.CharField(max_length=1, choices=EVENT_TYPE_CHOICES, blank=True,
        verbose_name=_("event"))
    timestamp = models.DateTimeField(auto_now=True,
        verbose_name=_("timestamp"))
    method = models.CharField(max_length=1, choices=METHOD_TYPE_CHOICES,
        verbose_name=_("method"))

    tournament = models.ForeignKey('tournaments.Tournament', models.CASCADE,
        verbose_name=_("tournament"))
    round = models.ForeignKey('tournaments.Round', models.CASCADE, blank=True, null=True,
        verbose_name=_("round"))

    email = models.EmailField(null=True,
        verbose_name=_("email"))
    context = JSONField(blank=True, null=True,
        verbose_name=_("context"))
    message = models.TextField(null=True,
        verbose_name=_("message"))

    class Meta:
        verbose_name = _("sent message")
        verbose_name_plural = _("sent messages")
        ordering = ['timestamp']

    def __str__(self):
        return "%s: %s" % (self.recipient.name, self.event)
