from django.db import models

from tournaments.models import SRManager


class DebateAdjudicator(models.Model):
    TYPE_CHAIR = 'C'
    TYPE_PANEL = 'P'
    TYPE_TRAINEE = 'T'

    TYPE_CHOICES = (
        (TYPE_CHAIR,   'chair'),
        (TYPE_PANEL,   'panellist'),
        (TYPE_TRAINEE, 'trainee'),
    )

    objects = SRManager()

    debate = models.ForeignKey('draw.Debate')
    adjudicator = models.ForeignKey('participants.Adjudicator')
    type = models.CharField(max_length=2, choices=TYPE_CHOICES)
    timing_confirmed = models.NullBooleanField(verbose_name="Available? ")

    def __str__(self):
        return '{} in {}'.format(self.adjudicator, self.debate)

    class Meta:
        unique_together = ('debate', 'adjudicator')


class AdjudicatorConflict(models.Model):
    adjudicator = models.ForeignKey('participants.Adjudicator')
    team = models.ForeignKey('participants.Team')

    class Meta:
        verbose_name = "adjudicator-team conflict"


class AdjudicatorAdjudicatorConflict(models.Model):
    adjudicator = models.ForeignKey('participants.Adjudicator', related_name="source_adjudicator")
    conflict_adjudicator = models.ForeignKey('participants.Adjudicator', related_name="target_adjudicator", verbose_name="Adjudicator")

    class Meta:
        verbose_name = "adjudicator-adjudicator conflict"


class AdjudicatorInstitutionConflict(models.Model):
    adjudicator = models.ForeignKey('participants.Adjudicator')
    institution = models.ForeignKey('participants.Institution')

    class Meta:
        verbose_name = "adjudicator-institution conflict"


class AdjudicatorAllocation:
    """Not a model, just a container object for the adjudicators on a panel."""

    def __init__(self, debate, chair=None, panel=None):
        self.debate = debate
        self.chair = chair
        self.panel = panel or []
        self.trainees = []

    @property
    def list(self):
        """Panel only, excludes trainees."""
        a = [self.chair]
        a.extend(self.panel)
        return a

    def __len__(self):
        return (0 if self.chair is None else 1) + len(self.panel) + len(self.trainees)

    def __str__(self):
        items = [str(getattr(x, "name", x)) for x in self.list]
        return ", ".join(items)

    def __iter__(self):
        """Iterates through all, including trainees."""
        if self.chair is not None:
            yield DebateAdjudicator.TYPE_CHAIR, self.chair
        for a in self.panel:
            yield DebateAdjudicator.TYPE_PANEL, a
        for a in self.trainees:
            yield DebateAdjudicator.TYPE_TRAINEE, a

    def __contains__(self, item):
        return item == self.chair or item in self.panel or item in self.trainees

    def __eq__(self, other):
        return self.debate == other.debate and self.chair == other.chair and \
            set(self.panel) == set(other.panel) and \
            set(self.trainees) == set(other.trainees)

    def delete(self):
        """Delete existing, current allocation"""
        self.debate.debateadjudicator_set.all().delete()
        self.chair = None
        self.panel = []
        self.trainees = []

    @property
    def has_chair(self):
        return self.chair is not None

    @property
    def is_panel(self):
        return len(self.panel) > 0

    @property
    def valid(self):
        return self.has_chair and len(self.panel) % 2 == 0

    def save(self):
        self.debate.debateadjudicator_set.all().delete()
        for t, adj in self:
            if adj:
                DebateAdjudicator(debate=self.debate, adjudicator=adj, type=t).save()
