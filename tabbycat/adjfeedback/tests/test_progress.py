from django.test import TestCase

from adjallocation.models import DebateAdjudicator
from draw.models import Debate, DebateTeam
from participants.models import Adjudicator, Institution, Speaker, Team
from results.models import BallotSubmission
from results.result import BallotSet
from tournaments.models import Round, Tournament
from venues.models import Venue

from ..models import AdjudicatorFeedback
from ..progress import FeedbackExpectedSubmissionFromAdjudicatorTracker, FeedbackExpectedSubmissionFromTeamTracker


class TestFeedbackProgressSimple(TestCase):

    #        ((teams), (adjs)),   ((teams), (adjs)),   ((teams), (adjs))
    # draw = [[((0, 1), (0, 1, 2)), ((2, 3), (3, 4, 5)), ((4, 5), (6))],
    #         [((0, 3), (4)),       ((2, 4), (0, 3, 6)), ((1, 5), (2))],
    #         [((0, 5), (3, 1, 6)), ((1, 2), (5, 0, 2)), ((3, 4), (4))],
    #         [((0, 2), (6, 5, 4)), ((1, 4), (3)),       ((3, 5), (1))]]

    def setUp(self):
        self.t = Tournament.objects.create()
        for i in range(6):
            inst = Institution.objects.create(code=i, name=i)
            team = Team.objects.create(tournament=self.t, institution=inst, reference=i)
            for j in range(3):
                Speaker.objects.create(team=team, name="%d-%d" % (i, j))

        adjsinst = Institution.objects.create(code="Adjs", name="Adjudicators")
        for i in range(7):
            Adjudicator.objects.create(tournament=self.t, institution=adjsinst, name=i)
        for i in range(3):
            Venue.objects.create(name=i, priority=i)

        self.rd = Round.objects.create(tournament=self.t, seq=1, abbreviation="R1")

    def _team(self, t):
        return Team.objects.get(tournament=self.t, reference=t)

    def _adj(self, a):
        return Adjudicator.objects.get(tournament=self.t, name=a)

    def _dt(self, debate, t):
        return DebateTeam.objects.get(debate=debate, team=self._team(t))

    def _da(self, debate, a):
        return DebateAdjudicator.objects.get(debate=debate, adjudicator=self._adj(a))

    def _create_debate(self, teams, adjs, votes, trainees=[], venue=None):
        if venue is None:
            venue = Venue.objects.first()
        debate = Debate.objects.create(round=self.rd, venue=venue)

        aff, neg = teams
        aff_team = self._team(aff)
        DebateTeam.objects.create(debate=debate, team=aff_team, position=DebateTeam.POSITION_AFFIRMATIVE)
        neg_team = self._team(neg)
        DebateTeam.objects.create(debate=debate, team=neg_team, position=DebateTeam.POSITION_NEGATIVE)

        chair = self._adj(adjs[0])
        DebateAdjudicator.objects.create(debate=debate, adjudicator=chair,
                type=DebateAdjudicator.TYPE_CHAIR)
        for p in adjs[1:]:
            panellist = self._adj(p)
            DebateAdjudicator.objects.create(debate=debate, adjudicator=panellist,
                    type=DebateAdjudicator.TYPE_PANEL)
        for tr in trainees:
            trainee = self._adj(tr)
            DebateAdjudicator.objects.create(debate=debate, adjudicator=trainee,
                    type=DebateAdjudicator.TYPE_TRAINEE)

        ballotsub = BallotSubmission(debate=debate, submitter_type=BallotSubmission.SUBMITTER_TABROOM)
        ballotset = BallotSet(ballotsub)

        for t in teams:
            team = self._team(t)
            speakers = team.speaker_set.all()
            for pos, speaker in enumerate(speakers, start=1):
                ballotset.set_speaker(team, pos, speaker)
            ballotset.set_speaker(team, 4, speakers[0])

        for a, vote in zip(adjs, votes):
            adj = self._adj(a)
            if vote == 'a':
                teams = [aff_team, neg_team]
            elif vote == 'n':
                teams = [neg_team, aff_team]
            else:
                raise ValueError
            for team, score in zip(teams, (76, 74)):
                for pos in range(1, 4):
                    ballotset.set_score(adj, team, pos, score)
                ballotset.set_score(adj, team, 4, score / 2)

        ballotset.confirmed = True
        ballotset.save()

        return debate

    def _create_feedback(self, source, target):
        if isinstance(source, DebateTeam):
            source_kwargs = dict(source_team=source)
        else:
            source_kwargs = dict(source_adjudicator=source)
        return AdjudicatorFeedback.objects.create(confirmed=True, adjudicator=target, score=3,
                **source_kwargs)

    def test_chair_oral_no_submission(self):
        debate = self._create_debate((0, 1), (0, 1, 2), "aan")
        for t in (0, 1):
            tracker = FeedbackExpectedSubmissionFromTeamTracker(self._dt(debate, t))
            self.assertIs(tracker.expected, True)
            self.assertIs(tracker.fulfilled, False)
            self.assertEqual(tracker.count, 0)
            self.assertCountEqual(tracker.related_submissions(), [])
            self.assertCountEqual(tracker.acceptable_targets(), [self._adj(0)])

    def test_chair_oral_good_submission(self):
        debate = self._create_debate((0, 1), (0, 1, 2), "aan")
        for t in (0, 1):
            feedback = self._create_feedback(self._dt(debate, t), self._adj(0))
            tracker = FeedbackExpectedSubmissionFromTeamTracker(self._dt(debate, t))
            self.assertIs(tracker.expected, True)
            self.assertIs(tracker.fulfilled, True)
            self.assertEqual(tracker.count, 1)
            self.assertCountEqual(tracker.related_submissions(), [feedback])
            self.assertCountEqual(tracker.acceptable_targets(), [self._adj(0)])

    def test_chair_oral_bad_submission(self):
        debate = self._create_debate((0, 1), (0, 1, 2), "aan")
        for t in (0, 1):
            feedback = self._create_feedback(self._dt(debate, t), self._adj(1))
            tracker = FeedbackExpectedSubmissionFromTeamTracker(self._dt(debate, t))
            self.assertIs(tracker.expected, True)
            self.assertIs(tracker.fulfilled, False)
            self.assertEqual(tracker.count, 1)
            self.assertCountEqual(tracker.related_submissions(), [feedback])
            self.assertCountEqual(tracker.acceptable_targets(), [self._adj(0)])

    def test_chair_oral_multiple_submissions(self):
        debate = self._create_debate((0, 1), (0, 1, 2), "aan")
        for t in (0, 1):
            feedback1 = self._create_feedback(self._dt(debate, t), self._adj(0))
            feedback2 = self._create_feedback(self._dt(debate, t), self._adj(1))
            tracker = FeedbackExpectedSubmissionFromTeamTracker(self._dt(debate, t))
            self.assertIs(tracker.expected, True)
            self.assertIs(tracker.fulfilled, False)
            self.assertEqual(tracker.count, 2)
            self.assertCountEqual(tracker.related_submissions(), [feedback1, feedback2])
            self.assertCountEqual(tracker.acceptable_targets(), [self._adj(0)])

    def test_chair_rolled_no_submission(self):
        debate = self._create_debate((0, 1), (0, 1, 2), "ann")
        for t in (0, 1):
            tracker = FeedbackExpectedSubmissionFromTeamTracker(self._dt(debate, t))
            self.assertIs(tracker.expected, True)
            self.assertIs(tracker.fulfilled, False)
            self.assertEqual(tracker.count, 0)
            self.assertCountEqual(tracker.related_submissions(), [])
            self.assertCountEqual(tracker.acceptable_targets(), [self._adj(1), self._adj(2)])

    def test_chair_rolled_good_submission(self):
        debate = self._create_debate((0, 1), (0, 1, 2), "ann")
        for t in (0, 1):
            tracker = FeedbackExpectedSubmissionFromTeamTracker(self._dt(debate, t))
            feedback = self._create_feedback(self._dt(debate, t), self._adj(1))
            self.assertIs(tracker.expected, True)
            self.assertIs(tracker.fulfilled, True)
            self.assertEqual(tracker.count, 1)
            self.assertCountEqual(tracker.related_submissions(), [feedback])
            self.assertCountEqual(tracker.acceptable_targets(), [self._adj(1), self._adj(2)])

    def test_chair_rolled_bad_submission(self):
        debate = self._create_debate((0, 1), (0, 1, 2), "ann")
        for t in (0, 1):
            tracker = FeedbackExpectedSubmissionFromTeamTracker(self._dt(debate, t))
            feedback = self._create_feedback(self._dt(debate, t), self._adj(0))
            self.assertIs(tracker.expected, True)
            self.assertIs(tracker.fulfilled, False)
            self.assertEqual(tracker.count, 1)
            self.assertCountEqual(tracker.related_submissions(), [feedback])
            self.assertCountEqual(tracker.acceptable_targets(), [self._adj(1), self._adj(2)])

    def test_chair_rolled_multiple_submissions(self):
        debate = self._create_debate((0, 1), (0, 1, 2), "ann")
        for t in (0, 1):
            feedback1 = self._create_feedback(self._dt(debate, t), self._adj(1))
            feedback2 = self._create_feedback(self._dt(debate, t), self._adj(2))
            tracker = FeedbackExpectedSubmissionFromTeamTracker(self._dt(debate, t))
            self.assertIs(tracker.expected, True)
            self.assertIs(tracker.fulfilled, False)
            self.assertEqual(tracker.count, 2)
            self.assertCountEqual(tracker.related_submissions(), [feedback1, feedback2])
            self.assertCountEqual(tracker.acceptable_targets(), [self._adj(1), self._adj(2)])

    def test_sole_adjudicator_no_submissions(self):
        debate = self._create_debate((0, 1), (0,), "n")
        for t in (0, 1):
            tracker = FeedbackExpectedSubmissionFromTeamTracker(self._dt(debate, t))
            self.assertIs(tracker.expected, True)
            self.assertIs(tracker.fulfilled, False)
            self.assertEqual(tracker.count, 0)
            self.assertCountEqual(tracker.related_submissions(), [])
            self.assertCountEqual(tracker.acceptable_targets(), [self._adj(0)])

    def test_sole_adjudicator_good_submission(self):
        debate = self._create_debate((0, 1), (0,), "n")
        for t in (0, 1):
            tracker = FeedbackExpectedSubmissionFromTeamTracker(self._dt(debate, t))
            feedback = self._create_feedback(self._dt(debate, t), self._adj(0))
            self.assertIs(tracker.expected, True)
            self.assertIs(tracker.fulfilled, True)
            self.assertEqual(tracker.count, 1)
            self.assertCountEqual(tracker.related_submissions(), [feedback])
            self.assertCountEqual(tracker.acceptable_targets(), [self._adj(0)])

    def test_sole_adjudicator_bad_submission(self):
        debate = self._create_debate((0, 1), (0,), "n")
        for t in (0, 1):
            tracker = FeedbackExpectedSubmissionFromTeamTracker(self._dt(debate, t))
            feedback = self._create_feedback(self._dt(debate, t), self._adj(3))
            self.assertIs(tracker.expected, True)
            self.assertIs(tracker.fulfilled, False)
            self.assertEqual(tracker.count, 1)
            self.assertCountEqual(tracker.related_submissions(), [feedback])
            self.assertCountEqual(tracker.acceptable_targets(), [self._adj(0)])

    def test_sole_adjudicator_multiple_submissions(self):
        debate = self._create_debate((0, 1), (0,), "n")
        for t in (0, 1):
            tracker = FeedbackExpectedSubmissionFromTeamTracker(self._dt(debate, t))
            feedback1 = self._create_feedback(self._dt(debate, t), self._adj(0))
            feedback2 = self._create_feedback(self._dt(debate, t), self._adj(3))
            feedback3 = self._create_feedback(self._dt(debate, t), self._adj(4))
            self.assertIs(tracker.expected, True)
            self.assertIs(tracker.fulfilled, False)
            self.assertEqual(tracker.count, 3)
            self.assertCountEqual(tracker.related_submissions(), [feedback1, feedback2, feedback3])
            self.assertCountEqual(tracker.acceptable_targets(), [self._adj(0)])

    def test_adj_on_adj_no_submission(self):
        debate = self._create_debate((0, 1), (0, 1, 2), "aan")
        for a in (1, 2):
            tracker = FeedbackExpectedSubmissionFromAdjudicatorTracker(self._da(debate, 0), self._adj(a))
            self.assertIs(tracker.expected, True)
            self.assertIs(tracker.fulfilled, False)
            self.assertEqual(tracker.count, 0)
            self.assertCountEqual(tracker.related_submissions(), [])
            self.assertCountEqual(tracker.acceptable_targets(), [self._adj(a)])

    def test_adj_on_adj_good_submission(self):
        debate = self._create_debate((0, 1), (0, 1, 2), "aan")
        for a in (1, 2):
            tracker = FeedbackExpectedSubmissionFromAdjudicatorTracker(self._da(debate, 0), self._adj(a))
            feedback = self._create_feedback(self._da(debate, 0), self._adj(a))
            self.assertIs(tracker.expected, True)
            self.assertIs(tracker.fulfilled, True)
            self.assertEqual(tracker.count, 1)
            self.assertCountEqual(tracker.related_submissions(), [feedback])
            self.assertCountEqual(tracker.acceptable_targets(), [self._adj(a)])

    def test_adj_on_adj_bad_submission(self):
        debate = self._create_debate((0, 1), (0, 1, 2), "aan")
        for a in (1, 2):
            tracker = FeedbackExpectedSubmissionFromAdjudicatorTracker(self._da(debate, 0), self._adj(a))
            self._create_feedback(self._da(debate, 0), self._adj(4))
            self.assertIs(tracker.expected, True)
            self.assertIs(tracker.fulfilled, False)
            self.assertEqual(tracker.count, 0) # it's not "related" when on a different judge
            self.assertCountEqual(tracker.related_submissions(), [])
            self.assertCountEqual(tracker.acceptable_targets(), [self._adj(a)])

    def test_adj_on_adj_multiple_submission(self):
        debate = self._create_debate((0, 1), (0, 1, 2), "aan")
        for a in (1, 2):
            tracker = FeedbackExpectedSubmissionFromAdjudicatorTracker(self._da(debate, 0), self._adj(a))
            self._create_feedback(self._da(debate, 0), self._adj(a))
            feedback2 = self._create_feedback(self._da(debate, 0), self._adj(a))
            self.assertIs(tracker.expected, True)
            self.assertIs(tracker.fulfilled, True) # the old one would be set to unconfirmed
            self.assertEqual(tracker.count, 1)
            self.assertCountEqual(tracker.related_submissions(), [feedback2])
            self.assertCountEqual(tracker.acceptable_targets(), [self._adj(a)])
