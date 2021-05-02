import unittest

from ..scoresheet import (BPScoresheet, HighPointWinsRequiredScoresheet,
    LowPointWinsAllowedScoresheet, ResultOnlyScoresheet,
    TiedPointWinsAllowedScoresheet)


def on_all_testdata(test_fn):
    """Decorator. Tests should be written to take two arguments: self,
     testdata. 'scoresheet' is a Scoresheet object. 'testdata'
    is a value of BaseBaseScoresheet.testdata. This decorator then sets up
    the scoresheet and runs the test once for each test dataset in
    BaseBaseScoresheet.testdata."""
    def foo(self):
        for testdata in self.testdata.values():
            test_fn(self, testdata)
    return foo


class TestTwoTeamScoresheets(unittest.TestCase):

    sides = ['aff', 'neg']

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

    def load_scores(self, scoresheet, testdata):
        for side, scores_for_side in zip(self.sides, testdata['scores']):
            for position, score in zip(testdata['positions'], scores_for_side):
                scoresheet.set_score(side, position, score)

    def assert_scores(self, scoresheet, testdata):
        for side, total in zip(self.sides, testdata['totals']):
            self.assertEqual(scoresheet.get_total(side), total)
        for side, scores_for_side in zip(self.sides, testdata['scores']):
            for position, score in zip(testdata['positions'], scores_for_side):
                self.assertEqual(scoresheet.get_score(side, position), score)

    @on_all_testdata
    def test_result_only(self, testdata):
        scoresheet = ResultOnlyScoresheet()
        scoresheet.add_declared_winner(testdata['declared_winner'])
        self.assertEqual(scoresheet.is_complete(), testdata['complete_declared'])
        if scoresheet.is_complete():
            self.assertEqual(next(iter(scoresheet.winners()), None), testdata['declared_winner'])
            self.assertEqual(len(scoresheet.winners()), 1)
        else:
            self.assertEqual(len(scoresheet.winners()), 0)

    @on_all_testdata
    def test_high_points_required(self, testdata):
        scoresheet = HighPointWinsRequiredScoresheet(testdata['positions'])
        self.load_scores(scoresheet, testdata)
        self.assertEqual(scoresheet.is_complete(), testdata['complete_scores'])
        if testdata['calculated_winner'] is None:
            self.assertEqual(len(scoresheet.winners()), 0)
        else:
            self.assertEqual(next(iter(scoresheet.winners()), None), testdata['calculated_winner'])
        self.assert_scores(scoresheet, testdata)
        self.assertEqual(scoresheet.is_valid(), testdata['calculated_winner'] is not None)

    @on_all_testdata
    def test_low_point_win(self, testdata):
        scoresheet = LowPointWinsAllowedScoresheet(testdata['positions'])
        scoresheet.add_declared_winner(testdata['declared_winner'])
        self.load_scores(scoresheet, testdata)
        self.assertEqual(scoresheet.is_complete(), testdata['complete_scores'] and testdata['complete_declared'])
        if scoresheet.is_complete():
            self.assertEqual(len(scoresheet.winners()), 1)
            self.assertEqual(next(iter(scoresheet.winners()), None), testdata['declared_winner'])
        else:
            self.assertEqual(len(scoresheet.winners()), 0)
        self.assert_scores(scoresheet, testdata)
        self.assertEqual(scoresheet.is_valid(), testdata['complete_scores'] and testdata['complete_declared'])

    @on_all_testdata
    def test_tie_point_win(self, testdata):
        scoresheet = TiedPointWinsAllowedScoresheet(testdata['positions'])
        scoresheet.add_declared_winner(testdata['declared_winner'])
        self.load_scores(scoresheet, testdata)
        self.assertEqual(scoresheet.is_complete(), testdata['complete_scores'] and testdata['complete_declared'])
        if scoresheet.is_complete() and (testdata['calculated_winner'] in [testdata['declared_winner'], None]):
            winner = testdata['declared_winner']
            self.assertEqual(next(iter(scoresheet.winners()), None), winner)
            self.assertEqual(len(scoresheet.winners()), 1)
        else:
            winner = None
            self.assertEqual(len(scoresheet.winners()), 0)
        self.assert_scores(scoresheet, testdata)
        self.assertEqual(scoresheet.is_valid(), winner is not None)

    def test_declared_winner_error(self):
        scoresheet = ResultOnlyScoresheet()
        self.assertRaises(AssertionError, scoresheet.set_declared_winners, set(['hello']))


class TestBPScoresheets(unittest.TestCase):

    sides = ['og', 'oo', 'cg', 'co']
    positions = [1, 2]

    testdata = {}

    testdata[1] = {  # normal
        'scores': [[76, 69], [76, 70], [72, 85], [69, 85]],
        'complete': True,
        'ranks': ['cg', 'co', 'oo', 'og'],
        'totals': [145, 146, 157, 154],
    }
    testdata[1] = {  # normal
        'scores': [[75, 75], [75, 74], [75, 76], [76, 76]],
        'complete': True,
        'ranks': ['co', 'cg', 'og', 'oo'],
        'totals': [150, 149, 151, 152],
    }
    testdata[1] = {  # tie-point
        'scores': [[84, 81], [80, 69], [81, 68], [85, 68]],
        'complete': True,
        'ranks': None,
        'totals': [165, 149, 149, 153],
    }
    testdata[2] = { # incomplete
        'scores': [[84, None], [80, 69], [None, 68], [85, 68]],
        'complete': False,
        'ranks': None,
        'totals': [None, 149, None, 153],
    }

    def load_scores(self, scoresheet, testdata):
        for side, scores_for_side in zip(self.sides, testdata['scores']):
            for position, score in zip(self.positions, scores_for_side):
                scoresheet.set_score(side, position, score)

    @on_all_testdata
    def test_bp_scoresheet(self, testdata):
        scoresheet = BPScoresheet(self.positions)
        self.load_scores(scoresheet, testdata)
        self.assertEqual(scoresheet.is_complete(), testdata['complete'])
        self.assertEqual(scoresheet.ranked_sides(), testdata['ranks'])
        if testdata['ranks'] is not None:
            for side, rank in zip(self.sides, testdata['ranks']):
                self.assertEqual(scoresheet.rank(side), testdata['ranks'].index(side))
        else:
            for side in self.sides:
                self.assertEqual(scoresheet.rank(side), None)
        for side, total in zip(self.sides, testdata['totals']):
            self.assertEqual(scoresheet.get_total(side), total)
        for side, scores_for_side in zip(self.sides, testdata['scores']):
            for position, score in zip(self.positions, scores_for_side):
                self.assertEqual(scoresheet.get_score(side, position), score)
        self.assertEqual(scoresheet.is_valid(), testdata['ranks'] is not None)
