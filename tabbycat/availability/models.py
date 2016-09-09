from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class RoundAvailability(models.Model):
    round = models.ForeignKey('tournaments.Round', models.CASCADE)

    content_type = models.ForeignKey(ContentType, models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = [('round', 'content_type', 'object_id')]

    def __repr__(self):
        return "<RoundAvailability: %s in %s>" % (self.content_object, self.round.name)


class Checkin(models.Model):
    person = models.ForeignKey('participants.Person')
    round = models.ForeignKey('tournaments.Round')


class ActiveVenue(models.Model):
    venue = models.ForeignKey('venues.Venue')
    round = models.ForeignKey('tournaments.Round')

    class Meta:
        unique_together = [('venue', 'round')]


class ActiveTeam(models.Model):
    team = models.ForeignKey('participants.Team')
    round = models.ForeignKey('tournaments.Round')

    class Meta:
        unique_together = [('team', 'round')]


class ActiveAdjudicator(models.Model):
    adjudicator = models.ForeignKey('participants.Adjudicator')
    round = models.ForeignKey('tournaments.Round')

    class Meta:
        unique_together = [('adjudicator', 'round')]
