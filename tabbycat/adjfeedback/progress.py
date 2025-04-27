"""Utilities to compute which feedback has been submitted and not submitted
by participants of the tournament.

The calculations are based around individual "trackers", each one representing
one expected piece of feedback, or an unexpected piece of feedback if there is
one. Each tracker reports whether is expected, submitted and fulfilled. Then,
instances of aggregation classes (subclasses of BaseFeedbackProgress)
instantiate a collection of trackers for a particular source (team or
adjudicator).
 """

import logging
from operator import attrgetter

from django.db.models import Count, F, Q

from adjallocation.models import DebateAdjudicator
from adjfeedback.models import AdjudicatorFeedback
from results.prefetch import populate_confirmed_ballots
from tournaments.models import Round

from .utils import expected_feedback_targets

logger = logging.getLogger(__name__)


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

    def acceptable_target_names(self):
        return [adj.get_public_name(self.round.tournament) for adj in self.acceptable_targets()]


class FeedbackExpectedSubmissionFromTeamTracker(BaseFeedbackExpectedSubmissionTracker):
    """Represents a single piece of expected feedback from a team on any valid
    adjudicator in a panel."""

    def __init__(self, source, enforce_orallist=True):
        self.enforce_orallist = enforce_orallist
        return super().__init__(source)

    def acceptable_targets(self):
        """For a team, this must be the adjudicator who delivered the oral
        adjudication. If the chair was rolled, then it is one of the majority
        adjudicators; if the chair was in the majority, then it must be the
        chair.

        For consensus adjudications and where information about splitting
        adjudicators is not shown publicly, the above-described rule can't be
        enforced, so instead we just expect it to be on any adjudicator on the
        panel."""

        if self.enforce_orallist and self.source.debate.confirmed_ballot:
            majority = self.source.debate.confirmed_ballot.result.majority_adjudicators()
            chair = self.source.debate.adjudicators.chair
            if chair in majority:
                return [chair]
            else:
                return majority

        else:
            return list(self.source.debate.adjudicators.voting())

    def get_acceptable_submissions(self):
        return self.source.adjudicatorfeedback_set.filter(confirmed=True,
                source_team=self.source,
                adjudicator__in=self.acceptable_targets()).select_related(
                'source_team', 'adjudicator', 'adjudicator__institution')


class FeedbackExpectedSubmissionFromTeamOnSingleAdjudicatorTracker(BaseFeedbackExpectedSubmissionTracker):
    """Represents a single piece of expected feedback from a team on a single
    adjudicator."""

    def __init__(self, source, target=None):
        self.target = target
        return super().__init__(source)

    def acceptable_targets(self):
        return [self.target]

    def get_acceptable_submissions(self):
        return self.source.adjudicatorfeedback_set.filter(confirmed=True,
                source_team=self.source, adjudicator=self.target).select_related(
                'source_team', 'adjudicator', 'adjudicator__institution')


class FeedbackExpectedSubmissionFromAdjudicatorTracker(BaseFeedbackExpectedSubmissionTracker):
    """Represents a single piece of expected feedback from an adjudicator."""

    def __init__(self, source, target):
        self.target = target
        return super().__init__(source)

    def acceptable_targets(self):
        return [self.target]

    def get_acceptable_submissions(self):
        return self.source.adjudicatorfeedback_set.filter(confirmed=True,
                source_adjudicator=self.source, adjudicator=self.target).select_related(
                'source_adjudicator', 'adjudicator', 'adjudicator__institution')


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

    def __init__(self, tournament):
        self.show_unexpected = tournament.pref('show_unexpected_feedback')

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
        if self.show_unexpected:
            return [FeedbackUnexpectedSubmissionTracker(feedback) for feedback in
                self.submitted_feedback() if feedback not in self.expected_feedback()]
        else:
            return []

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

    def __init__(self, team, tournament=None):
        self.team = team
        if tournament is None:
            tournament = team.tournament
        self.enforce_orallist = (tournament.pref("show_splitting_adjudicators") and
                                 tournament.pref("ballots_per_debate_prelim") == 'per-adj')
        self.expect_orallists = tournament.pref("feedback_from_teams") in ['orallist', 'all-adjs']
        self.expect_all_adjs = tournament.pref("feedback_from_teams") == 'all-adjs'
        super().__init__(tournament)

    @staticmethod
    def _submitted_feedback_queryset_operations(queryset):
        # this is also used by get_feedback_progress
        return queryset.filter(confirmed=True,
            source_team__debate__round__stage=Round.Stage.PRELIMINARY).select_related(
            'adjudicator', 'adjudicator__institution', 'source_team__debate__round')

    def get_submitted_feedback(self):
        queryset = AdjudicatorFeedback.objects.filter(source_team__team=self.team)
        return self._submitted_feedback_queryset_operations(queryset)

    @staticmethod
    def _debateteam_queryset_operations(queryset):
        # this is also used by get_feedback_progress
        debateteams = queryset.filter(
            debate__ballotsubmission__confirmed=True,
            debate__round__silent=False,
            debate__round__stage=Round.Stage.PRELIMINARY,
        ).select_related('debate', 'debate__round').prefetch_related(
            'debate__debateadjudicator_set__adjudicator')
        populate_confirmed_ballots([dt.debate for dt in debateteams], results=True)
        return debateteams

    def _get_debateteams(self):
        if not hasattr(self, '_debateteams'):
            self._debateteams = self._debateteam_queryset_operations(self.team.debateteam_set)
        return self._debateteams

    def get_expected_trackers(self):
        debateteams = self._get_debateteams()
        if self.expect_all_adjs:
            # If teams submit on all adjudicators, there is one tracker for each
            # adjudicator in each debate for which there is a confirmed ballot
            # and the round is not silent.
            trackers = [FeedbackExpectedSubmissionFromTeamOnSingleAdjudicatorTracker(dt, adj)
                        for dt in debateteams
                        for adj in dt.debate.adjudicators.all()]
            self._prefetch_tracker_acceptable_submissions(trackers,
                    attrgetter('source', 'target'),
                    attrgetter('source_team', 'adjudicator'))

        elif self.expect_orallists:
            # If teams submit only on orallists, there is one tracker for each
            # debate for which there is a confirmed ballot, and the round is not
            # silent.
            trackers = [FeedbackExpectedSubmissionFromTeamTracker(dt, self.enforce_orallist)
                        for dt in debateteams]
            self._prefetch_tracker_acceptable_submissions(trackers,
                        attrgetter('source'), attrgetter('source_team'))
        else:
            trackers = []

        return trackers


class FeedbackProgressForAdjudicator(BaseFeedbackProgress):
    """Class to compute feedback submitted or owed by an adjudicator."""

    def __init__(self, adjudicator, tournament=None):
        self.adjudicator = adjudicator
        if tournament is None:
            tournament = adjudicator.tournament
        if tournament is None:
            logger.warning("No tournament specified and adjudicator %s has no tournament", adjudicator)
        else:
            self.feedback_paths = tournament.pref('feedback_paths')
        super().__init__(tournament)

    @staticmethod
    def _submitted_feedback_queryset_operations(queryset):
        # this is also used by get_feedback_progress
        return queryset.filter(confirmed=True,
            source_adjudicator__debate__round__stage=Round.Stage.PRELIMINARY).select_related(
            'adjudicator', 'adjudicator__institution', 'source_adjudicator__debate__round')

    def get_submitted_feedback(self):
        queryset = AdjudicatorFeedback.objects.filter(source_adjudicator__adjudicator=self.adjudicator)
        return self._submitted_feedback_queryset_operations(queryset)

    @staticmethod
    def _debateadjudicator_queryset_operations(queryset):
        # this is also used by get_feedback_progress
        return queryset.filter(
            debate__ballotsubmission__confirmed=True,
            debate__round__stage=Round.Stage.PRELIMINARY,
        ).select_related('debate', 'debate__round').prefetch_related(
            'debate__debateadjudicator_set__adjudicator')

    def _get_debateadjudicators(self):
        if not hasattr(self, '_debateadjudicators'):
            self._debateadjudicators = self._debateadjudicator_queryset_operations(self.adjudicator.debateadjudicator_set)
        return self._debateadjudicators

    def get_expected_trackers(self):
        """Trackers are as follows:
          - Chairs owe on everyone in their panel.
          - Panellists owe on chairs if the relevant tournament preference is enabled.
        """
        debateadjs = self._get_debateadjudicators()

        trackers = []
        for debateadj in debateadjs:
            for target, _ in expected_feedback_targets(debateadj, self.feedback_paths):
                trackers.append(FeedbackExpectedSubmissionFromAdjudicatorTracker(debateadj, target))

        self._prefetch_tracker_acceptable_submissions(trackers,
                attrgetter('source', 'target'), attrgetter('source_adjudicator', 'adjudicator'))

        return trackers


def get_feedback_progress_statistics(tournament):
    """Returns a tuple ([Team], [Adjudicator]), with statistics of the number
    of feedback submitted, missing, and expected. Using Progress objects would
    be too costly for use when only aggregate statistics are needed."""

    if tournament.pref('feedback_from_teams') == 'orallist':
        teams_expected_filter = Q(debateteam__debate__debateadjudicator__type=DebateAdjudicator.TYPE_CHAIR)
    else:  # 'all-adjs'
        teams_expected_filter = Q()
    teams = tournament.team_set.annotate(
        num_submitted=Count('debateteam__adjudicatorfeedback', filter=Q(debateteam__adjudicatorfeedback__confirmed=True)),
    ).prefetch_related('speaker_set').all()
    by_team_id = {t.id: t for t in teams}
    ts = tournament.team_set.filter(id__in=by_team_id.keys()).annotate(
        num_expected=Count('debateteam__debate__debateadjudicator', filter=Q(
            debateteam__debate__round__stage=Round.STAGE_PRELIMINARY,
            debateteam__debate__round__silent=False,
            debateteam__debate__ballotsubmission__confirmed=True,
        ) & teams_expected_filter))
    for t in ts.all():
        o_t = by_team_id[t.id]
        o_t.num_expected = t.num_expected
        o_t.num_missing = t.num_expected - o_t.num_submitted

    adjudicators = tournament.adjudicator_set.annotate(
        num_submitted=Count('debateadjudicator__adjudicatorfeedback', filter=Q(debateadjudicator__adjudicatorfeedback__confirmed=True)),
    ).all()
    by_adj_id = {adj.id: adj for adj in adjudicators}

    exclude_self_filter = ~Q(debateadjudicator__debate__debateadjudicator__adjudicator_id=F('id'))
    when_chair_filter = Q(debateadjudicator__type=DebateAdjudicator.TYPE_CHAIR)
    adj_expected_filter = {
        'minimal': when_chair_filter,
        'with-t-on-c': ~Q(debateadjudicator__type=DebateAdjudicator.TYPE_CHAIR) & Q(
            debateadjudicator__debate__debateadjudicator__type=DebateAdjudicator.TYPE_CHAIR,
        ) | when_chair_filter,
        'with-p-on-c': Q(
            debateadjudicator__type=DebateAdjudicator.TYPE_PANEL,
            debateadjudicator__debate__debateadjudicator__type=DebateAdjudicator.TYPE_CHAIR,
        ) | when_chair_filter,
        'all-adjs': Q(),
    }[tournament.pref('feedback_paths')]
    adjs = tournament.adjudicator_set.filter(id__in=by_adj_id.keys()).annotate(
        num_expected=Count('debateadjudicator__debate__debateadjudicator', filter=Q(
            debateadjudicator__debate__round__stage=Round.STAGE_PRELIMINARY,
            debateadjudicator__debate__ballotsubmission__confirmed=True,
        ) & exclude_self_filter & adj_expected_filter),
    ).all()
    for adj in adjs:
        o_adj = by_adj_id[adj.id]
        o_adj.num_expected = adj.num_expected
        o_adj.num_missing = adj.num_expected - o_adj.num_submitted

    return by_team_id.values(), by_adj_id.values()
