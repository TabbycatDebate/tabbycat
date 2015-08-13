from django.db import models

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