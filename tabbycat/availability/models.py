from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class RoundAvailability(models.Model):

    CONTENT_TYPE_CHOICES = models.Q(app_label='participants', model='team') | \
        models.Q(app_label='participants', model='adjudicator') | \
        models.Q(app_label='venues', model='venue')

    content_type = models.ForeignKey(ContentType, models.CASCADE,
        limit_choices_to=CONTENT_TYPE_CHOICES)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    round = models.ForeignKey('tournaments.Round', models.CASCADE)

    class Meta:
        unique_together = [('round', 'content_type', 'object_id')]
        verbose_name_plural = 'round availabilities'

    def __repr__(self):
        return "<RoundAvailability: %s in %s>" % (self.content_object, self.round.name)
