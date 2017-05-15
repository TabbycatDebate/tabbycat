import unittest

from ..scoresheet import HighPointWinsRequiredScoresheet, LowPointWinsAllowedScoresheet, ResultOnlyScoresheet, TiedPointWinsAllowedScoresheet

class TestTwoTeamScoresheets(unittest.TestCase):

    SIDES = ['aff', 'neg']

    testdata = dict()
    testdata[1] = {  # normal
        'positions': [1, 2, 3, 4],
        'scores': [[75.0, 76.0, 74.0, 38.0], [76.0, 73.0, 75.0, 37.5]],
        'declared_winner': 'aff',
        'complete_scores': True,
        'complete_declared': True,
        'totals': [263, 261.5],
        'calculated_winner': 'aff',
    }
    testdata[2] = {  # low-point win
        'positions': [1, 2, 3],
        'scores': [[73.0, 70.0, 40.0], [80.0, 78.0, 38.5]],
        'declared_winner': 'aff',
        'complete_scores': True,
        'complete_declared': True,
        'totals': [183.0, 196.5],
        'calculated_winner': 'neg',
    }
    testdata[3] = {  # tie-point win
        'positions': [1, 2, 3, 4],
        'scores': [[75.0, 76.0, 77.0, 38.5], [76.0, 78.0, 75.0, 37.5]],
        'declared_winner': 'neg',
        'complete_scores': True,
        'complete_declared': True,
        'totals': [266.5, 266.5],
        'calculated_winner': None,
    }
    testdata[4] = {  # incomplete
        'positions': [1, 2, 3, 4],
        'scores': [[75.0, 76.0, 77.0, 38.5], [76.0, 78.0, None, 37.5]],
        'declared_winner': 'neg',
        'complete_scores': False,
        'complete_declared': True,
        'totals': [266.5, None],
        'calculated_winner': None,
    }
    testdata[5] = {  # incomplete
        'positions': [1, 2, 3],
        'scores': [[73.0, 70.0, 40.0], [80.0, 78.0, 38.5]],
        'declared_winner': None,
        'complete_scores': True,
        'complete_declared': False,
        'totals': [183.0, 196.5],
        'calculated_winner': 'neg',
    }

    def on_all_testdata(test_fn):  # flake8: noqa
        """Decorator. Tests should be written to take two arguments: self,
         testdata. 'scoresheet' is a Scoresheet object. 'testdata'
        is a value of BaseTestScoresheet.testdata. This decorator then sets up
        the scoresheet and runs the test once for each test dataset in
        BaseTestScoresheet.testdata."""
        def foo(self):
            for testdata in self.testdata.values():
                test_fn(self, testdata)
        return foo

    def load_scores(self, scoresheet, testdata):
        for side, scores_for_side in zip(self.SIDES, testdata['scores']):
            for position, score in zip(testdata['positions'], scores_for_side):
                scoresheet.set_score(side, position, score)

    @on_all_testdata
    def test_result_only(self, testdata):
        scoresheet = ResultOnlyScoresheet()
        scoresheet.set_declared_winner(testdata['declared_winner'])
        self.assertEqual(scoresheet.complete, testdata['complete_declared'])
        self.assertEqual(scoresheet.winner(), testdata['declared_winner'])

    @on_all_testdata
    def test_high_points_required(self, testdata):
        scoresheet = HighPointWinsRequiredScoresheet(testdata['positions'])
        self.load_scores(scoresheet, testdata)
        self.assertEqual(scoresheet.complete, testdata['complete_scores'])
        self.assertEqual(scoresheet.winner(), testdata['calculated_winner'])
        for side, total in zip(self.SIDES, testdata['totals']):
            self.assertEqual(scoresheet.get_total(side), total)

    @on_all_testdata
    def test_low_point_win(self, testdata):
        scoresheet = LowPointWinsAllowedScoresheet(testdata['positions'])
        scoresheet.set_declared_winner(testdata['declared_winner'])
        self.load_scores(scoresheet, testdata)
        self.assertEqual(scoresheet.complete, testdata['complete_scores'] and testdata['complete_declared'])
        self.assertEqual(scoresheet.winner(), testdata['declared_winner'] if scoresheet.complete else None)
        for side, total in zip(self.SIDES, testdata['totals']):
            self.assertEqual(scoresheet.get_total(side), total)

    @on_all_testdata
    def test_tie_point_win(self, testdata):
        scoresheet = TiedPointWinsAllowedScoresheet(testdata['positions'])
        scoresheet.set_declared_winner(testdata['declared_winner'])
        self.load_scores(scoresheet, testdata)
        self.assertEqual(scoresheet.complete, testdata['complete_scores'] and testdata['complete_declared'])
        if scoresheet.complete and (testdata['calculated_winner'] in [testdata['declared_winner'], None]):
            winner = testdata['declared_winner']
        else:
            winner = None
        self.assertEqual(scoresheet.winner(), winner)
        for side, total in zip(self.SIDES, testdata['totals']):
            self.assertEqual(scoresheet.get_total(side), total)

    def test_declared_winner_error(self):
        scoresheet = ResultOnlyScoresheet()
        self.assertRaises(AssertionError, scoresheet.set_declared_winner, 'hello')
