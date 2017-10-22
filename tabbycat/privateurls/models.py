from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext


class PrivateUrlSentMailRecord(models.Model):

    URL_TYPE_BALLOT = 'b'
    URL_TYPE_FEEDBACK = 'f'
    URL_TYPE_CHOICES = (
        (URL_TYPE_BALLOT, _("ballot")),
        (URL_TYPE_FEEDBACK, _("feedback")),
    )

    adjudicator = models.ForeignKey('participants.Adjudicator', models.CASCADE, blank=True, null=True,
        verbose_name=_("recipient adjudicator"))
    speaker = models.ForeignKey('participants.Speaker', models.CASCADE, blank=True, null=True,
        verbose_name=_("recipient speaker"))

    url_type = models.CharField(max_length=1, choices=URL_TYPE_CHOICES,
        verbose_name=_("URL type"))

    email = models.EmailField(verbose_name=_("e-mail address"))
    url_key = models.SlugField(max_length=24, verbose_name=_("URL key"))

    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("timestamp"))

    class Meta:
        verbose_name = _("private URL sent mail record")
        verbose_name_plural = _("private URL sent mail records")

    def __str__(self):
        return "{x.recipient_name:s} ({x.email:s}): {x.url_key:s}".format(x=self)

    @property
    def recipient_name(self):
        if self.adjudicator and self.speaker:
            return ugettext("<both adjudicator and speaker>")
        elif self.adjudicator:
            return self.adjudicator.name
        elif self.speaker:
            return self.speaker.name

    @property
    def current_url_key(self):
        """Returns the current URL key for the recipient."""
        if self.adjudicator:
            return self.adjudicator.url_key
        elif self.speaker:
            return self.speaker.team.url_key

    def clean(self):
        if not (self.adjudicator or self.speaker):
            raise ValidationError(
                ugettext("No recipient (adjudicator or speaker) was specified."))
        if self.adjudicator and self.speaker:
            raise ValidationError(
                ugettext("There was both a recipient adjudicator and a recipient speaker."))
        return super().clean()
