from django.db import models

class VenueGroup(models.Model):
    name = models.CharField(unique=True, max_length=200)
    short_name = models.CharField(db_index=True, max_length=25)
    team_capacity = models.IntegerField(blank=True, null=True)

    @property
    def divisions_count(self):
        return self.division_set.count()

    @property
    def venues(self):
        return self.venue_set.all()

    class Meta:
        ordering = ['short_name']

    def __unicode__(self):
        if self.short_name:
            return u"%s" % (self.short_name)
        else:
            return u"%s" % (self.name)

class Venue(models.Model):
    name = models.CharField(max_length=40)
    group = models.ForeignKey(VenueGroup, blank=True, null=True)
    priority = models.IntegerField(help_text="Venues with a higher priority number will be preferred in the draw")
    tournament = models.ForeignKey('debate.Tournament', blank=True, null=True)
    time = models.DateTimeField(blank=True, null=True, help_text="")

    class Meta:
        ordering = ['group', 'name']
        index_together = ['group', 'name']

    def __unicode__(self):
        if self.group:
            return u'%s - %s' % (self.group, self.name)
        else:
            return u'%s' % (self.name)