from django.db import models
from django.utils.translation import gettext_lazy as _
from html2text import html2text

from utils.models import UniqueConstraint


class Motion(models.Model):
    """Represents a single motion (not a set of motions)."""

    text = models.TextField(max_length=500,
        verbose_name=_("text"),
        help_text=_("The full motion e.g., \"This House would straighten all bananas\""))
    reference = models.CharField(max_length=100,
        verbose_name=_("reference"),
        help_text=_("Shortcode for the motion, e.g., \"Bananas\""))
    info_slide = models.TextField(
        verbose_name=_("info slide"), default="", blank=True,
        help_text=_("The information slide for this topic; if it has one"))

    tournament = models.ForeignKey('tournaments.tournament', models.CASCADE,
        verbose_name=_("tournament"))
    rounds = models.ManyToManyField('tournaments.Round', through='motions.RoundMotion',
        verbose_name=_("rounds"))

    class Meta:
        verbose_name = _("motion")
        verbose_name_plural = _("motions")

    def __str__(self):
        return self.text

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude=exclude)
        if html2text(self.info_slide or '').isspace() and 'info_slide' not in exclude:
            self.info_slide = ''

    @property
    def info_slide_plain(self):
        if (self.info_slide or '').startswith('<p'):
            return html2text(self.info_slide).strip()
        return self.info_slide


class DebateTeamMotionPreference(models.Model):
    """Represents a motion preference submitted by a debate team."""

    debate_team = models.ForeignKey('draw.DebateTeam', models.CASCADE,
        verbose_name=_("debate team"))
    motion = models.ForeignKey(Motion, models.CASCADE, db_index=True,
        verbose_name=_("motion"))
    preference = models.IntegerField(db_index=True,
        verbose_name=_("preferences"))
    ballot_submission = models.ForeignKey('results.BallotSubmission', models.CASCADE,
        verbose_name=_("ballot submission"))

    class Meta:
        constraints = [UniqueConstraint(fields=['debate_team', 'preference', 'ballot_submission'])]
        verbose_name = _("debate team motion preference")
        verbose_name_plural = _("debate team motion preferences")

    def __str__(self):
        return "{0.motion.reference:s} ({0.preference:d}) by {0.debate_team!s}".format(self)

    @property
    def roundmotion(self):
        if not hasattr(self, "_roundmotion"):
            self._roundmotion = RoundMotion.objects.get(motion=self.motion, round_id=self.debate_team.debate.round_id)
        return self._roundmotion


class RoundMotion(models.Model):
    """Represents the relation between rounds and motions"""

    motion = models.ForeignKey(Motion, models.CASCADE,
        verbose_name=_("motion"))
    round = models.ForeignKey('tournaments.Round', models.CASCADE,
        verbose_name=_("round"))

    seq = models.IntegerField(default=1,
        verbose_name=_("sequence number"),
        help_text=_("The order in which motions are displayed"))

    class Meta:
        constraints = [UniqueConstraint(fields=['round', 'seq'])]
        ordering = ('round', 'seq')
        verbose_name = _("round motion")
        verbose_name_plural = _("round motions")

    def __str__(self):
        return "%s: %s" % (self.motion.reference, self.round.name)
