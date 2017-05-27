from django.test import TestCase

from tournaments.models import Round, Tournament
from participants.models import Adjudicator, Institution, Speaker, Team
from venues.models import Venue
from draw.models import Debate, DebateTeam
from results.models import BallotSubmission
from adjallocation.models import DebateAdjudicator

from ..result import VotingDebateResult


class TestVotingDebateResult(TestCase):

    testdata = dict()
    testdata[1] = {
        'scores': [[[75.0, 76.0, 74.0, 38.0], [76.0, 73.0, 75.0, 37.5]],
                   [[74.0, 75.0, 76.0, 37.0], [77.0, 74.0, 74.0, 38.0]],
                   [[75.0, 75.0, 75.0, 37.5], [76.0, 78.0, 77.0, 37.0]]],
        'totals_by_adj': [[263, 261.5], [262, 263], [262.5, 268]],
        'majority_scores': [[74.5, 75, 75.5, 37.25], [76.5, 76, 75.5, 37.5]],
        'majority_totals': [262.25, 265.5],
        'majority_margins': [-3.25, 3.25],
        'winner_by_adj': ['aff', 'neg', 'neg'],
        'winner': 'neg',
        'num_adjs_for_team': [1, 2],
    }
    testdata[2] = {
        'scores': [[[73.0, 76.0, 79.0, 37.5], [77.0, 77.0, 78.0, 39.0]],
                   [[79.0, 80.0, 70.0, 36.0], [78.0, 79.0, 73.0, 37.0]],
                   [[73.0, 70.0, 77.0, 35.0], [76.0, 76.0, 77.0, 37.0]]],
        'totals_by_adj': [[265.5, 271.0], [265.0, 267.0], [255.0, 266.0]],
        'majority_scores': [[75.0, 75.33333333333333, 75.33333333333333, 36.166666666666664],
                            [77.0, 77.33333333333333, 76.0, 37.666666666666664]],
        'majority_totals': [261.8333333333333, 268.0],
        'majority_margins': [-6.166666666666667, 6.166666666666667],
        'winner_by_adj': ['neg', 'neg', 'neg'],
        'winner': 'neg',
        'num_adjs_for_team': [0, 3],
    }
    testdata[3] = {
        'majority_scores': [[75.5, 76.5, 77.5, 38.75], [71.5, 71.5, 75.0, 38.5]],
        'winner': 'aff',
        'winner_by_adj': ['neg', 'aff', 'aff'],
        'totals_by_adj': [[261.0, 271.5], [268.5, 259.0], [268.0, 254.0]],
        'majority_totals': [268.25, 256.5],
        'majority_margins': [11.75, -11.75],
        'scores': [[[73.0, 70.0, 78.0, 40.0], [80.0, 78.0, 75.0, 38.5]],
                   [[79.0, 75.0, 75.0, 39.5], [73.0, 73.0, 73.0, 40.0]],
                   [[72.0, 78.0, 80.0, 38.0], [70.0, 70.0, 77.0, 37.0]]],
        'num_adjs_for_team': [2, 1],
        'num_adjs': 3,
    }

    SIDES = ['aff', 'neg']

    def setUp(self):
        self.t = Tournament.objects.create(slug="resulttest", name="ResultTest")
        for i in range(2):
            inst = Institution.objects.create(code="Inst{:d}".format(i), name="Institution {:d}".format(i))
            team = Team.objects.create(tournament=self.t, institution=inst, reference="Team {:d}".format(i), use_institution_prefix=False)
            for j in range(3):
                Speaker.objects.create(team=team, name="Speaker {:d}-{:d}".format(i, j))
        inst = Institution.objects.create(code="Adjs", name="Adjudicators")
        for i in range(3):
            Adjudicator.objects.create(tournament=self.t, institution=inst, name="Adjudicator {:d}".format(i), test_score=5)
        venue = Venue.objects.create(name="Venue", priority=10)

        rd = Round.objects.create(tournament=self.t, seq=1, abbreviation="R1")
        self.debate = Debate.objects.create(round=rd, venue=venue)

        sides = [DebateTeam.POSITION_AFFIRMATIVE, DebateTeam.POSITION_NEGATIVE]
        for team, side in zip(Team.objects.all(), sides):
            DebateTeam.objects.create(debate=self.debate, team=team, position=side)

        self.adjs = list(Adjudicator.objects.all())
        adjtypes = [DebateAdjudicator.TYPE_CHAIR, DebateAdjudicator.TYPE_PANEL, DebateAdjudicator.TYPE_PANEL]
        for adj, adjtype in zip(self.adjs, adjtypes):
            DebateAdjudicator.objects.create(debate=self.debate, adjudicator=adj, type=adjtype)

    def tearDown(self):
        DebateTeam.objects.all().delete()
        Institution.objects.all().delete()
        self.t.delete()

    def _get_result(self):
        ballotsub = BallotSubmission.objects.get(debate=self.debate, confirmed=True)
        return VotingDebateResult(ballotsub, scoresheet_pref='high-required')

    def save_complete_result(self, testdata, post_create=None):
        # unconfirm existing ballot
        try:
            existing = BallotSubmission.objects.get(debate=self.debate, confirmed=True)
        except BallotSubmission.DoesNotExist:
            pass
        else:
            existing.confirmed = False
            existing.save()

        ballotsub = BallotSubmission.objects.create(debate=self.debate, confirmed=True,
                submitter_type=BallotSubmission.SUBMITTER_TABROOM)

        result = VotingDebateResult(ballotsub, scoresheet_pref='high-required')
        if post_create:
            post_create(result)

        for side in self.SIDES:
            speakers = self.debate.get_team(side).speaker_set.all()
            for pos, speaker in enumerate(speakers, start=1):
                result.set_speaker(side, pos, speaker)
            result.set_speaker(side, 4, speakers[0])
            # ghost fields should be False by default

        for adj, sheet in zip(self.adjs, testdata['scores']):
            for side, teamscores in zip(self.SIDES, sheet):
                for pos, score in enumerate(teamscores, start=1):
                    result.set_score(adj, side, pos, score)

        result.save()

    def on_all_datasets(test_fn):  # flake8: noqa
        """Decorator.
        Tests should be written to take three arguments: self, ballotset and
        testdata. 'ballotset' is a BallotSet object. 'testdata' is a value of
        BaseTestResult.testdata.
        This decorator then sets up the BallotSet and runs the test once for
        each test dataset in BaseTestResult.testdata."""
        def foo(self):
            for testdata_key in self.testdata:
                testdata = self.testdata[testdata_key]
                self.save_complete_result(testdata)
                result = self._get_result()
                test_fn(self, result, testdata)
        return foo

    @on_all_datasets
    def test_save(self, result, testdata):
        # Run self.save_complete_result and check completeness
        self.assertTrue(result.is_complete)

    @on_all_datasets
    def test_totals_by_adj(self, result, testdata):
        for adj, totals in zip(self.adjs, testdata['totals_by_adj']):
            for side, total in zip(self.SIDES, totals):
                self.assertEqual(result.scoresheets[adj].get_total(side), total)

    @on_all_datasets
    def test_majority_scores(self, result, testdata):
        for side, totals in zip(self.SIDES, testdata['majority_scores']):
            for pos, score in enumerate(totals, start=1):
                self.assertEqual(result.get_speaker_score(side, pos), score)

    @on_all_datasets
    def test_individual_scores(self, result, testdata):
        for adj, sheet in zip(self.adjs, testdata['scores']):
            for side, scores in zip(self.SIDES, sheet):
                for pos, score in enumerate(scores, start=1):
                    self.assertEqual(result.get_score(adj, side, pos), score)

    @on_all_datasets
    def test_winner_by_adj(self, result, testdata):
        for adj, winner in zip(self.adjs, testdata['winner_by_adj']):
            self.assertEqual(result.scoresheets[adj].winner(), winner)

    @on_all_datasets
    def test_teamscorefield_points(self, result, testdata):
        for side in self.SIDES:
            points = 1 if side == testdata['winner'] else 0
            self.assertEqual(result.teamscorefield_points(side), points)

    @on_all_datasets
    def test_teamscorefield_win(self, result, testdata):
        for side in self.SIDES:
            win = side == testdata['winner']
            self.assertEqual(result.teamscorefield_win(side), win)

    @on_all_datasets
    def test_teamscorefield_score(self, result, testdata):
        for side, total in zip(self.SIDES, testdata['majority_totals']):
            self.assertAlmostEqual(result.teamscorefield_score(side), total)

    @on_all_datasets
    def test_teamscorefield_margin(self, result, testdata):
        for side, margin in zip(self.SIDES, testdata['majority_margins']):
            self.assertAlmostEqual(result.teamscorefield_margin(side), margin)

    @on_all_datasets
    def test_teamscorefield_votes_given(self, result, testdata):
        for side, votes in zip(self.SIDES, testdata['num_adjs_for_team']):
            self.assertAlmostEqual(result.teamscorefield_votes_given(side), votes)

    @on_all_datasets
    def test_teamscorefield_votes_possible(self, result, testdata):
        for side in self.SIDES:
            self.assertAlmostEqual(result.teamscorefield_votes_possible(side),
                    sum(testdata['num_adjs_for_team']))

