"""Utilities to compute which feedback has been submitted and not submitted
by participants of the tournament.

There are a few possibilities for how to characterise a feedback submission:
"""

from operator import attrgetter

from adjallocation.allocation import populate_allocations
from adjallocation.models import DebateAdjudicator
from adjfeedback.models import AdjudicatorFeedback
from results.prefetch import populate_confirmed_ballots
from tournaments.models import Round


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
        return len(self.acceptable_submissions())

    @property
    def fulfilled(self):
        return self.count == 1

    def acceptable_submissions(self):
        if not hasattr(self, '_acceptable_submissions'):
            self._acceptable_submissions = self.get_acceptable_submissions()
        return self._acceptable_submissions

    def get_acceptable_submissions(self):
        """Subclasses should override this method to provide an iterable of
        acceptable submissions. Users of this class might pre-populate
        the `_acceptable_submissions` attribute to avoid duplicate database
        hits."""
        raise NotImplementedError

    def submission(self):
        if self.fulfilled:
            return self.acceptable_submissions()[0]
        else:
            return None


class FeedbackExpectedSubmissionFromTeamTracker(BaseFeedbackExpectedSubmissionTracker):
    """Represents a single piece of expected feedback from a team."""

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

    def get_acceptable_submissions(self):
        return self.source.adjudicatorfeedback_set.filter(confirmed=True,
                source_team=self.source,
                adjudicator__in=self.acceptable_targets()).select_related(
                'source_team', 'adjudicator', 'adjudicator__institution')


class FeedbackExpectedSubmissionFromAdjudicatorTracker(BaseFeedbackExpectedSubmissionTracker):
    """Represents a single piece of expected feedback from an adjudicator."""

    def __init__(self, source, target):
        self.target = target
        return super().__init__(source)

    def get_acceptable_submissions(self):
        return self.source.adjudicatorfeedback_set.filter(confirmed=True,
            adjudicator=self.target, source_adjudicator=self.source).select_related(
            'source_adjudicator', 'adjudicator', 'adjudicator__institution')

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
        return self.feedback.round

    @property
    def count(self):
        return 1

    def submission(self):
        return self.feedback


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
        as expected (including where more are submitted than expected)."""
        return [feedback for tracker in self.expected_trackers()
                for feedback in tracker.acceptable_submissions()]

    def unexpected_trackers(self):
        """Returns a list of trackers for feedback that was submitted but not
        expected to be there."""
        return [FeedbackUnexpectedSubmissionTracker(feedback) for feedback in
            self.submitted_feedback() if feedback not in self.expected_feedback()]

    def fulfilled_trackers(self):
        """Returns a list of trackers that are fulfilled."""
        return [tracker for tracker in self.expected_trackers() if tracker.fulfilled]

    def trackers(self):
        """Returns a list of all trackers, sorted by round."""
        # return sorted(self.expected_trackers() + self.unexpected_trackers(),
        return sorted(self.expected_trackers(), # don't include unexpected trackers
                key=lambda x: x.round.seq)

    def num_submitted(self):
        """Returns the number of feedbacks that were submitted, including
        duplicate and unexpected submissions."""
        return len(self.submitted_feedback())

    def num_expected(self):
        """Returns the number of feedbacks that are expected from this participant."""
        return len(self.expected_trackers())

    def num_fulfilled(self):
        """Returns the number of feedbacks that are correctly submitted,
        excluding those where more than one feedback was submitted but only
        one was expected."""
        return len(self.fulfilled_trackers())

    def num_unsubmitted(self):
        return self.num_expected() - self.num_fulfilled()

    def coverage(self):
        """Returns the number of fulfilled feedbacks divided by the number
        of expected feedbacks."""
        if self.num_expected() == 0:
            return 1.0
        return self.num_fulfilled() / self.num_expected()

    def _prefetch_tracker_acceptable_submissions(self, trackers, tracker_identifier, feedback_identifier):
        trackers_by_identifier = {}
        for tracker in trackers:
            tracker._acceptable_submissions = []
            identifier = tracker_identifier(tracker)
            trackers_by_identifier[identifier] = tracker
        for feedback in self.submitted_feedback():
            identifier = feedback_identifier(feedback)
            try:
                tracker = trackers_by_identifier[identifier]
            except KeyError:
                continue
            if feedback.adjudicator in tracker.acceptable_targets():
                tracker._acceptable_submissions.append(feedback)


class FeedbackProgressForTeam(BaseFeedbackProgress):
    """Class to compute feedback submitted or owed by a team."""

    def __init__(self, team):
        self.team = team

    def get_submitted_feedback(self):
        return AdjudicatorFeedback.objects.filter(confirmed=True,
                source_team__team=self.team,
                source_team__debate__round__stage=Round.STAGE_PRELIMINARY).select_related(
                'adjudicator', 'adjudicator__institution', 'source_team__debate__round')

    def get_expected_trackers(self):
        # There is one tracker for each debate for which there is a confirmed ballot,
        # and the round is not silent.

        debateteams = self.team.debateteam_set.filter(
                debate__ballotsubmission__confirmed=True,
                debate__round__silent=False,
                debate__round__stage=Round.STAGE_PRELIMINARY).select_related(
                'debate', 'debate__round')
        debates = [dt.debate for dt in debateteams]
        populate_allocations(debates)
        populate_confirmed_ballots(debates, ballotsets=True)

        trackers = [FeedbackExpectedSubmissionFromTeamTracker(dt) for dt in debateteams]
        self._prefetch_tracker_acceptable_submissions(trackers,
                attrgetter('source'), attrgetter('source_team'))
        return trackers


class FeedbackProgressForAdjudicator(BaseFeedbackProgress):
    """Class to compute feedback submitted or owed by an adjudicator."""

    def __init__(self, adjudicator):
        self.adjudicator = adjudicator

    def get_submitted_feedback(self):
        return AdjudicatorFeedback.objects.filter(confirmed=True,
                source_adjudicator__adjudicator=self.adjudicator,
                source_adjudicator__debate__round__stage=Round.STAGE_PRELIMINARY).select_related(
                'adjudicator', 'adjudicator__institution', 'source_adjudicator__debate__round')

    def get_expected_trackers(self):
        """Trackers are as follows:
          - Chairs owe on everyone in their panel.
          - Panellists owe on chairs if the relevant tournament preference is enabled.
        """
        debateadjs = self.adjudicator.debateadjudicator_set.filter(
                debate__ballotsubmission__confirmed=True,
                debate__round__stage=Round.STAGE_PRELIMINARY).select_related(
                'debate', 'debate__round')

        if len(debateadjs) == 0:
            return []

        # TODO re-incorporate this in
        # panellist_feedback_enabled = debateadjs[0].debate.round.tournament.pref('panellist_feedback_enabled')
        populate_allocations([da.debate for da in debateadjs])

        trackers = []
        for debateadj in debateadjs:
            # TODO this is hard-coded for Australs 2016, need to make general
            adjudicators = debateadj.debate.adjudicators
            if debateadj.type == DebateAdjudicator.TYPE_CHAIR:
                for target in adjudicators.all(): # including trainees
                    if target == self.adjudicator:
                        continue
                    trackers.append(FeedbackExpectedSubmissionFromAdjudicatorTracker(debateadj, target))
            elif debateadj.type == DebateAdjudicator.TYPE_PANEL:
                for target in adjudicators.voting(): # excluding trainees
                    if target == self.adjudicator:
                        continue
                    trackers.append(FeedbackExpectedSubmissionFromAdjudicatorTracker(debateadj, target))
            elif debateadj.type == DebateAdjudicator.TYPE_TRAINEE:
                trackers.append(FeedbackExpectedSubmissionFromAdjudicatorTracker(debateadj, adjudicators.chair))

        self._prefetch_tracker_acceptable_submissions(trackers,
                attrgetter('source', 'target'), attrgetter('source_adjudicator', 'adjudicator'))

        return trackers
