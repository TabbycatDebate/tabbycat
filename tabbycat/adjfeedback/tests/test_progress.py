import logging

from django.test import TestCase

from adjallocation.models import DebateAdjudicator
from adjfeedback.models import AdjudicatorFeedback
from draw.models import Debate, DebateTeam
from draw.types import DebateSide
from participants.models import Adjudicator, Institution, Speaker, Team
from results.models import BallotSubmission
from results.result import DebateResultByAdjudicatorWithScores
from tournaments.models import Round, Tournament
from utils.tests import suppress_logs
from venues.models import Venue

from ..progress import FeedbackExpectedSubmissionFromAdjudicatorTracker, FeedbackExpectedSubmissionFromTeamTracker
from ..progress import FeedbackProgressForAdjudicator, FeedbackProgressForTeam, get_feedback_progress


class TestFeedbackProgress(TestCase):

    NUM_TEAMS = 6
    NUM_ADJS = 7
    NUM_VENUES = 3

    def setUp(self):
        self.tournament = Tournament.objects.create()
        for i in range(self.NUM_TEAMS):
            inst = Institution.objects.create(code=i, name=i)
            team = Team.objects.create(tournament=self.tournament, institution=inst, reference=i)
            for j in range(3):
                Speaker.objects.create(team=team, name="%d-%d" % (i, j))

        adjsinst = Institution.objects.create(code="Adjs", name="Adjudicators")
        for i in range(self.NUM_ADJS):
            Adjudicator.objects.create(tournament=self.tournament, institution=adjsinst, name=i)
        for i in range(self.NUM_VENUES):
            Venue.objects.create(name=i, priority=i)

        self.rd = Round.objects.create(tournament=self.tournament, seq=1, schedule_group=1, abbreviation="R1")

    def tearDown(self):
        DebateTeam.objects.all().delete()
        Institution.objects.all().delete()
        Venue.objects.all().delete()
        self.tournament.delete()

    # These shouldn't use the related managers (e.g. `self.tournament.team_set`),
    # because the teams and adjudicators change often and the related managers
    # won't be updated to account for that.

    def _team(self, t):
        return Team.objects.get(tournament=self.tournament, reference=t)

    def _adj(self, a):
        return Adjudicator.objects.get(tournament=self.tournament, name=a)

    def _dt(self, debate, t):
        return DebateTeam.objects.get(debate=debate, team=self._team(t))

    def _da(self, debate, a):
        return DebateAdjudicator.objects.get(debate=debate, adjudicator=self._adj(a))

    def _create_elim_round(self):
        return Round.objects.create(tournament=self.tournament, seq=2, schedule_group=1,
                abbreviation="EF", stage=Round.Stage.ELIMINATION)

    def _create_debate(self, teams, adjs, votes, trainees=[], venue=None, rd=None):
        """Enters a debate into the database, using the teams and adjudicators specified.
        `votes` should be a string (or iterable of characters) indicating "a" for affirmative or
            "n" for negative, e.g. "ann" if the chair was rolled in a decision for the negative.
        The method will give the winning team all 76s and the losing team all 74s.
        The first adjudicator is the chair; the rest are panellists."""

        if venue is None:
            venue = Venue.objects.first()
        debate = Debate.objects.create(round=rd or self.rd, venue=venue)

        aff, neg = teams
        aff_team = self._team(aff)
        DebateTeam.objects.create(debate=debate, team=aff_team, side=0)
        neg_team = self._team(neg)
        DebateTeam.objects.create(debate=debate, team=neg_team, side=1)

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

        ballotsub = BallotSubmission(debate=debate, submitter_type=BallotSubmission.Submitter.TABROOM)
        result = DebateResultByAdjudicatorWithScores(ballotsub)

        for t, side in zip(teams, (DebateSide.AFF, DebateSide.NEG)):
            team = self._team(t)
            speakers = team.speaker_set.all()
            for pos, speaker in enumerate(speakers, start=1):
                result.set_speaker(side, pos, speaker)
                result.set_ghost(side, pos, False)
            result.set_speaker(side, 4, speakers[0])
            result.set_ghost(side, 4, False)

        for a, vote in zip(adjs, votes):
            adj = self._adj(a)
            if vote == 'a':
                sides = (DebateSide.AFF, DebateSide.NEG)
            elif vote == 'n':
                sides = (DebateSide.NEG, DebateSide.AFF)
            else:
                raise ValueError
            for side, score in zip(sides, (76, 74)):
                for pos in range(1, 4):
                    result.set_score(adj, side, pos, score)
                result.set_score(adj, side, 4, score / 2)

        ballotsub.confirmed = True
        ballotsub.save()
        result.save()

        return debate

    def _create_feedback(self, source, target, confirmed=True, ignored=False):
        if isinstance(source, DebateTeam):
            source_kwargs = dict(source_team=source)
        else:
            source_kwargs = dict(source_adjudicator=source)
        target_adj = self._adj(target)
        return AdjudicatorFeedback.objects.create(confirmed=confirmed, ignored=ignored, adjudicator=target_adj, score=3,
                **source_kwargs)

    # ==========================================================================
    # From team
    # ==========================================================================

    def assertExpectedFromTeamTracker(self, debate, t, expected, fulfilled, count, submissions, targets, tracker_kwargs={}): # noqa
        tracker = FeedbackExpectedSubmissionFromTeamTracker(self._dt(debate, t), **tracker_kwargs)
        self.assertIs(tracker.expected, expected)
        self.assertIs(tracker.fulfilled, fulfilled)
        self.assertEqual(tracker.count, count)
        self.assertCountEqual(tracker.acceptable_submissions(), submissions)
        self.assertCountEqual(tracker.acceptable_targets(), [self._adj(a) for a in targets])

    def test_chair_oral_no_submission(self):
        debate = self._create_debate((0, 1), (0, 1, 2), "aan")
        for t in (0, 1):
            self.assertExpectedFromTeamTracker(debate, t, True, False, 0, [], [0])

    def test_chair_oral_good_submission(self):
        debate = self._create_debate((0, 1), (0, 1, 2), "aan")
        for t in (0, 1):
            feedback = self._create_feedback(self._dt(debate, t), 0)
            self.assertExpectedFromTeamTracker(debate, t, True, True, 1, [feedback], [0])

    def test_chair_oral_bad_submission(self):
        debate = self._create_debate((0, 1), (0, 1, 2), "aan")
        for t in (0, 1):
            feedback = self._create_feedback(self._dt(debate, t), 1)
            self.assertExpectedFromTeamTracker(debate, t, True, False, 0, [], [0])
            self.assertExpectedFromTeamTracker(debate, t, True, True, 1, [feedback], [0, 1, 2], {'enforce_orallist': False})

    def test_chair_oral_multiple_submissions(self):
        self.tournament.preferences['feedback__feedback_from_teams'] = 'all-adjs'
        debate = self._create_debate((0, 1), (0, 1, 2), "aan")
        for t in (0, 1):
            feedback1 = self._create_feedback(self._dt(debate, t), 0)
            feedback2 = self._create_feedback(self._dt(debate, t), 1)
            # The submission on adj 1 is irrelevant, so shouldn't appear at all.
            # (It should appear as "unexpected" in the FeedbackProgressForTeam.)
            self.assertExpectedFromTeamTracker(debate, t, True, True, 1, [feedback1], [0])
            # If the orallist is not enforced, though, both submissions are relevant.
            self.assertExpectedFromTeamTracker(debate, t, True, False, 2, [feedback1, feedback2], [0, 1, 2], {'enforce_orallist': False})

    def test_chair_rolled_no_submission(self):
        debate = self._create_debate((0, 1), (0, 1, 2), "ann")
        for t in (0, 1):
            self.assertExpectedFromTeamTracker(debate, t, True, False, 0, [], [1, 2])

    def test_chair_rolled_good_submission(self):
        debate = self._create_debate((0, 1), (0, 1, 2), "ann")
        for t in (0, 1):
            feedback = self._create_feedback(self._dt(debate, t), 1)
            self.assertExpectedFromTeamTracker(debate, t, True, True, 1, [feedback], [1, 2])

    def test_chair_rolled_bad_submission(self):
        debate = self._create_debate((0, 1), (0, 1, 2), "ann")
        for t in (0, 1):
            feedback = self._create_feedback(self._dt(debate, t), 0)
            self.assertExpectedFromTeamTracker(debate, t, True, False, 0, [], [1, 2])
            self.assertExpectedFromTeamTracker(debate, t, True, True, 1, [feedback], [0, 1, 2], {'enforce_orallist': False})

    def test_chair_rolled_multiple_submissions(self):
        self.tournament.preferences['feedback__feedback_from_teams'] = 'all-adjs'
        debate = self._create_debate((0, 1), (0, 1, 2), "ann")
        for t in (0, 1):
            feedback1 = self._create_feedback(self._dt(debate, t), 1)
            feedback2 = self._create_feedback(self._dt(debate, t), 2)
            self.assertExpectedFromTeamTracker(debate, t, True, False, 2, [feedback1, feedback2], [1, 2])

    def test_sole_adjudicator_no_submissions(self):
        debate = self._create_debate((0, 1), (0,), "n")
        for t in (0, 1):
            self.assertExpectedFromTeamTracker(debate, t, True, False, 0, [], [0])

    def test_sole_adjudicator_good_submission(self):
        debate = self._create_debate((0, 1), (0,), "n")
        for t in (0, 1):
            feedback = self._create_feedback(self._dt(debate, t), 0)
            self.assertExpectedFromTeamTracker(debate, t, True, True, 1, [feedback], [0])

    def test_sole_adjudicator_bad_submission(self):
        debate = self._create_debate((0, 1), (0,), "n")
        for t in (0, 1):
            self._create_feedback(self._dt(debate, t), 3)
            self.assertExpectedFromTeamTracker(debate, t, True, False, 0, [], [0])

    def test_sole_adjudicator_multiple_submissions(self):
        self.tournament.preferences['feedback__feedback_from_teams'] = 'all-adjs'
        debate = self._create_debate((0, 1), (0,), "n")
        for t in (0, 1):
            feedback1 = self._create_feedback(self._dt(debate, t), 0)
            self._create_feedback(self._dt(debate, t), 3)
            self._create_feedback(self._dt(debate, t), 4)
            # The submissions on adjs 3 and 4 are irrelevant, so shouldn't appear at all.
            # (They should appear as "unexpected" in the FeedbackProgressForTeam.)
            self.assertExpectedFromTeamTracker(debate, t, True, True, 1, [feedback1], [0])
            self.assertExpectedFromTeamTracker(debate, t, True, True, 1, [feedback1], [0], {'enforce_orallist': False})

    def test_multiple_submissions_allowed_when_only_orallist_expected(self):
        self.tournament.preferences['feedback__feedback_from_teams'] = 'all-adjs-allowed'
        debate = self._create_debate((0, 1), (0, 1, 2), "aan")
        feedback1 = self._create_feedback(self._dt(debate, 0), 0)
        feedback2 = self._create_feedback(self._dt(debate, 0), 1)

        feedback1.refresh_from_db()
        self.assertTrue(feedback1.confirmed)
        self.assertTrue(feedback2.confirmed)

        progress = FeedbackProgressForTeam(self._team(0))
        self.assertEqual(progress.num_submitted(), 2)
        self.assertEqual(progress.num_expected(), 1)
        self.assertEqual(progress.num_fulfilled(), 1)

    # ==========================================================================
    # From adjudicator
    # ==========================================================================

    def assertExpectedFromAdjudicatorTracker(self, debate, source, target, expected, fulfilled, count, submissions): # noqa
        tracker = FeedbackExpectedSubmissionFromAdjudicatorTracker(self._da(debate, source), self._adj(target))
        self.assertIs(tracker.expected, expected)
        self.assertIs(tracker.fulfilled, fulfilled)
        self.assertEqual(tracker.count, count)
        self.assertCountEqual(tracker.acceptable_submissions(), submissions)
        self.assertCountEqual(tracker.acceptable_targets(), [self._adj(target)])

    def test_adj_on_adj_no_submission(self):
        debate = self._create_debate((0, 1), (0, 1, 2), "aan")
        for a in (1, 2):
            self.assertExpectedFromAdjudicatorTracker(debate, 0, a, True, False, 0, [])

    def test_adj_on_adj_good_submission(self):
        debate = self._create_debate((0, 1), (0, 1, 2), "aan")
        for a in (1, 2):
            feedback = self._create_feedback(self._da(debate, 0), a)
            self.assertExpectedFromAdjudicatorTracker(debate, 0, a, True, True, 1, [feedback])

    def test_adj_on_adj_bad_submission(self):
        debate = self._create_debate((0, 1), (0, 1, 2), "aan")
        for a in (1, 2):
            self._create_feedback(self._da(debate, 0), a+2)
            self.assertExpectedFromAdjudicatorTracker(debate, 0, a, True, False, 0, [])

    def test_submitted_feedback_ignored_score(self):
        debate = self._create_debate((0, 1), (0, 1, 2), "aan")
        for a in (1, 2):
            feedback = self._create_feedback(self._da(debate, 0), a, ignored=True)
            self.assertExpectedFromAdjudicatorTracker(debate, 0, a, True, True, 1, [feedback])

    def test_submitted_feedback_unconfirmed_score(self):
        debate = self._create_debate((0, 1), (0, 1, 2), "aan")
        for a in (1, 2):
            self._create_feedback(self._da(debate, 0), a, confirmed=False)
            self.assertExpectedFromAdjudicatorTracker(debate, 0, a, True, False, 0, [])

    def test_submitted_feedback_ignored_unconfirmed_score(self):
        debate = self._create_debate((0, 1), (0, 1, 2), "aan")
        for a in (1, 2):
            self._create_feedback(self._da(debate, 0), a, confirmed=False, ignored=True)
            self.assertExpectedFromAdjudicatorTracker(debate, 0, a, True, False, 0, [])

    def test_adj_on_adj_multiple_submission(self):
        debate = self._create_debate((0, 1), (0, 1, 2), "aan")
        for a in (1, 2):
            with suppress_logs('results.models', logging.WARNING):  # suppress duplicate confirmed warning
                self._create_feedback(self._da(debate, 0), a)
                feedback2 = self._create_feedback(self._da(debate, 0), a)
            self.assertExpectedFromAdjudicatorTracker(debate, 0, a, True, True, 1, [feedback2])

    def test_adj_on_adj_trainees_not_submitted(self):
        debate = self._create_debate((0, 1), (0,), "n", trainees=[4])
        self.assertExpectedFromAdjudicatorTracker(debate, 0, 4, True, False, 0, [])

    def test_adj_on_adj_trainees_submitted(self):
        debate = self._create_debate((0, 1), (0, 1, 2), "nan", trainees=[4])
        feedback = self._create_feedback(self._da(debate, 0), 4)
        self.assertExpectedFromAdjudicatorTracker(debate, 0, 4, True, True, 1, [feedback])

    # ==========================================================================
    # Team progress
    # ==========================================================================

    def _create_team_progress_dataset(self, adj1, adj2, adj3):
        debate1 = self._create_debate((0, 1), (0, 1, 2), "nnn")
        debate2 = self._create_debate((0, 2), (3, 4, 5), "ann")
        debate3 = self._create_debate((0, 3), (6,), "a")
        if adj1 is not None:
            self._create_feedback(self._dt(debate1, 0), adj1)
        if adj2 is not None:
            self._create_feedback(self._dt(debate2, 0), adj2)
        if adj3 is not None:
            self._create_feedback(self._dt(debate3, 0), adj3)

    def assertTeamProgress(self, feedback_policy, show_splits, t, submitted, # noqa
                           expected, fulfilled, unsubmitted, coverage):
        self.tournament.preferences['feedback__feedback_from_teams'] = feedback_policy
        self.tournament.preferences['ui_options__show_splitting_adjudicators'] = show_splits
        progress = FeedbackProgressForTeam(self._team(t))
        self.assertEqual(progress.num_submitted(), submitted)
        self.assertEqual(progress.num_expected(), expected)
        self.assertEqual(progress.num_fulfilled(), fulfilled)
        self.assertEqual(progress.num_unsubmitted(), unsubmitted)
        self.assertAlmostEqual(progress.coverage(), coverage)
        return progress

    def test_team_progress_all_good_orallist(self):
        self.tournament.preferences['feedback__feedback_from_teams'] = 'all-adjs'
        self._create_team_progress_dataset(0, 4, 6)
        self.assertTeamProgress('orallist', True, 0, 3, 3, 3, 0, 1.0)
        self.assertTeamProgress('orallist', False, 0, 3, 3, 3, 0, 1.0)
        self.assertTeamProgress('all-adjs-allowed', True, 0, 3, 3, 3, 0, 1.0)

    def test_team_progress_all_good_all_adjs(self):
        self.tournament.preferences['feedback__feedback_from_teams'] = 'all-adjs'
        debate1 = self._create_debate((0, 1), (0, 1, 2), "nnn")
        debate2 = self._create_debate((0, 2), (3, 4, 5), "ann")
        debate3 = self._create_debate((0, 3), (6,), "a")
        self._create_feedback(self._dt(debate1, 0), 0)
        self._create_feedback(self._dt(debate1, 0), 1)
        self._create_feedback(self._dt(debate1, 0), 2)
        self._create_feedback(self._dt(debate2, 0), 3)
        self._create_feedback(self._dt(debate2, 0), 4)
        self._create_feedback(self._dt(debate2, 0), 5)
        self._create_feedback(self._dt(debate3, 0), 6)
        self.assertTeamProgress('all-adjs', True, 0, 7, 7, 7, 0, 1.0)
        self.assertTeamProgress('all-adjs', False, 0, 7, 7, 7, 0, 1.0)

    def test_team_progress_all_voting_adjs_excludes_trainees(self):
        self.tournament.preferences['feedback__feedback_from_teams'] = 'all-adjs'
        debate = self._create_debate((0, 1), (0, 1, 2), "nnn", trainees=[3])
        for adj in (0, 1, 2, 3):
            self._create_feedback(self._dt(debate, 0), adj)
        progress = self.assertTeamProgress('all-voting-adjs', True, 0, 4, 3, 3, 0, 1.0)
        self.assertEqual(len(progress.unexpected_trackers()), 1)

    def test_team_progress_no_submissions(self):
        self.tournament.preferences['feedback__feedback_from_teams'] = 'all-adjs'
        self._create_team_progress_dataset(None, None, None)
        self.assertTeamProgress('orallist', True, 0, 0, 3, 0, 3, 0.0)
        self.assertTeamProgress('all-adjs', True, 0, 0, 7, 0, 7, 0.0)
        self.assertTeamProgress('orallist', False, 0, 0, 3, 0, 3, 0.0)
        self.assertTeamProgress('all-adjs', False, 0, 0, 7, 0, 7, 0.0)

    def test_team_progress_no_debates(self):
        self.tournament.preferences['feedback__feedback_from_teams'] = 'all-adjs'
        FeedbackProgressForTeam(self._team(4))
        self.assertTeamProgress('orallist', True, 4, 0, 0, 0, 0, 1.0)
        self.assertTeamProgress('all-adjs', True, 4, 0, 0, 0, 0, 1.0)

    def test_team_progress_missing_submission(self):
        self.tournament.preferences['feedback__feedback_from_teams'] = 'all-adjs'
        self._create_team_progress_dataset(0, None, 6)
        self.assertTeamProgress('orallist', True, 0, 2, 3, 2, 1, 2/3)
        self.assertTeamProgress('all-adjs', True, 0, 2, 7, 2, 5, 2/7)
        self.assertTeamProgress('orallist', False, 0, 2, 3, 2, 1, 2/3)
        self.assertTeamProgress('all-adjs', False, 0, 2, 7, 2, 5, 2/7)

    def test_team_progress_wrong_target_on_unanimous(self):
        self.tournament.preferences['feedback__feedback_from_teams'] = 'all-adjs'
        self._create_team_progress_dataset(2, 4, 6)
        progress = self.assertTeamProgress('orallist', True, 0, 3, 3, 2, 1, 2/3)
        self.assertEqual(len(progress.unexpected_trackers()), 1)
        progress = self.assertTeamProgress('orallist', False, 0, 3, 3, 3, 0, 1.0)
        self.assertEqual(len(progress.unexpected_trackers()), 0)

    def test_team_progress_wrong_target_on_rolled_chair(self):
        self.tournament.preferences['feedback__feedback_from_teams'] = 'all-adjs'
        self._create_team_progress_dataset(0, 3, 6)
        progress = self.assertTeamProgress('orallist', True, 0, 3, 3, 2, 1, 2/3)
        self.assertEqual(len(progress.unexpected_trackers()), 1)
        progress = self.assertTeamProgress('orallist', False, 0, 3, 3, 3, 0, 1.0)
        self.assertEqual(len(progress.unexpected_trackers()), 0)

    def test_team_progress_unexpected(self):
        self.tournament.preferences['feedback__feedback_from_teams'] = 'all-adjs'
        self._create_team_progress_dataset(5, 3, None)
        progress = self.assertTeamProgress('orallist', True, 0, 2, 3, 0, 3, 0.0)
        self.assertEqual(len(progress.unexpected_trackers()), 2)

        self.tournament.preferences['feedback__show_unexpected_feedback'] = False
        progress = self.assertTeamProgress('orallist', True, 0, 2, 3, 0, 3, 0.0)
        self.assertEqual(len(progress.unexpected_trackers()), 0)

    # ==========================================================================
    # Adjudicator progress
    # ==========================================================================

    def _create_adjudicator_progress_dataset(self, adjs1, adjs2, adjs3):
        debate1 = self._create_debate((0, 1), (0, 1, 2), "nnn")
        debate2 = self._create_debate((2, 3), (3, 0, 4), "ann")
        debate3 = self._create_debate((4, 0), (0,), "a")
        for adj in adjs1:
            self._create_feedback(self._da(debate1, 0), adj)
        for adj in adjs2:
            self._create_feedback(self._da(debate2, 0), adj)
        for adj in adjs3:
            self._create_feedback(self._da(debate3, 0), adj)

    def assertAdjudicatorProgress(self, feedback_paths, a, submitted, expected, fulfilled, unsubmitted, coverage): # noqa
        self.tournament.preferences['feedback__feedback_paths'] = feedback_paths
        progress = FeedbackProgressForAdjudicator(self._adj(a))
        self.assertEqual(progress.num_submitted(), submitted)
        self.assertEqual(progress.num_expected(), expected)
        self.assertEqual(progress.num_fulfilled(), fulfilled)
        self.assertEqual(progress.num_unsubmitted(), unsubmitted)
        self.assertAlmostEqual(progress.coverage(), coverage)
        return progress

    def test_adjudicator_progress_all_good(self):
        self._create_adjudicator_progress_dataset([1, 2], [3, 4], [])
        self.assertAdjudicatorProgress('minimal', 0, 4, 2, 2, 0, 1.0)
        self.assertAdjudicatorProgress('with-p-on-c', 0, 4, 3, 3, 0, 1.0)
        self.assertAdjudicatorProgress('all-adjs', 0, 4, 4, 4, 0, 1.0)

    def test_adjudicator_progress_missing_p_on_p(self):
        self._create_adjudicator_progress_dataset([1, 2], [3], [])
        self.assertAdjudicatorProgress('minimal', 0, 3, 2, 2, 0, 1.0)
        self.assertAdjudicatorProgress('with-p-on-c', 0, 3, 3, 3, 0, 1.0)
        self.assertAdjudicatorProgress('all-adjs', 0, 3, 4, 3, 1, 3/4)

    def test_adjudicator_progress_no_submissions(self):
        self._create_adjudicator_progress_dataset([], [], [])
        self.assertAdjudicatorProgress('minimal', 0, 0, 2, 0, 2, 0.0)
        self.assertAdjudicatorProgress('with-p-on-c', 0, 0, 3, 0, 3, 0.0)
        self.assertAdjudicatorProgress('all-adjs', 0, 0, 4, 0, 4, 0.0)

    def test_adjudicator_progress_no_debates(self):
        FeedbackProgressForAdjudicator(self._adj(5))
        self.assertAdjudicatorProgress('minimal', 5, 0, 0, 0, 0, 1.0)
        self.assertAdjudicatorProgress('with-p-on-c', 5, 0, 0, 0, 0, 1.0)
        self.assertAdjudicatorProgress('all-adjs', 5, 0, 0, 0, 0, 1.0)

    def test_adjudicator_progress_missing_submission(self):
        self._create_adjudicator_progress_dataset([1], [3], [])
        self.assertAdjudicatorProgress('minimal', 0, 2, 2, 1, 1, 1/2)
        self.assertAdjudicatorProgress('with-p-on-c', 0, 2, 3, 2, 1, 2/3)
        self.assertAdjudicatorProgress('all-adjs', 0, 2, 4, 2, 2, 1/2)

    def test_adjudicator_progress_wrong_target(self):
        self._create_adjudicator_progress_dataset([1, 2], [4], [])
        progress = self.assertAdjudicatorProgress('with-p-on-c', 0, 3, 3, 2, 1, 2/3)
        self.assertEqual(len(progress.unexpected_trackers()), 1)

    def test_adjudicator_progress_extra_target(self):
        self._create_adjudicator_progress_dataset([1, 2], [3, 4], [])
        progress = self.assertAdjudicatorProgress('with-p-on-c', 0, 4, 3, 3, 0, 1.0)
        self.assertEqual(len(progress.unexpected_trackers()), 1)

    def test_adjudicator_progress_unexpected(self):
        self._create_adjudicator_progress_dataset([5], [1], [2])
        progress = self.assertAdjudicatorProgress('with-p-on-c', 0, 3, 3, 0, 3, 0.0)
        self.assertEqual(len(progress.unexpected_trackers()), 3)

        self.tournament.preferences['feedback__show_unexpected_feedback'] = False
        progress = self.assertAdjudicatorProgress('with-p-on-c', 0, 3, 3, 0, 3, 0.0)
        self.assertEqual(len(progress.unexpected_trackers()), 0)

    # ==========================================================================
    # Round scope (preliminary vs elimination rounds)
    # ==========================================================================

    def _create_elim_scope_dataset(self):
        """One prelim debate and one elimination debate, each with feedback from
        team 0 and from adjudicator 0 on the whole panel."""
        elim = self._create_elim_round()
        prelim_debate = self._create_debate((0, 1), (0, 1, 2), "nnn")
        elim_debate = self._create_debate((0, 2), (0, 3, 4), "nnn", rd=elim)
        for debate, adjs in ((prelim_debate, (0, 1, 2)), (elim_debate, (0, 3, 4))):
            self._create_feedback(self._dt(debate, 0), adjs[0])
            for adj in adjs[1:]:
                self._create_feedback(self._da(debate, 0), adj)
        return prelim_debate, elim_debate

    def test_team_progress_scope_prelims_only(self):
        self._create_elim_scope_dataset()
        self.tournament.preferences['feedback__feedback_from_teams_rounds'] = 'prelims'
        self.assertTeamProgress('orallist', True, 0, 1, 1, 1, 0, 1.0)

    def test_team_progress_scope_all_rounds(self):
        self._create_elim_scope_dataset()
        self.tournament.preferences['feedback__feedback_from_teams_rounds'] = 'all'
        self.assertTeamProgress('orallist', True, 0, 2, 2, 2, 0, 1.0)

    def test_team_progress_scope_all_rounds_missing_elim_submission(self):
        elim = self._create_elim_round()
        prelim_debate = self._create_debate((0, 1), (0, 1, 2), "nnn")
        self._create_debate((0, 2), (3, 4, 5), "nnn", rd=elim)
        self._create_feedback(self._dt(prelim_debate, 0), 0)

        self.tournament.preferences['feedback__feedback_from_teams_rounds'] = 'prelims'
        self.assertTeamProgress('orallist', True, 0, 1, 1, 1, 0, 1.0)

        self.tournament.preferences['feedback__feedback_from_teams_rounds'] = 'all'
        self.assertTeamProgress('orallist', True, 0, 1, 2, 1, 1, 1/2)

    def test_team_progress_scope_excludes_silent_elim_rounds(self):
        elim = self._create_elim_round()
        elim.silent = True
        elim.save()
        self._create_debate((0, 1), (0, 1, 2), "nnn")
        self._create_debate((0, 2), (3, 4, 5), "nnn", rd=elim)

        self.tournament.preferences['feedback__feedback_from_teams_rounds'] = 'all'
        # The silent elimination round is not expected, in the same way that a
        # silent preliminary round is not.
        self.assertTeamProgress('orallist', True, 0, 0, 1, 0, 1, 0.0)

    def test_adjudicator_progress_scope_prelims_only(self):
        self._create_elim_scope_dataset()
        self.tournament.preferences['feedback__feedback_paths_rounds'] = 'prelims'
        self.assertAdjudicatorProgress('minimal', 0, 2, 2, 2, 0, 1.0)

    def test_adjudicator_progress_scope_all_rounds(self):
        self._create_elim_scope_dataset()
        self.tournament.preferences['feedback__feedback_paths_rounds'] = 'all'
        self.assertAdjudicatorProgress('minimal', 0, 4, 4, 4, 0, 1.0)

    def test_adjudicator_progress_scope_all_rounds_missing_elim_submission(self):
        elim = self._create_elim_round()
        prelim_debate = self._create_debate((0, 1), (0, 1, 2), "nnn")
        self._create_debate((2, 3), (0, 3, 4), "nnn", rd=elim)
        for adj in (1, 2):
            self._create_feedback(self._da(prelim_debate, 0), adj)

        self.tournament.preferences['feedback__feedback_paths_rounds'] = 'prelims'
        self.assertAdjudicatorProgress('minimal', 0, 2, 2, 2, 0, 1.0)

        self.tournament.preferences['feedback__feedback_paths_rounds'] = 'all'
        self.assertAdjudicatorProgress('minimal', 0, 2, 4, 2, 2, 1/2)

    def test_adjudicator_progress_scope_includes_silent_elim_rounds(self):
        elim = self._create_elim_round()
        elim.silent = True
        elim.save()
        self._create_debate((0, 1), (0, 1, 2), "nnn")
        self._create_debate((2, 3), (0, 3, 4), "nnn", rd=elim)

        self.tournament.preferences['feedback__feedback_paths_rounds'] = 'all'
        # Silent rounds only suppress feedback from teams, not from adjudicators.
        self.assertAdjudicatorProgress('minimal', 0, 0, 4, 0, 4, 0.0)

    def test_scopes_are_independent(self):
        self._create_elim_scope_dataset()
        self.tournament.preferences['feedback__feedback_paths_rounds'] = 'all'
        self.tournament.preferences['feedback__feedback_from_teams_rounds'] = 'prelims'
        self.assertAdjudicatorProgress('minimal', 0, 4, 4, 4, 0, 1.0)
        self.assertTeamProgress('orallist', True, 0, 1, 1, 1, 0, 1.0)

        self.tournament.preferences['feedback__feedback_paths_rounds'] = 'prelims'
        self.tournament.preferences['feedback__feedback_from_teams_rounds'] = 'all'
        self.assertAdjudicatorProgress('minimal', 0, 2, 2, 2, 0, 1.0)
        self.assertTeamProgress('orallist', True, 0, 2, 2, 2, 0, 1.0)

    # ==========================================================================
    # get_feedback_progress (bulk/prefetched variant)
    # ==========================================================================

    def _bulk_progress(self):
        """Returns (team progress, adjudicator progress) by team/adjudicator,
        computed through the bulk-prefetching code path."""
        tournament = Tournament.objects.get(pk=self.tournament.pk)
        teams_progress, adjs_progress = get_feedback_progress(tournament)
        return ({p.team.reference: p for p in teams_progress},
                {p.adjudicator.name: p for p in adjs_progress})

    def test_bulk_progress_matches_individual_prelims_only(self):
        self._create_elim_scope_dataset()
        self.tournament.preferences['feedback__feedback_paths_rounds'] = 'prelims'
        self.tournament.preferences['feedback__feedback_from_teams_rounds'] = 'prelims'
        self.tournament.preferences['feedback__feedback_from_teams'] = 'orallist'
        self.tournament.preferences['feedback__feedback_paths'] = 'minimal'

        teams, adjs = self._bulk_progress()
        self.assertEqual(teams['0'].num_expected(), 1)
        self.assertEqual(teams['0'].num_submitted(), 1)
        self.assertEqual(adjs['0'].num_expected(), 2)
        self.assertEqual(adjs['0'].num_submitted(), 2)

    def test_bulk_progress_matches_individual_all_rounds(self):
        self._create_elim_scope_dataset()
        self.tournament.preferences['feedback__feedback_paths_rounds'] = 'all'
        self.tournament.preferences['feedback__feedback_from_teams_rounds'] = 'all'
        self.tournament.preferences['feedback__feedback_from_teams'] = 'orallist'
        self.tournament.preferences['feedback__feedback_paths'] = 'minimal'

        teams, adjs = self._bulk_progress()
        self.assertEqual(teams['0'].num_expected(), 2)
        self.assertEqual(teams['0'].num_submitted(), 2)
        self.assertEqual(adjs['0'].num_expected(), 4)
        self.assertEqual(adjs['0'].num_submitted(), 4)

    def test_bulk_progress_respects_independent_scopes(self):
        self._create_elim_scope_dataset()
        self.tournament.preferences['feedback__feedback_paths_rounds'] = 'all'
        self.tournament.preferences['feedback__feedback_from_teams_rounds'] = 'prelims'
        self.tournament.preferences['feedback__feedback_from_teams'] = 'orallist'
        self.tournament.preferences['feedback__feedback_paths'] = 'minimal'

        teams, adjs = self._bulk_progress()
        self.assertEqual(teams['0'].num_expected(), 1)
        self.assertEqual(adjs['0'].num_expected(), 4)

    # ==========================================================================
    # Orallist enforcement follows the round's stage
    # ==========================================================================

    def _create_rolled_chair_elim_debate(self):
        """An elimination debate in which the chair (adj 0) was rolled, so the
        orallist is a panellist, and the team gave feedback on the chair."""
        elim = self._create_elim_round()
        debate = self._create_debate((0, 1), (0, 1, 2), "ann", rd=elim)
        self._create_feedback(self._dt(debate, 0), 0)
        return debate

    def test_enforce_orallist_uses_elim_ballots_pref(self):
        self._create_rolled_chair_elim_debate()
        self.tournament.preferences['feedback__feedback_from_teams_rounds'] = 'all'
        self.tournament.preferences['debate_rules__ballots_per_debate_elim'] = 'per-adj'
        # The chair was rolled, so feedback on the chair does not fulfil the
        # expectation when the orallist is enforced.
        progress = self.assertTeamProgress('orallist', True, 0, 1, 1, 0, 1, 0.0)
        self.assertEqual(len(progress.unexpected_trackers()), 1)

    def test_enforce_orallist_not_applied_for_consensus_elim_ballots(self):
        self._create_rolled_chair_elim_debate()
        self.tournament.preferences['feedback__feedback_from_teams_rounds'] = 'all'
        self.tournament.preferences['debate_rules__ballots_per_debate_elim'] = 'per-debate'
        # With a consensus ballot there is no orallist to enforce, so feedback
        # on the chair is accepted.
        progress = self.assertTeamProgress('orallist', True, 0, 1, 1, 1, 0, 1.0)
        self.assertEqual(len(progress.unexpected_trackers()), 0)

    def test_elim_ballots_pref_does_not_affect_prelim_rounds(self):
        # Chair rolled in a preliminary round; only the prelim ballots
        # preference should govern whether the orallist is enforced there.
        debate = self._create_debate((0, 1), (0, 1, 2), "ann")
        self._create_feedback(self._dt(debate, 0), 0)
        self.tournament.preferences['debate_rules__ballots_per_debate_prelim'] = 'per-adj'
        self.tournament.preferences['debate_rules__ballots_per_debate_elim'] = 'per-debate'
        progress = self.assertTeamProgress('orallist', True, 0, 1, 1, 0, 1, 0.0)
        self.assertEqual(len(progress.unexpected_trackers()), 1)
