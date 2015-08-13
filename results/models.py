from django.db import models
from django.utils.functional import cached_property

from debate.models import Submission

class ScoreField(models.FloatField):
    pass

class BallotSubmission(Submission):
    """Represents a single submission of ballots for a debate.
    (Not a single motion, but a single submission of all ballots for a debate.)"""

    debate = models.ForeignKey('debate.Debate', db_index=True)
    motion = models.ForeignKey('motions.Motion', blank=True, null=True, on_delete=models.SET_NULL)

    copied_from = models.ForeignKey('BallotSubmission', blank=True, null=True)
    discarded = models.BooleanField(default=False)

    forfeit = models.ForeignKey('debate.DebateTeam', blank=True, null=True)

    class Meta:
        unique_together = [('debate', 'version')]

    def __unicode__(self):
        return 'Ballot for ' + unicode(self.debate) + ' submitted at ' + \
                ('<unknown>' if self.timestamp is None else unicode(self.timestamp.isoformat()))


    @cached_property
    def ballot_set(self):
        if not hasattr(self, "_ballot_set"):
            self._ballot_set = BallotSet(self)
        return self._ballot_set

    def clean(self):
        # The motion must be from the relevant round
        super(BallotSubmission, self).clean()
        if self.motion.round != self.debate.round:
                raise ValidationError("Debate is in round %d but motion (%s) is from round %d" % (self.debate.round, self.motion.reference, self.motion.round))
        if self.confirmed and self.discarded:
            raise ValidationError("A ballot can't be both confirmed and discarded!")

    def is_identical(self, other):
        """Returns True if all data fields are the same. Returns False in any
        other case. Does not raise exceptions if things look weird. Possibly
        over-conservative: it checks fields that are theoretically redundant."""
        if self.debate != other.debate:
            return False
        if self.motion != other.motion:
            return False
        def check(this, other_set, fields):
            """Returns True if it could find an object with the same data.
            Using filter() doesn't seem to work on non-integer float fields,
            so we compare score by retrieving it."""
            try:
                other_obj = other_set.get(**dict((f, getattr(this, f)) for f in fields))
            except (MultipleObjectsReturned, ObjectDoesNotExist):
                return False
            return this.score == other_obj.score
        # Check all of the SpeakerScoreByAdjs.
        # For each one, we must be able to find one by the same adjudicator, team and
        # position, and they must have the same score.
        for this in self.speakerscorebyadj_set.all():
            if not check(this, other.speakerscorebyadj_set, ["debate_adjudicator", "debate_team", "position"]):
                return False
        # Check all of the SpeakerScores.
        # In theory, we should only need to check speaker positions, since that is
        # the only information not inferrable from SpeakerScoreByAdj. But check
        # everything, to be safe.
        for this in self.speakerscore_set.all():
            if not check(this, other.speakerscore_set, ["debate_team", "speaker", "position"]):
                return False
        # Check TeamScores, to be safe
        for this in self.teamscore_set.all():
            if not check(this, other.teamscore_set, ["debate_team", "points"]):
                return False
        return True

    # For further discussion
    #submitter_name = models.CharField(max_length=40, null=True)                # only relevant for public submissions
    #submitter_email = models.EmailField(max_length=254, blank=True, null=True) # only relevant for public submissions
    #submitter_phone = models.CharField(max_length=40, blank=True, null=True)   # only relevant for public submissions


class SpeakerScoreByAdj(models.Model):
    """
    Holds score given by a particular adjudicator in a debate
    """
    ballot_submission = models.ForeignKey(BallotSubmission)
    debate_adjudicator = models.ForeignKey('debate.DebateAdjudicator')
    debate_team = models.ForeignKey('debate.DebateTeam')
    score = ScoreField()
    position = models.IntegerField()

    class Meta:
        unique_together = [('debate_adjudicator', 'debate_team', 'position', 'ballot_submission')]
        index_together = ['ballot_submission','debate_adjudicator']

    @property
    def debate(self):
        return self.debate_team.debate


class TeamScore(models.Model):
    """
    Holds a teams total score and points in a debate
    """
    ballot_submission = models.ForeignKey(BallotSubmission)
    debate_team = models.ForeignKey('debate.DebateTeam', db_index=True)
    points = models.PositiveSmallIntegerField()
    margin = ScoreField()
    win = models.NullBooleanField()
    score = ScoreField()
    affects_averages = models.BooleanField(default=True, blank=False, null=False,
        help_text="Whether to count this when determining average speaker points and/or margins")

    @property # TODO this should be called something more descriptive, or turned into a method
    def get_margin(self):
        if self.affects_averages == True:
            return self.margin
        else:
            return None

    @property # TODO this should be called something more descriptive, or turned into a method
    def get_score(self):
        if self.affects_averages == True:
            return self.score
        else:
            return None

    class Meta:
        unique_together = [('debate_team', 'ballot_submission')]


class SpeakerScoreManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        return super(SpeakerScoreManager,
                     self).get_queryset().select_related('speaker')


class SpeakerScore(models.Model):
    """Represents a speaker's (overall) score in a debate.

    The 'speaker' field is canonical. The 'score' field, however, is a
    performance enhancement; raw scores are stored in SpeakerScoreByAdj. The
    BallotSet class in result.py calculates this when it saves a ballot set.
    """
    ballot_submission = models.ForeignKey(BallotSubmission)
    debate_team = models.ForeignKey('debate.DebateTeam')
    speaker = models.ForeignKey('debate.Speaker', db_index=True)
    score = ScoreField()
    position = models.IntegerField()

    objects = SpeakerScoreManager()

    class Meta:
        unique_together = [('debate_team', 'speaker', 'position', 'ballot_submission')]
