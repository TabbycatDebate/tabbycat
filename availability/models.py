from django.db import models


class Checkin(models.Model):
    person = models.ForeignKey('debate.Person')
    round = models.ForeignKey('debate.Round')


class ActiveVenue(models.Model):
    venue = models.ForeignKey('debate.Venue')
    round = models.ForeignKey('debate.Round')

    class Meta:
        unique_together = [('venue', 'round')]


class ActiveTeam(models.Model):
    team = models.ForeignKey('debate.Team')
    round = models.ForeignKey('debate.Round')

    class Meta:
        unique_together = [('team', 'round')]


class ActiveAdjudicator(models.Model):
    adjudicator = models.ForeignKey('debate.Adjudicator')
    round = models.ForeignKey('debate.Round')

    class Meta:
        unique_together = [('adjudicator', 'round')]