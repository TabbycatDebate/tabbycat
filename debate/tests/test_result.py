"""Unit tests for result.py"""

from unittest import SkipTest
from django.test import TestCase
import debate.models as m
import results.models as rm
import venues.models as vm
import random
from results.result import BallotSet

class BaseTestResult(TestCase):

    testdata = dict()
    testdata[1] = {
        'scores': [[[75.0, 76.0, 74.0, 38.0],   [76.0, 73.0, 75.0, 37.5]],
                  [[74.0, 75.0, 76.0, 37.0],   [77.0, 74.0, 74.0, 38.0]],
                  [[75.0, 75.0, 75.0, 37.5], [76.0, 78.0, 77.0, 37.0]]],
       'totals_by_adj': [[263, 261.5], [262, 263], [262.5, 268]],
       'majority_scores': [[74.5, 75, 75.5, 37.25], [76.5, 76, 75.5, 37.5]],
       'majority_totals': [262.25, 265.5],
       'winner_by_adj': [0, 1, 1],
       'winner': 1
   }
    testdata[2] = {
        'scores': [[[73.0, 76.0, 79.0, 37.5], [77.0, 77.0, 78.0, 39.0]],
                   [[79.0, 80.0, 70.0, 36.0], [78.0, 79.0, 73.0, 37.0]],
                   [[73.0, 70.0, 77.0, 35.0], [76.0, 76.0, 77.0, 37.0]]],
        'totals_by_adj': [[265.5, 271.0], [265.0, 267.0], [255.0, 266.0]],
        'majority_scores': [[75.0, 75.33333333333333, 75.33333333333333, 36.166666666666664],
                            [77.0, 77.33333333333333, 76.0, 37.666666666666664]],
        'majority_totals': [261.8333333333333, 268.0],
        'winner_by_adj': [1, 1, 1],
        'winner': 1
    }
    testdata[3] = {
        'majority_scores': [[75.5, 76.5, 77.5, 38.75], [71.5, 71.5, 75.0, 38.5]],
        'winner': 0,
        'winner_by_adj': [1, 0, 0],
        'totals_by_adj': [[261.0, 271.5], [268.5, 259.0], [268.0, 254.0]],
        'majority_totals': [268.25, 256.5],
        'scores': [[[73.0, 70.0, 78.0, 40.0], [80.0, 78.0, 75.0, 38.5]],
                   [[79.0, 75.0, 75.0, 39.5], [73.0, 73.0, 73.0, 40.0]],
                   [[72.0, 78.0, 80.0, 38.0], [70.0, 70.0, 77.0, 37.0]]]
    }

    incompletedata = {'scores': [[[75, 76, None, 38],   [76, 73, 75, 37.5]],
                                 [[74, 75, 76, 37],   [77, None, 74, 38]],
                                 [[75, 75, 75, 37.5], [76, 78, 77, None]]],
                      'totals_by_adj': [[None, 261.5], [262, None], [262.5, None]],
                      'majority_scores': [[None, 75, 75.5, 37.25], [76.5, None, 75.5, None]],
                      'majority_totals': [None, None],
                      'winner_by_adj': [None, None, None],
                      'winner': None}

    def setUp(self):
        self.t = m.Tournament(slug="resulttest", name="ResultTest")
        self.t.save()
        for i in range(2):
            inst = m.Institution(code="Inst%d"%i, name="Institution %d"%i)
            inst.save()
            team = m.Team(tournament=self.t, institution=inst, reference="Team %d"%i,
                use_institution_prefix=False)
            team.save()
            for j in range(3):
                speaker = m.Speaker(team=team, name="Speaker %d-%d"%(i,j))
                speaker.save()
        inst = m.Institution(code="Indep", name="Independent %d"%i)
        inst.save()
        for i in range(3):
            adj = m.Adjudicator(tournament=self.t, institution=inst,
                    name="Adjudicator %d"%i, test_score=5)
            adj.save()
        venue = vm.Venue(name="Venue", priority=10)
        venue.save()

        self.adjs = list(m.Adjudicator.objects.all())
        self.teams = list(m.Team.objects.all())

        self.round = m.Round(tournament=self.t, seq=1, abbreviation="R1")
        self.round.save()
        for venue in vm.Venue.objects.all():
            self.round.activate_venue(venue, True)
        self.debate = m.Debate(round=self.round, venue=venue)
        self.debate.save()
        positions = [m.DebateTeam.POSITION_AFFIRMATIVE, m.DebateTeam.POSITION_NEGATIVE]
        for team, pos in zip(self.teams, positions):
            self.round.activate_team(team, True)
            m.DebateTeam(debate=self.debate, team=team, position=pos).save()
        adjtypes = [m.DebateAdjudicator.TYPE_CHAIR, m.DebateAdjudicator.TYPE_PANEL, m.DebateAdjudicator.TYPE_PANEL]
        for adj, adjtype in zip(self.adjs, adjtypes):
            self.round.activate_adjudicator(adj, True)
            m.DebateAdjudicator(debate=self.debate, adjudicator=adj, type=adjtype).save()

    def _get_team(self, team):
        if team in ['aff', 'neg']:
            team = self.debate.get_team(team)
        return team

    def _get_ballotset(self):
        ballotsub = rm.BallotSubmission.objects.get(debate=self.debate, confirmed=True)
        return BallotSet(ballotsub)

    def save_complete_ballotset(self, teams, testdata):
        self._save_complete_ballotset(teams, testdata)

    def _save_complete_ballotset(self, teams, testdata, post_ballotset_create=None):
        # unconfirm existing ballot
        try:
            existing = rm.BallotSubmission.objects.get(debate=self.debate, confirmed=True)
        except rm.BallotSubmission.DoesNotExist:
            pass
        else:
            existing.confirmed = False
            existing.save()

        ballotsub = rm.BallotSubmission(debate=self.debate, submitter_type=rm.BallotSubmission.SUBMITTER_TABROOM)
        ballotset = BallotSet(ballotsub)
        if post_ballotset_create:
            post_ballotset_create(ballotset)
        scores = testdata['scores']

        for team in teams:
            speakers = self._get_team(team).speaker_set.all()
            for pos, speaker in enumerate(speakers, start=1):
                ballotset.set_speaker(team, pos, speaker)
            ballotset.set_speaker(team, 4, speakers[0])

        for adj, sheet in zip(self.adjs, scores):
            for team, teamscores in zip(teams, sheet):
                for pos, score in enumerate(teamscores, start=1):
                    ballotset.set_score(adj, team, pos, score)

        ballotset.confirmed = True
        ballotset.save()

        return ballotset

class CommonTests(object):

    def on_all_datasets(test_fn):
        """Decorator.
        Tests should be written to take three arguments: self, ballotset and
        testdata. 'ballotset' is a BallotSet object. 'testdata' is a value of
        BaseTestResult.testdata.
        This decorator then sets up the BallotSet and runs the test once for
        each test dataset in BaseTestResult.testdata."""
        def foo(self):
            for testdata_key in self.testdata:
                testdata = self.testdata[testdata_key]
                self.save_complete_ballotset(self.teams_input, testdata)
                ballotset = self._get_ballotset()
                test_fn(self, ballotset, testdata)
        return foo

    @on_all_datasets
    def test_save_complete_ballotset(self, ballotset, testdata):
        # Just run self.save_complete_ballotset
        pass

    @on_all_datasets
    def test_totals_by_adj(self, ballotset, testdata):
        for adj, totals in zip(self.adjs, testdata['totals_by_adj']):
            for team, total in zip(self.teams_input, totals):
                self.assertEqual(ballotset.adjudicator_sheets[adj].get_total(team), total)

    @on_all_datasets
    def test_totals_by_adj_by_side(self, ballotset, testdata):
        for adj, totals in zip(self.adjs, testdata['totals_by_adj']):
            self.assertEqual(ballotset.adjudicator_sheets[adj].aff_score, totals[0])
            self.assertEqual(ballotset.adjudicator_sheets[adj].neg_score, totals[1])

    @on_all_datasets
    def test_majority_scores(self, ballotset, testdata):
        for team, totals in zip(self.teams_input, testdata['majority_scores']):
            for pos, score in enumerate(totals, start=1):
                self.assertEqual(ballotset.get_avg_score(team, pos), score)

    @on_all_datasets
    def test_individual_scores(self, ballotset, testdata):
        for adj, sheet in zip(self.adjs, testdata['scores']):
            for team, totals in zip(self.teams_input, sheet):
                for pos, score in enumerate(totals, start=1):
                    self.assertEqual(ballotset.get_score(adj, team, pos), score)

    @on_all_datasets
    def test_winner_by_adj(self, ballotset, testdata):
        for adj, winner in zip(self.adjs, testdata['winner_by_adj']):
            self.assertEqual(ballotset.adjudicator_sheets[adj].winner,
                    self.teams[winner])

    @on_all_datasets
    def test_winner_by_adj_by_side(self, ballotset, testdata):
        for adj, winner in zip(self.adjs, testdata['winner_by_adj']):
            self.assertEqual(ballotset.adjudicator_sheets[adj].aff_win,
                    winner == 0)
            self.assertEqual(ballotset.adjudicator_sheets[adj].neg_win,
                    winner == 1)

    @on_all_datasets
    def test_winner(self, ballotset, testdata):
        self.assertEqual(ballotset.winner, self.teams[testdata['winner']])

    @on_all_datasets
    def test_winner_by_side(self, ballotset, testdata):
        self.assertEqual(ballotset.aff_win, testdata['winner'] == 0)
        self.assertEqual(ballotset.neg_win, testdata['winner'] == 1)

    @on_all_datasets
    def test_majority_totals(self, ballotset, testdata):
        for team, total in zip(self.teams_input, testdata['majority_totals']):
            self.assertAlmostEqual(ballotset.get_avg_total(team), total)

    @on_all_datasets
    def test_majority_totals_by_side(self, ballotset, testdata):
        self.assertAlmostEqual(ballotset.aff_score, testdata['majority_totals'][0])
        self.assertAlmostEqual(ballotset.neg_score, testdata['majority_totals'][1])

    @on_all_datasets
    def test_sheet_iter(self, ballotset, testdata):
        NAMES = ["1", "2", "3", "Reply"]
        for sheet, adj, scores, total, winner in zip(ballotset.sheet_iter, self.adjs, testdata['scores'], testdata['totals_by_adj'], testdata['winner_by_adj']):
            self.assertEqual(sheet.adjudicator, adj)
            for pos, name, speaker, score in zip(sheet.affs, NAMES, self._get_team('aff').speaker_set.all(), scores[0]):
                self.assertEqual(pos.name, name)
                self.assertEqual(pos.speaker, speaker)
                self.assertEqual(pos.score, score)
            for pos, name, speaker, score in zip(sheet.negs, NAMES, self._get_team('neg').speaker_set.all(), scores[1]):
                self.assertEqual(pos.name, name)
                self.assertEqual(pos.speaker, speaker)
                self.assertEqual(pos.score, score)
            self.assertEqual(sheet.aff_score, total[0])
            self.assertEqual(sheet.neg_score, total[1])
            self.assertEqual(sheet.aff_win, winner == 0)
            self.assertEqual(sheet.neg_win, winner == 1)

    def test_incomplete_save(self):
        self.assertRaises(AssertionError, self.save_complete_ballotset, self.teams_input, self.incompletedata)

class TestResultByTeam(BaseTestResult, CommonTests):
    def setUp(self):
        BaseTestResult.setUp(self)
        self.teams_input = self.teams

class TestResultBySide(BaseTestResult, CommonTests):
    def setUp(self):
        BaseTestResult.setUp(self)
        self.teams_input = ['aff', 'neg']

class TestResultWithInitiallyUnknownSides(BaseTestResult, CommonTests):

    def setUp(self):
        BaseTestResult.setUp(self)
        for dt in self.debate.debateteam_set.all():
            dt.position = m.DebateTeam.POSITION_UNALLOCATED
            dt.save()
        self.teams_input = ['aff', 'neg']

    def save_complete_ballotset(self, teams, testdata):
        self._save_complete_ballotset(teams, testdata,
                post_ballotset_create=lambda ballotset: ballotset.set_sides(*self.teams))

    def test_unknown_sides(self):
        self.assertRaises(m.DebateTeam.DoesNotExist, self._save_complete_ballotset,
                self.teams_input, self.testdata.values()[0])