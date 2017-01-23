from django.db import models


class Motion(models.Model):
    """Represents a single motion (not a set of motions)."""

    seq = models.IntegerField(
        help_text="The order in which motions are displayed")
    text = models.TextField(max_length=500,
        help_text="The full motion e.g., \"This House would straighten all bananas\"")
    reference = models.CharField(max_length=100,
        help_text="Shortcode for the motion, e.g., \"Bananas\"")
    flagged = models.BooleanField(default=False,
        help_text="For WADL: Allows for particular motions to be flagged as contentious")
    round = models.ForeignKey('tournaments.Round', models.CASCADE)
    divisions = models.ManyToManyField('divisions.Division', blank=True)

    class Meta:
        ordering = ('seq', )

    def __str__(self):
        return self.text


class DebateTeamMotionPreference(models.Model):
    """Represents a motion preference submitted by a debate team."""
    debate_team = models.ForeignKey('draw.DebateTeam', models.CASCADE)
    motion = models.ForeignKey(Motion, models.CASCADE, db_index=True)
    preference = models.IntegerField(db_index=True)
    ballot_submission = models.ForeignKey('results.BallotSubmission', models.CASCADE)

    class Meta:
        unique_together = [('debate_team', 'preference', 'ballot_submission')]
