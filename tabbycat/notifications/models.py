from django.db import models
from django.utils.translation import gettext_lazy as _


class MessageSentRecord(models.Model):

    EVENT_TYPE_POINTS = 'p'
    EVENT_TYPE_BALLOT_CONFIRMED = 'c'
    EVENT_TYPE_FEEDBACK_URL = 'f'
    EVENT_TYPE_BALLOT_URL = 'b'
    EVENT_TYPE_CHOICES = (
        (EVENT_TYPE_POINTS, _("team points")),
        (EVENT_TYPE_BALLOT_CONFIRMED, _("ballot confirmed")),
        (EVENT_TYPE_FEEDBACK_URL, _("feedback URL")),
        (EVENT_TYPE_BALLOT_URL, _("ballot URL"))
    )

    METHOD_TYPE_EMAIL = 'e'
    METHOD_TYPE_CHOICES = (
        (METHOD_TYPE_EMAIL, _("email")),
    )

    recepient = models.ForeignKey('participants.Person', models.CASCADE,
        verbose_name=_("recepient"))
    event = models.CharField(max_length=1, choices=EVENT_TYPE_CHOICES,
        verbose_name=_("event"))
    timestamp = models.DateTimeField(auto_now=True,
        verbose_name=_("timestamp"))
    method = models.CharField(max_length=1, choices=METHOD_TYPE_CHOICES,
        verbose_name=_("method"))

    tournament = models.ForeignKey('tournaments.Tournament', models.CASCADE,
        verbose_name=_("tournament"))
    round = models.ForeignKey('tournaments.Round', models.CASCADE, blank=True, null=True,
        verbose_name=_("round"))

    class Meta:
        verbose_name = _("message sent record")
        verbose_name_plural = _("message sent records")
        ordering = ['timestamp']

    def __str__(self):
        return "%s: %s" % (self.recepient.name, self.event)
