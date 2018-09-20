from django.db import models
from django.utils.translation import gettext_lazy as _


class DebateAdjudicatorManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        return super().get_queryset().select_related('debate')


class DebateAdjudicator(models.Model):
    TYPE_CHAIR = 'C'
    TYPE_PANEL = 'P'
    TYPE_TRAINEE = 'T'

    TYPE_CHOICES = (
        (TYPE_CHAIR,   _("chair")),
        (TYPE_PANEL,   _("panellist")),
        (TYPE_TRAINEE, _("trainee")),
    )

    objects = DebateAdjudicatorManager()

    debate = models.ForeignKey('draw.Debate', models.CASCADE,
        verbose_name=_("debate"))
    adjudicator = models.ForeignKey('participants.Adjudicator', models.CASCADE,
        verbose_name=_("adjudicator"))
    type = models.CharField(max_length=2, choices=TYPE_CHOICES,
        verbose_name=_("type"))
    timing_confirmed = models.NullBooleanField(verbose_name=_("available?"))

    class Meta:
        verbose_name = _("debate adjudicator")
        verbose_name_plural = _("debate adjudicators")
        unique_together = ('debate', 'adjudicator')

    def __str__(self):
        return '{} in {} ({})'.format(self.adjudicator, self.debate, self.get_type_display())


class AdjudicatorTeamConflict(models.Model):
    adjudicator = models.ForeignKey('participants.Adjudicator', models.CASCADE,
        verbose_name=_("adjudicator"))
    team = models.ForeignKey('participants.Team', models.CASCADE,
        verbose_name=_("team"))

    class Meta:
        verbose_name = _("adjudicator-team conflict")
        verbose_name_plural = _("adjudicator-team conflicts")
        unique_together = ('adjudicator', 'team')

    def __str__(self):
        return '{} with {}'.format(self.adjudicator, self.team)


class AdjudicatorAdjudicatorConflict(models.Model):
    adjudicator1 = models.ForeignKey('participants.Adjudicator', models.CASCADE, related_name="adjudicatoradjudicatorconflict_source_set",
        verbose_name=_("adjudicator 1"))
    adjudicator2 = models.ForeignKey('participants.Adjudicator', models.CASCADE, related_name="adjudicatoradjudicatorconflict_target_set",
        verbose_name=_("adjudicator 2"))

    class Meta:
        verbose_name = _("adjudicator-adjudicator conflict")
        verbose_name_plural = _("adjudicator-adjudicator conflicts")
        unique_together = ('adjudicator1', 'adjudicator2')

    def __str__(self):
        return '{} with {}'.format(self.adjudicator1, self.adjudicator2)


class AdjudicatorInstitutionConflict(models.Model):
    adjudicator = models.ForeignKey('participants.Adjudicator', models.CASCADE,
        verbose_name=_("adjudicator"))
    institution = models.ForeignKey('participants.Institution', models.CASCADE,
        verbose_name=_("institution"))

    class Meta:
        verbose_name = _("adjudicator-institution conflict")
        verbose_name_plural = _("adjudicator-institution conflicts")
        unique_together = ('adjudicator', 'institution')

    def __str__(self):
        return '{} with {}'.format(self.adjudicator, self.institution)


class TeamInstitutionConflict(models.Model):
    team = models.ForeignKey('participants.Team', models.CASCADE,
        verbose_name=_("team"))
    institution = models.ForeignKey('participants.Institution', models.CASCADE,
        verbose_name=_("institution"))

    class Meta:
        verbose_name = _("team-institution conflict")
        verbose_name_plural = _("team-institution conflicts")
        unique_together = ('team', 'institution')

    def __str__(self):
        return '{} with {}'.format(self.team, self.institution)
