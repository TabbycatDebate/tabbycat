from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _


class RoundAvailability(models.Model):

    CONTENT_TYPE_CHOICES = models.Q(app_label='participants', model='team') | \
        models.Q(app_label='participants', model='adjudicator') | \
        models.Q(app_label='venues', model='venue')

    content_type = models.ForeignKey(ContentType, models.CASCADE,
        limit_choices_to=CONTENT_TYPE_CHOICES,
        verbose_name=_("content type"))
    object_id = models.PositiveIntegerField(verbose_name=_("object id"))
    content_object = GenericForeignKey('content_type', 'object_id')

    round = models.ForeignKey('tournaments.Round', models.CASCADE,
        verbose_name=_("round"))

    class Meta:
        unique_together = [('round', 'content_type', 'object_id')]
        verbose_name = _("round availability")
        verbose_name_plural = _("round availabilities")

    def __repr__(self):
        return "<RoundAvailability: %s in %s>" % (self.content_object, self.round.name)
