from django.db import models


class DebateAdjudicatorManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        return super().get_queryset().select_related('debate')


class DebateAdjudicator(models.Model):
    TYPE_CHAIR = 'C'
    TYPE_PANEL = 'P'
    TYPE_TRAINEE = 'T'

    TYPE_CHOICES = (
        (TYPE_CHAIR,   'chair'),
        (TYPE_PANEL,   'panellist'),
        (TYPE_TRAINEE, 'trainee'),
    )

    objects = DebateAdjudicatorManager()

    debate = models.ForeignKey('draw.Debate', models.CASCADE)
    adjudicator = models.ForeignKey('participants.Adjudicator', models.CASCADE)
    type = models.CharField(max_length=2, choices=TYPE_CHOICES)
    timing_confirmed = models.NullBooleanField(verbose_name="Available? ")

    def __str__(self):
        return '{} in {} ({})'.format(self.adjudicator, self.debate, self.get_type_display())

    class Meta:
        unique_together = ('debate', 'adjudicator')


class AdjudicatorConflict(models.Model):
    adjudicator = models.ForeignKey('participants.Adjudicator', models.CASCADE)
    team = models.ForeignKey('participants.Team', models.CASCADE)

    class Meta:
        verbose_name = "adjudicator-team conflict"


class AdjudicatorAdjudicatorConflict(models.Model):
    adjudicator = models.ForeignKey('participants.Adjudicator', models.CASCADE, related_name="source_adjudicator")
    conflict_adjudicator = models.ForeignKey('participants.Adjudicator', models.CASCADE, related_name="target_adjudicator", verbose_name="Adjudicator")

    class Meta:
        verbose_name = "adjudicator-adjudicator conflict"


class AdjudicatorInstitutionConflict(models.Model):
    adjudicator = models.ForeignKey('participants.Adjudicator', models.CASCADE)
    institution = models.ForeignKey('participants.Institution', models.CASCADE)

    class Meta:
        verbose_name = "adjudicator-institution conflict"
