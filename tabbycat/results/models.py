import logging
from threading import Lock

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

from .result import BallotSet

logger = logging.getLogger(__name__)


class ScoreField(models.FloatField):
    pass


class Submission(models.Model):
    """Abstract base class to provide functionality common to different
    types of submissions.

    The unique_together class attribute of the Meta class MUST be set in
    all subclasses."""

    SUBMITTER_TABROOM = 'T'
    SUBMITTER_PUBLIC = 'P'
    SUBMITTER_TYPE_CHOICES = ((SUBMITTER_TABROOM, 'Tab room'),
                              (SUBMITTER_PUBLIC, 'Public'), )

    timestamp = models.DateTimeField(auto_now_add=True)
    version = models.PositiveIntegerField()
    submitter_type = models.CharField(max_length=1,
                                      choices=SUBMITTER_TYPE_CHOICES)

    submitter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        related_name="%(app_label)s_%(class)s_submitted"
    )  # only relevant if submitter was in tab room
    confirmer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        related_name="%(app_label)s_%(class)s_confirmed")
    confirm_timestamp = models.DateTimeField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    version_lock = Lock()

    confirmed = models.BooleanField(default=False)

    class Meta:
        abstract = True

    @property
    def _unique_filter_args(self):
        return dict((arg, getattr(self, arg))
                    for arg in self._meta.unique_together[0]
                    if arg != 'version')

    def save(self, *args, **kwargs):
        # Check for uniqueness.
        if self.confirmed:
            try:
                current = self.__class__.objects.get(confirmed=True,
                                                     **
                                                     self._unique_filter_args)
            except self.DoesNotExist:
                pass
            else:
                if current != self:
                    logger.warning(
                        "{} confirmed while {} was already confirmed, setting latter to unconfirmed".format(
                            self, current))
                    current.confirmed = False
                    current.save()

        # Assign the version field to one more than the current maximum version.
        # Use a lock to protect against the possibility that two submissions do this
        # at the same time and get the same version number.
        with self.version_lock:
            if self.pk is None:
                existing = self.__class__.objects.filter(**
                                                         self._unique_filter_args)
                if existing.exists():
                    self.version = existing.aggregate(models.Max('version'))[
                        'version__max'] + 1
                else:
                    self.version = 1
            super(Submission, self).save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.submitter_type == self.SUBMITTER_TABROOM and self.submitter is None:
            raise ValidationError("A tab room ballot must have a user associated.")


class BallotSubmission(Submission):
    """Represents a single submission of ballots for a debate.
    (Not a single motion, but a single submission of all ballots for a debate.)"""

    debate = models.ForeignKey('draw.Debate', db_index=True)
    motion = models.ForeignKey('motions.Motion',
                               blank=True,
                               null=True,
                               on_delete=models.SET_NULL)

    copied_from = models.ForeignKey('BallotSubmission', blank=True, null=True)
    discarded = models.BooleanField(default=False)

    forfeit = models.ForeignKey('draw.DebateTeam', blank=True, null=True)

    class Meta:
        unique_together = [('debate', 'version')]

    def __str__(self):
        return "Ballot for {debate} submitted at {time} (version {version})".format(
            debate=self.debate.matchup,
            version=self.version,
            time=('<unknown>' if self.timestamp is None else str(
                self.timestamp.isoformat())))

    @property
    def ballot_set(self):
        if not hasattr(self, "_ballot_set"):
            self._ballot_set = BallotSet(self)
        return self._ballot_set

    def clean(self):
        # The motion must be from the relevant round
        super().clean()
        if self.motion.round != self.debate.round:
            raise ValidationError(
                "Debate is in round {:d} but motion ({:s}) is from round {:d}".format(
                    self.debate.round, self.motion.reference,
                    self.motion.round))
        if self.confirmed and self.discarded:
            raise ValidationError("A ballot can't be both confirmed and discarded!")


class SpeakerScoreByAdj(models.Model):
    """Holds score given by a particular adjudicator in a debate."""
    ballot_submission = models.ForeignKey(BallotSubmission)
    debate_adjudicator = models.ForeignKey('adjallocation.DebateAdjudicator')
    debate_team = models.ForeignKey('draw.DebateTeam')
    score = ScoreField()
    position = models.IntegerField()

    class Meta:
        unique_together = [('debate_adjudicator', 'debate_team', 'position',
                            'ballot_submission')]
        index_together = ['ballot_submission', 'debate_adjudicator']
        verbose_name_plural = 'speaker scores by adj'

    @property
    def debate(self):
        return self.debate_team.debate

    def clean(self):
        super().clean()
        if (self.debate_team.debate != self.debate_adjudicator.debate or
                self.debate_team.debate != self.ballot_submission.debate):
            raise ValidationError("The debate team, debate adjudicator and ballot "
                    "submission must all relate to the same debate.")


class TeamScore(models.Model):
    """Stores information about a team's result in a debate. This is all
    redundant information — it can all be derived from indirectly-related
    SpeakerScore objects. We use a separate model for it for performance
    reasons."""

    ballot_submission = models.ForeignKey(BallotSubmission)
    debate_team = models.ForeignKey('draw.DebateTeam', db_index=True)

    points = models.PositiveSmallIntegerField()
    margin = ScoreField()
    win = models.NullBooleanField()
    score = ScoreField()
    votes_given = models.PositiveSmallIntegerField()
    votes_possible = models.PositiveSmallIntegerField()

    forfeit = models.BooleanField(
        default=False, blank=False, null=False,
        help_text="Debate was a forfeit (True for both winning and forfeiting teams)")

    class Meta:
        unique_together = [('debate_team', 'ballot_submission')]


class SpeakerScoreManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        return super().get_queryset().select_related('speaker')


class SpeakerScore(models.Model):
    """Represents a speaker's (overall) score in a debate.

    The 'speaker' field is canonical. The 'score' field, however, is a
    performance enhancement; raw scores are stored in SpeakerScoreByAdj. The
    BallotSet class in result.py calculates this when it saves a ballot set.
    """
    ballot_submission = models.ForeignKey(BallotSubmission)
    debate_team = models.ForeignKey('draw.DebateTeam')
    speaker = models.ForeignKey('participants.Speaker', db_index=True)
    score = ScoreField()
    position = models.IntegerField()

    objects = SpeakerScoreManager()

    class Meta:
        unique_together = [('debate_team', 'position', 'ballot_submission')]

    def clean(self):
        super().clean()
        if self.debate_team.team != self.speaker.team:
            raise ValidationError("The debate team and speaker must be from the "
                    "same team.")
        if self.ballot_submission.debate != self.debate_team.debate:
            raise ValidationError("The ballot submission and debate team must "
                    "relate to the same debate.")
