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
        verbose_name = "🏢 Venue Group"

    def __str__(self):
        if self.short_name:
            return "%s" % (self.short_name)
        else:
            return "%s" % (self.name)


class Venue(models.Model):
    name = models.CharField(max_length=40)
    group = models.ForeignKey(VenueGroup, blank=True, null=True)
    priority = models.IntegerField(
        help_text=
        "Venues with a higher priority number will be preferred in the draw")
    tournament = models.ForeignKey('tournaments.Tournament',
                                   blank=True,
                                   null=True,
                                   db_index=True)
    time = models.DateTimeField(blank=True, null=True, help_text="")

    class Meta:
        ordering = ['group', 'name']
        index_together = ['group', 'name']
        verbose_name = "🎪 Venue"

    def __str__(self):
        if self.group:
            return '%s - %s' % (self.group, self.name)
        else:
            return '%s' % (self.name)
