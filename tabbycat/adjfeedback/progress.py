"""Utilities to compute which feedback has been submitted and not submitted
by participants of the tournament.

There are a few possibilities for how to characterise a feedback submission:
"""

from .models import AdjudicatorFeedback


class BaseFeedbackExpectedSubmissionTracker:
    """Represents a single piece of expected feedback."""

    expected = True

    def __init__(self, source):
        self.source = source  # either a DebateTeam or a DebateAdjudicator

    @property
    def round(self):
        return self.source.debate.round

    @property
    def count(self):
        return self.related_submissions().count()

    @property
    def fulfilled(self):
        return self.acceptable_submissions().count() == 1 and self.count == 1

    def related_submissions(self):
        """In subclass implementations, this should return a QuerySet."""
        raise NotImplementedError

    def acceptable_submissions(self):
        """Subclasses should override this method of it is possible for some
        submissions to be relevant, but not acceptable."""
        return self.related_submissions()


class FeedbackExpectedSubmissionFromTeamTracker(BaseFeedbackExpectedSubmissionTracker):
    """Represents a single piece of expected feedback from a team."""

    expected = True

    def acceptable_targets(self):
        """For a team, this must be the adjudicator who delivered the oral
        adjudication. If the chair was rolled, then it is one of the majority
        adjudicators; if the chair was in the majority, then it must be the
        chair."""

        majority = self.source.debate.confirmed_ballot.ballot_set.majority_adj
        chair = self.source.debate.adjudicators.chair

        if chair in majority:
            return [chair]
        else:
            return majority

    def related_submissions(self):
        return self.source.adjudicatorfeedback_set.filter(confirmed=True, source_team=self.source)

    def acceptable_submissions(self):
        return self.related_submissions().filter(adjudicator__in=self.acceptable_targets())


class FeedbackExpectedSubmissionFromAdjudicatorTracker(BaseFeedbackExpectedSubmissionTracker):
    """Represents a single piece of expected feedback from an adjudicator."""

    expected = True

    def __init__(self, source, target):
        self.target = target
        return super().__init__(source)

    def related_submissions(self):
        return self.source.adjudicatorfeedback_set.filter(confirmed=True,
            adjudicator=self.target, source_adjudicator=self.source)

    def acceptable_targets(self):
        return [self.target]


class FeedbackUnexpectedSubmissionTracker:
    """Represents a single piece of unexpected feedback."""

    expected = False
    fulfilled = False

    def __init__(self, feedback):
        self.feedback = feedback  # an AdjudicatorFeedback instance

    @property
    def round(self):
        return self.feedback.source.debate.round

    @property
    def count(self):
        return 1

    def related_submissions(self):
        return [self.feedback]


class BaseFeedbackProgress:
    """Class to compute feedback submitted or owed by a participant.

    Rather than just counting and comparing aggregates, everything is compared
    at the individual feedback level using objects called "trackers". This
    ensures that feedbacks that were actually submitted match those that were
    expected."""

    def get_expected_trackers(self):
        raise NotImplementedError

    def get_submitted_feedback(self):
        raise NotImplementedError

    def expected_trackers(self):
        if not hasattr(self, "_expected_trackers"):
            self._expected_trackers = self.get_expected_trackers()
        return self._expected_trackers

    def submitted_feedback(self):
        if not hasattr(self, "_submitted_feedback"):
            self._submitted_feedback = self.get_submitted_feedback()
        return self._submitted_feedback

    def expected_feedback(self):
        """Returns a list of AdjudicatorFeedback objects that are submitted
        as expected."""
        return [feedback for tracker in self.expected_trackers()
                for feedback in tracker.submissions()]

    def unexpected_trackers(self):
        """Returns a list of trackers for feedback that was submitted but not
        expected to be there."""
        return [FeedbackUnexpectedSubmissionTracker(feedback) for feedback in
            self.feedback_submitted() if feedback not in self.expected_feedback()]

    def fulfilled_trackers(self):
        """Returns a list of trackers that are fulfilled."""
        return [tracker for tracker in self.expected_trackers() if tracker.fulfilled]

    def trackers(self):
        """Returns a list of all trackers, sorted by round."""
        return sorted(self.expected_trackers() + self.unexpected_trackers(),
                key=lambda x: x.round.seq)

    def num_submitted(self):
        """Returns the number of feedbacks that were submitted, including
        duplicate and unexpected submissions."""
        return self.feedback_submitted().count()

    def num_expected(self):
        """Returns the number of feedbacks that are expected from this participant."""
        return len(self.expected_trackers())

    def num_fulfilled(self):
        """Returns the number of feedbacks that are correctly submitted,
        excluding those where more than one feedback was submitted but only
        one was expected."""
        return len(self.fulfilled_trackers())

    def coverage(self):
        """Returns the number of fulfilled feedbacks divided by the number
        of expected feedbacks."""
        return self.num_fulfilled() / self.num_expected()


class FeedbackProgressForTeam(BaseFeedbackProgress):
    """Class to compute feedback submitted or owed by a team.

    A team owes feedback on every orallist. There are therefore three types of
    entries:
     - Feedback submitted as expected
     - Feedback that is expected on an orallist, but has not been submitted
     - Feedback that has been submitted, but was not expected from that team
    """

    def __init__(self, team):
        self.team = team

    def _debateteams(self):
        """Returns all of the DebateTeam instances for which a team owes
        feedback, which is all the debates for which there is a confirmed
        ballot."""
        return self.team.debateteam_set.filter(debate__ballotsubmission__confirmed=True).unique()

    def get_feedback_submitted(self):
        return AdjudicatorFeedback.objects.filter(source_team__team=self.team)

    def get_expected_trackers(self):
        return [FeedbackExpectedSubmissionFromTeamTracker(dt) for dt in self._debateteams()]
