import logging
from threading import Lock

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from motions.models import RoundMotion
from tournaments.models import Tournament
from utils.misc import badge_datetime_format, reverse_tournament
from utils.models import UniqueConstraint

from .result import DebateResult
from .utils import readable_ballotsub_result

logger = logging.getLogger(__name__)


class ScoreField(models.FloatField):
    pass


class Submission(models.Model):
    """Abstract base class to provide functionality common to different
    types of submissions.

    The unique_together class attribute of the Meta class MUST be set in
    all subclasses."""

    class Submitter(models.TextChoices):
        TABROOM = 'T', _("Tab room")
        PUBLIC = 'P', _("Public")
        AUTOMATION = 'A', _("Automation")

    timestamp = models.DateTimeField(auto_now_add=True,
        verbose_name=_("timestamp"))
    version = models.PositiveIntegerField(
        verbose_name=_("version"))
    submitter_type = models.CharField(max_length=1, choices=Submitter.choices,
        verbose_name=_("submitter type"))
    confirmed = models.BooleanField(default=False,
        verbose_name=_("confirmed"))

    # relevant for private URL submissions
    private_url = models.BooleanField(default=False,
        verbose_name=_("from private URL"))
    participant_submitter = models.ForeignKey('participants.Person', models.PROTECT,
        blank=True, null=True, related_name="%(app_label)s_%(class)s_participant_submitted",
        verbose_name=_("from participant"))

    # only relevant if submitter was in tab room
    submitter = models.ForeignKey(settings.AUTH_USER_MODEL, models.PROTECT,
        blank=True, null=True, related_name="%(app_label)s_%(class)s_submitted",
        verbose_name=_("submitter"))
    confirmer = models.ForeignKey(settings.AUTH_USER_MODEL, models.PROTECT,
        blank=True, null=True, related_name="%(app_label)s_%(class)s_confirmed",
        verbose_name=_("confirmer"))
    confirm_timestamp = models.DateTimeField(blank=True, null=True,
        verbose_name=_("confirm timestamp"))
    ip_address = models.GenericIPAddressField(blank=True, null=True,
        verbose_name=_("IP address"))

    save_lock = Lock()

    class Meta:
        abstract = True

    @property
    def _unique_filter_args(self):
        return dict((arg, getattr(self, arg)) for arg in self._meta.constraints[0].fields
                    if arg != 'version')

    def _unique_unconfirm_args(self):
        return self._unique_filter_args

    def save(self, *args, **kwargs):
        # Use a lock to protect against the possibility that two submissions do this
        # at the same time and get the same version number or both be confirmed.
        with self.save_lock:

            # Assign the version field to one more than the current maximum version.
            if self.pk is None:
                existing = self.__class__.objects.filter(**self._unique_filter_args)
                if existing.exists():
                    self.version = existing.aggregate(models.Max('version'))['version__max'] + 1
                else:
                    self.version = 1

            # Check for uniqueness.
            if self.confirmed:
                unconfirmed = self.__class__.objects.filter(confirmed=True,
                        **self._unique_unconfirm_args()).exclude(pk=self.pk).update(confirmed=False)
                if unconfirmed > 0:
                    logger.info("Unconfirmed %d %s so that %s could be confirmed", unconfirmed, self._meta.verbose_name_plural, self)

            super(Submission, self).save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.submitter_type == self.Submitter.TABROOM and self.submitter is None:
            raise ValidationError(_("A tab room ballot must have a user associated."))


class BallotSubmission(Submission):
    """Represents a single submission of ballots for a debate.
    (Not a single motion, but a single submission of all ballots for a debate.)"""

    debate = models.ForeignKey('draw.Debate', models.CASCADE, db_index=True,
        verbose_name=_("debate"))
    motion = models.ForeignKey('motions.Motion', models.SET_NULL, blank=True, null=True,
        verbose_name=_("motion"))
    discarded = models.BooleanField(default=False,
        verbose_name=_("discarded"))
    single_adj = models.BooleanField(default=False,
        verbose_name=_("single adjudicator"),
        help_text=_("Whether this submission represents only the submitting adjudicator on a panel, "
                    "when individual adjudicator ballots are enabled."))

    class Meta:
        constraints = [UniqueConstraint(fields=['debate', 'version'])]
        verbose_name = _("ballot submission")
        verbose_name_plural = _("ballot submissions")

    def __str__(self):
        if self.timestamp is None:
            return "[{0.id}] Ballot for {0.debate!s}, no submission time (v{0.version})".format(self)
        else:
            return ("[{0.id}] Ballot for {0.debate!s}, submitted at "
                "{0.timestamp:%Y-%m-%dT%H:%M:%S} (v{0.version})").format(self)

    @property
    def result(self):
        if not hasattr(self, "_result"):
            self._result = DebateResult(self)
        return self._result

    def clean(self):
        # The motion must be from the relevant round
        super().clean()
        if self.motion is not None and self.debate.round not in self.motion.rounds.all():
            raise ValidationError(_("Debate is in %(round)s but motion (%(motion)s) is not in round") % {
                    'round': self.debate.round.name,
                    'motion': self.motion.reference})

        if self.confirmed and self.discarded:
            raise ValidationError(_("A ballot can't be both confirmed and discarded!"))

    @property
    def serialize_like_actionlog(self):
        if hasattr(self, '_result'):
            dr = self._result
        else:
            from results.result import DebateResult
            dr = DebateResult(self)
        result_winner, result = readable_ballotsub_result(dr)
        return {
            'user': result_winner,
            'id': self.id,
            'type': result,
            'param': '',
            'timestamp': badge_datetime_format(self.timestamp),
            'confirmed': self.confirmed,
            'debate': self.debate.id,
            'result_status': self.debate.result_status,
        }

    def serialize(self, tournament=None):
        if not tournament:
            tournament = self.debate.round.tournament

        # Shown in the results page on a per-ballot; always measured in tab TZ
        created_short = timezone.localtime(self.timestamp).strftime("%H:%M")
        # These are used by the status graph
        created = timezone.localtime(self.timestamp).isoformat()
        confirmed = None
        if self.confirm_timestamp and self.confirmed:
            confirmed = timezone.localtime(self.confirm_timestamp).isoformat()

        if tournament.pref('enable_blind_checks') and tournament.pref('teams_in_debate') == 4:
            admin_url = 'results-ballotset-edit'
            assistant_url = 'results-assistant-ballotset-edit'
        else:
            admin_url = 'old-results-ballotset-edit'
            assistant_url = 'old-results-assistant-ballotset-edit'

        submitter = self.ip_address
        private_url = False
        if self.submitter:
            submitter = self.submitter.username
        elif self.participant_submitter:
            submitter = self.participant_submitter.name
            private_url = True

        return {
            'ballot_id': self.id,
            'debate_id': self.debate.id,
            'submitter': submitter,
            'private_url': private_url,
            'admin_link': reverse_tournament(admin_url, tournament, kwargs={'pk': self.id}),
            'assistant_link': reverse_tournament(assistant_url, tournament, kwargs={'pk': self.id}),
            'short_time': created_short,
            'created_timestamp': created,
            'confirmed_timestamp': confirmed,
            'version': self.version,
            'confirmed': self.confirmed,
            'discarded': self.discarded,
            'single_adj': self.single_adj,
        }

    @property
    def roundmotion(self):
        if not hasattr(self, "_roundmotion"):
            if self.motion is not None:
                self._roundmotion = RoundMotion.objects.get(motion=self.motion, round_id=self.debate.round_id)
            else:
                self._roundmotion = None
        return self._roundmotion


class TeamScoreByAdj(models.Model):
    """Holds team result given by a particular adjudicator in a debate.
    Mostly redundant; is necessary however for voting elimination ballots."""
    ballot_submission = models.ForeignKey(BallotSubmission, models.CASCADE,
        verbose_name=_("ballot submission"))
    debate_adjudicator = models.ForeignKey('adjallocation.DebateAdjudicator', models.CASCADE,
        verbose_name=_("debate adjudicator"))
    debate_team = models.ForeignKey('draw.DebateTeam', models.CASCADE,
        verbose_name=_("debate team"))

    win = models.BooleanField(null=True, blank=True,
        verbose_name=_("win"))
    margin = ScoreField(null=True, blank=True,
        verbose_name=_("margin"))
    score = ScoreField(null=True, blank=True,
        verbose_name=_("score"))

    class Meta:
        constraints = [
            UniqueConstraint(fields=['debate_adjudicator', 'debate_team', 'ballot_submission']),
        ]
        indexes = [models.Index(fields=['ballot_submission', 'debate_adjudicator'])]
        verbose_name = _("team score by adjudicator")
        verbose_name_plural = _("team scores by adjudicator")

    def __str__(self):
        has_won = "Win" if self.win else "Loss"
        return ("[{0.ballot_submission_id}/{0.id}] {1} for "
            "{0.debate_team!s} from {0.debate_adjudicator!s}").format(self, has_won)

    @property
    def debate(self):
        return self.debate_team.debate

    def clean(self):
        super().clean()
        if (self.debate_team.debate != self.debate_adjudicator.debate or
                self.debate_team.debate != self.ballot_submission.debate):
            raise ValidationError(_("The debate team, debate adjudicator and ballot "
                    "submission must all relate to the same debate."))


class SpeakerScoreByAdj(models.Model):
    """Holds score given by a particular adjudicator in a debate."""
    ballot_submission = models.ForeignKey(BallotSubmission, models.CASCADE,
        verbose_name=_("ballot submission"))
    debate_adjudicator = models.ForeignKey('adjallocation.DebateAdjudicator', models.CASCADE,
        verbose_name=_("debate adjudicator"))
    debate_team = models.ForeignKey('draw.DebateTeam', models.CASCADE,
        verbose_name=_("debate team"))
    score = ScoreField(verbose_name=_("score"))
    position = models.IntegerField(verbose_name=_("position"))

    class Meta:
        constraints = [
            UniqueConstraint(fields=['debate_adjudicator', 'debate_team', 'position', 'ballot_submission']),
        ]
        indexes = [models.Index(fields=['ballot_submission', 'debate_adjudicator'])]
        verbose_name = _("speaker score by adjudicator")
        verbose_name_plural = _("speaker scores by adjudicator")

    def __str__(self):
        return ("[{0.ballot_submission_id}/{0.id}] {0.score} at {0.position} for "
            "{0.debate_team!s} from {0.debate_adjudicator!s}").format(self)

    @property
    def debate(self):
        return self.debate_team.debate

    def clean(self):
        super().clean()
        if (self.debate_team.debate != self.debate_adjudicator.debate or
                self.debate_team.debate != self.ballot_submission.debate):
            raise ValidationError(_("The debate team, debate adjudicator and ballot "
                    "submission must all relate to the same debate."))


class TeamScore(models.Model):
    """Stores information about a team's result in a debate. This is all
    redundant information — it can all be derived from indirectly-related
    SpeakerScore objects. We use a separate model for it for performance
    reasons."""

    ballot_submission = models.ForeignKey(BallotSubmission, models.CASCADE,
        verbose_name=_("ballot submission"))
    debate_team = models.ForeignKey('draw.DebateTeam', models.CASCADE, db_index=True,
        verbose_name=_("debate team"))

    points = models.PositiveSmallIntegerField(null=True, blank=True,
        verbose_name=_("points"))
    win = models.BooleanField(null=True, blank=True,
        verbose_name=_("win"))
    margin = ScoreField(null=True, blank=True,
        verbose_name=_("margin"))
    score = ScoreField(null=True, blank=True,
        verbose_name=_("score"))
    votes_given = models.PositiveSmallIntegerField(null=True, blank=True,
        verbose_name=_("votes given"))
    votes_possible = models.PositiveSmallIntegerField(null=True, blank=True,
        verbose_name=_("votes possible"))
    has_ghost = models.BooleanField(null=True, blank=True, verbose_name=_("has ghost score"))

    class Meta:
        constraints = [UniqueConstraint(fields=['debate_team', 'ballot_submission'])]
        verbose_name = _("team score")
        verbose_name_plural = _("team scores")

    def __str__(self):
        return ("[{0.ballot_submission_id}/{0.id}] {0.points}, {0.score} for "
            "{0.debate_team!s}").format(self)


class SpeakerScoreManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        return super().get_queryset().select_related('speaker')


class SpeakerScore(models.Model):
    """Represents a speaker's (overall) score in a debate.

    The 'speaker' field is canonical. The 'score' field, however, is a
    performance enhancement; raw scores are stored in SpeakerScoreByAdj. The
    result classes in result.py calculates this when it saves a result.
    """
    ballot_submission = models.ForeignKey(BallotSubmission, models.CASCADE,
        verbose_name=_("ballot submission"))
    debate_team = models.ForeignKey('draw.DebateTeam', models.CASCADE,
        verbose_name=_("debate team"))
    speaker = models.ForeignKey('participants.Speaker', models.CASCADE, db_index=True,
        verbose_name=_("speaker"))
    rank = models.PositiveSmallIntegerField(null=True, blank=True,
        verbose_name=_("rank"))
    score = ScoreField(verbose_name=_("score"))
    position = models.IntegerField(verbose_name=_("position"))
    ghost = models.BooleanField(default=False,
        verbose_name=_("ghost"),
        help_text=_("If checked, this score does not count towards the speaker tab. "
            "This is typically checked for speeches where someone spoke twice to "
            "make up for an absent teammate (sometimes known as \"iron-person\" or "
            "\"iron-man\" speeches)."))

    objects = SpeakerScoreManager()

    class Meta:
        constraints = [UniqueConstraint(fields=['debate_team', 'position', 'ballot_submission'])]
        verbose_name = _("speaker score")
        verbose_name_plural = _("speaker scores")

    def __str__(self):
        return ("[{0.ballot_submission_id}/{0.id}] {0.score} at {0.position} for "
            "{0.speaker.name} in {0.debate_team!s}").format(self)

    def clean(self):
        super().clean()
        if self.debate_team.team != self.speaker.team:
            raise ValidationError(_("The debate team and speaker must be from the "
                    "same team."))
        if self.ballot_submission.debate != self.debate_team.debate:
            raise ValidationError(_("The ballot submission and debate team must "
                    "relate to the same debate."))


class ScoreCriterion(models.Model):
    """Score criterion for speaker score"""
    tournament = models.ForeignKey(Tournament, models.CASCADE,
        verbose_name=_("tournament"))
    name = models.CharField(max_length=20,
        verbose_name=("name"))
    seq = models.IntegerField(verbose_name=_("sequence"))
    weight = models.FloatField(verbose_name=_("weight"))
    min_score = ScoreField(verbose_name=_("minimum score"))
    max_score = ScoreField(verbose_name=_("maximum score"))
    step = models.FloatField(verbose_name=_("step"))
    required = models.BooleanField(default=True,
        verbose_name="required")

    class Meta:
        constraints = [UniqueConstraint(fields=['tournament', 'seq'])]
        verbose_name = _("score criterion")
        verbose_name_plural = _("score criteria")

    def __str__(self):
        return ("{0.name} at {0.tournament}").format(self)


class SpeakerCriterionScore(models.Model):

    score = ScoreField(verbose_name=_("score"))
    criterion = models.ForeignKey(ScoreCriterion, models.CASCADE,
        verbose_name=_("score criterion"))
    speaker_score = models.ForeignKey(SpeakerScore, models.CASCADE,
        verbose_name="speaker score")

    class Meta:
        constraints = [UniqueConstraint(fields=['speaker_score', 'criterion'])]
        verbose_name = _("speaker score for criterion")
        verbose_name_plural = _("speaker scores for criteria")

    def __str__(self):
        return ("[{0.speaker_score_id}/{0.id}] {0.score} for {0.criterion_id}").format(self)


class SpeakerCriterionScoreByAdj(models.Model):

    score = ScoreField(verbose_name=_("score"))
    criterion = models.ForeignKey(ScoreCriterion, models.CASCADE,
        verbose_name=_("score criterion"))
    speaker_score_by_adj = models.ForeignKey(SpeakerScoreByAdj, models.CASCADE,
        verbose_name="speaker score")

    class Meta:
        constraints = [UniqueConstraint(fields=['speaker_score_by_adj', 'criterion'])]
        verbose_name = _("speaker score for criterion by adjudicator")
        verbose_name_plural = _("speaker scores for criteria by adjudicator")

    def __str__(self):
        return ("[{0.speaker_score_by_adj_id}/{0.id}] {0.score} for {0.criterion_id}").format(self)
