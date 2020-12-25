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
    timing_confirmed = models.BooleanField(null=True, verbose_name=_("available?"))

    class Meta:
        verbose_name = _("debate adjudicator")
        verbose_name_plural = _("debate adjudicators")
        unique_together = ('debate', 'adjudicator')

    def __str__(self):
        return '{} in {} ({})'.format(self.adjudicator, self.debate, self.get_type_display())


# ==============================================================================
# Conflicts
# ==============================================================================

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
    adjudicator1 = models.ForeignKey('participants.Adjudicator', models.CASCADE,
        related_name="adjudicatoradjudicatorconflict_source_set",
        verbose_name=_("adjudicator 1"))
    adjudicator2 = models.ForeignKey('participants.Adjudicator', models.CASCADE,
        related_name="adjudicatoradjudicatorconflict_target_set",
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


# ==============================================================================
# Preformed panels
# ==============================================================================

class PreformedPanel(models.Model):
    round = models.ForeignKey('tournaments.Round', models.CASCADE,
        verbose_name=_("round"))
    importance = models.FloatField(default=0.0, choices=[(float(i), i) for i in range(-2, 3)],
        verbose_name=_("importance"))

    bracket_min = models.FloatField(default=0,
        verbose_name=_("minimum bracket"),
        help_text=_("Estimate of the lowest bracket for which this panel might be"))
    bracket_max = models.FloatField(default=0,
        verbose_name=_("maximum bracket"),
        help_text=_("Estimate of the highest bracket for which this panel might be"))
    room_rank = models.IntegerField(default=0,
        verbose_name=_("room rank"),
        help_text=_("Sequential number of panel, not used in any algorithms"))
    liveness = models.IntegerField(default=0,
        verbose_name=_("liveness"),
        help_text=_("Number of categories this room is expected to be live for"))

    class Meta:
        verbose_name = _("preformed panel")
        verbose_name_plural = _("preformed panels")

    def __str__(self):
        return "[{x.id}] {x.round.name} impt={x.importance}".format(x=self)

    @property
    def related_adjudicator_set(self):
        """Used by objects that work with both Debate and PreformedPanel."""
        return self.preformedpaneladjudicator_set

    @property
    def adjudicators(self):
        """Returns an AdjudicatorAllocation containing the adjudicators on this
        panel."""
        try:
            return self._adjudicators
        except AttributeError:
            from adjallocation.allocation import AdjudicatorAllocation
            self._adjudicators = AdjudicatorAllocation(self, from_db=True)
            return self._adjudicators

    # Properties to make this look like Debate for the adjudicator allocators

    @property
    def bracket(self):
        return self.bracket_max

    @property
    def teams(self):
        return []


class PreformedPanelAdjudicator(models.Model):
    panel = models.ForeignKey(PreformedPanel, models.CASCADE,
        verbose_name=_("panel"))
    adjudicator = models.ForeignKey('participants.Adjudicator', models.CASCADE,
        verbose_name=_("adjudicator"))
    type = models.CharField(max_length=2, choices=DebateAdjudicator.TYPE_CHOICES,
        verbose_name=_("type"))

    class Meta:
        verbose_name = _("preformed panel adjudicator")
        verbose_name_plural = _("preformed panel adjudicators")

    def __str__(self):
        return "[{x.id}] {x.adjudicator.name} in panel {x.panel_id}".format(x=self)
