from django.db import models


class VenueGroup(models.Model):
    name = models.CharField(unique=True, max_length=200)
    short_name = models.CharField(max_length=25)
    team_capacity = models.IntegerField(
        blank=True,
        null=True,
        help_text=
        "The greatest possible number of teams that can debate in this venue group")

    @property
    def divisions_count(self):
        return self.division_set.count()

    @property
    def venues(self):
        return self.venue_set.all()

    class Meta:
        ordering = ['short_name']

    def __str__(self):
        return self.short_name or self.name


class Venue(models.Model):
    name = models.CharField(max_length=40)
    group = models.ForeignKey(VenueGroup, blank=True, null=True)
    priority = models.IntegerField(
        help_text=
        "Venues with a higher priority number will be preferred in the draw")
    tournament = models.ForeignKey('tournaments.Tournament',
                                   blank=True,
                                   null=True,
                                   db_index=True,
                                   help_text="Venues not assigned to any tournament can be shared between tournaments")

    class Meta:
        ordering = ['group', 'name']
        index_together = ['group', 'name']

    def __str__(self):
        if self.group:
            return '%s – %s' % (self.group, self.name)
        else:
            return '%s' % (self.name)

    def __repr__(self):
        return "<Venue: %s (%s) [%s]>" % (str(self), self.priority, self.id)


class BaseVenueConstraint(models.Model):
    venue_group = models.ForeignKey(VenueGroup)
    priority = models.IntegerField()

    class Meta:
        abstract = True

    def __str__(self):
        return "%s for %s [%s]" % (self.subject, self.venue_group, self.priority)

    @property
    def subject(self):
        """Subclasses must override to return something that can be compared
        so that if two constraints (a, b) relate to the same requestor,
        a.subject == b.subject."""
        raise NotImplementedError("Subclasses must implement subject()")


class TeamVenueConstraint(BaseVenueConstraint):
    team = models.ForeignKey('participants.Team')

    @property
    def subject(self):
        return self.team


class AdjudicatorVenueConstraint(BaseVenueConstraint):
    adjudicator = models.ForeignKey('participants.Adjudicator')

    @property
    def subject(self):
        return self.adjudicator


class InstitutionVenueConstraint(BaseVenueConstraint):
    institution = models.ForeignKey('participants.Institution')

    @property
    def subject(self):
        return self.institution


class DivisionVenueConstraint(BaseVenueConstraint):
    division = models.ForeignKey('tournaments.Division')

    @property
    def subject(self):
        return self.division
