from django.db import models
from django.utils.translation import gettext_lazy as _


class Motion(models.Model):
    """Represents a single motion (not a set of motions)."""

    seq = models.IntegerField(default=1,
        verbose_name=_("sequence number"),
        help_text=_("The order in which motions are displayed"))
    text = models.TextField(max_length=500,
        verbose_name=_("text"),
        help_text=_("The full motion e.g., \"This House would straighten all bananas\""))
    reference = models.CharField(max_length=100,
        verbose_name=_("reference"),
        help_text=_("Shortcode for the motion, e.g., \"Bananas\""))
    info_slide = models.TextField(
        verbose_name=_("info slide"), default="", blank=True,
        help_text=_("The information slide for this topic; if it has one"))
    round = models.ForeignKey('tournaments.Round', models.CASCADE,
        verbose_name=_("round"))

    class Meta:
        ordering = ('seq', )
        verbose_name = _("motion")
        verbose_name_plural = _("motions")

    def __str__(self):
        return self.text

    def as_iterable(self):
        """For DRF; stopgap for many-to-many"""
        return [self]


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
        unique_together = [('debate_team', 'preference', 'ballot_submission')]
        verbose_name = _("debate team motion preference")
        verbose_name_plural = _("debate team motion preferences")

    def __str__(self):
        return "{0.motion.reference:s} ({0.preference:d}) by {0.debate_team!s}".format(self)
