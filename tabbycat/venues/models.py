from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models


class VenueGroup(models.Model):
    name = models.CharField(unique=True, max_length=200)
    short_name = models.CharField(max_length=25)
    team_capacity = models.IntegerField(
        blank=True,
        null=True,
        help_text="The greatest possible number of teams that can debate in this venue group")

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
    group = models.ForeignKey(VenueGroup, models.SET_NULL, blank=True, null=True)
    priority = models.IntegerField(
        help_text="Venues with a higher priority number will be preferred in the draw")
    tournament = models.ForeignKey('tournaments.Tournament', models.CASCADE,
        blank=True, null=True, db_index=True,
        help_text="Venues not assigned to any tournament can be shared between tournaments")

    round_availabilities = GenericRelation('availability.RoundAvailability')

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


class VenueConstraintManager(models.Manager):

    def filter_for_debates(self, debates):
        """Convenience function. Filters for all constraints relevant to the
        given iterable of debates."""
        return VenueConstraint.objects.filter(
            models.Q(team__debateteam__debate__in=debates) |
            models.Q(institution__team__debateteam__debate__in=debates) |
            models.Q(adjudicator__debateadjudicator__debate__in=debates) |
            models.Q(division__debate__in=debates)
        ).distinct()


class VenueConstraintCategory(models.Model):
    name = models.CharField(max_length=50)
    venues = models.ManyToManyField(Venue)

    class Meta:
        verbose_name_plural = "venue constraint categories"

    def __str__(self):
        return self.name


class VenueConstraint(models.Model):

    SUBJECT_CONTENT_TYPE_CHOICES = models.Q(app_label='participants', model='team') | \
                                   models.Q(app_label='participants', model='adjudicator') | \
                                   models.Q(app_label='participants', model='institution') | \
                                   models.Q(app_label='divisions', model='division')

    category = models.ForeignKey(VenueConstraintCategory, models.CASCADE)
    priority = models.IntegerField()

    subject_content_type = models.ForeignKey(ContentType, models.CASCADE,
            limit_choices_to=SUBJECT_CONTENT_TYPE_CHOICES)
    subject_id = models.PositiveIntegerField()
    subject = GenericForeignKey('subject_content_type', 'subject_id')

    objects = VenueConstraintManager()

    def __str__(self):
        return "%s for %s [%s]" % (self.subject, self.category, self.priority)
