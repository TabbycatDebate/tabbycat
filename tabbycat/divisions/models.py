from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.functional import cached_property


class Division(models.Model):
    name = models.CharField(max_length=50, verbose_name="Name or suffix")
    seq = models.IntegerField(blank=True, null=True,
        help_text="The order in which divisions are displayed")
    tournament = models.ForeignKey('tournaments.Tournament')
    time_slot = models.TimeField(blank=True, null=True)
    venue_group = models.ForeignKey('venues.VenueGroup', blank=True, null=True)

    venue_constraints = GenericRelation('venues.VenueConstraint', related_query_name='division',
            content_type_field='subject_content_type', object_id_field='subject_id')

    @property
    def teams_count(self):
        return self.team_set.count()

    @cached_property
    def teams(self):
        return self.team_set.all().order_by(
            'institution', 'reference').select_related('institution')

    def __str__(self):
        return "%s - %s" % (self.tournament, self.name)

    class Meta:
        unique_together = [('tournament', 'name')]
        ordering = ['tournament', 'seq']
        index_together = ['tournament', 'seq']
