import unittest

from .utils import TestTeam
from ..generator.powerpair import GraphCostMixin, GraphPowerPairedDrawGenerator
from ..types import DebateSide

DUMMY_TEAMS = [TestTeam(1, 'A', allocated_side=DebateSide.AFF), TestTeam(2, 'B', allocated_side=DebateSide.NEG)]


class TestPowerPairedDrawGeneratorParts(unittest.TestCase):

    def test_pairings_slide_deviation_top(self):
        teams = [TestTeam(i+1, chr(ord('A') + i), subrank=i+1) for i in range(8)]

        for i, team in enumerate(teams):
            """Expected:
            (A-A): 4
            A - B: 3
            A - C: 2
            A - D: 1
            A - E: 0
            A - F: 1
            A - G: 2
            A - H: 3"""
            with self.subTest(i=i):
                self.assertEqual(GraphCostMixin._pairings_slide([teams[0], team], 8), abs(i - 4))

    def test_pairings_slide_deviation(self):
        teams = [TestTeam(i+1, chr(ord('A') + i), subrank=i+1) for i in range(8)]

        for i, team in enumerate(teams):
            """Expected:
            D - A: 1
            D - B: 2
            D - C: 3
            (D-D): 4
            D - E: 3
            D - F: 2
            D - G: 1
            D - H: 0"""
            with self.subTest(i=i):
                self.assertEqual(GraphCostMixin._pairings_slide([teams[3], team], 8), 4 - abs(i - 3))

    def test_pairings_fold_deviation_top(self):
        teams = [TestTeam(i+1, chr(ord('A') + i), subrank=i+1) for i in range(8)]

        for i, team in enumerate(teams):
            """Expected:
            (A-A): 7
            A - B: 6
            A - C: 5
            A - D: 4
            A - E: 3
            A - F: 2
            A - G: 1
            A - H: 0"""
            with self.subTest(i=i):
                self.assertEqual(GraphCostMixin._pairings_fold([teams[0], team], 8), 7-i)

    def test_pairings_fold_deviation(self):
        teams = [TestTeam(i+1, chr(ord('A') + i), subrank=i+1) for i in range(8)]

        for i, team in enumerate(teams):
            """Expected:
            D - A: 4
            D - B: 3
            D - C: 2
            (D-D): 1
            D - E: 0
            D - F: 1
            D - G: 2
            D - H: 3"""
            with self.subTest(i=i):
                self.assertEqual(GraphCostMixin._pairings_fold([teams[3], team], 8), abs(4-i))
        return [abs(4-i) for i in range(8)]

    def test_pairings_random_deviation_zero(self):
        teams = [TestTeam(i+1, chr(ord('A') + i), subrank=i+1) for i in range(8)]
        # Always 0
        self.assertEqual(GraphCostMixin._pairings_random([teams[0], teams[1]], 8), 0)

    def test_pairings_adjacent_deviation_top(self):
        teams = [TestTeam(i+1, chr(ord('A') + i), subrank=i+1) for i in range(8)]

        for i, team in enumerate(teams):
            """Expected:
            (A-A): -1
            A - B: 0
            A - C: 1
            A - D: 2
            A - E: 3
            A - F: 4
            A - G: 5
            A - H: 6"""
            with self.subTest(i=i):
                self.assertEqual(GraphCostMixin._pairings_adjacent([teams[0], team], 8), i-1)

    def test_pairings_adjacent_deviation(self):
        teams = [TestTeam(i+1, chr(ord('A') + i), subrank=i+1) for i in range(8)]

        for i, team in enumerate(teams):
            """Expected:
            D - A: 2
            D - B: 1
            D - C: 0
            (D-D): -1
            D - E: 0
            D - F: 1
            D - G: 2
            D - H: 3"""
            with self.subTest(i=i):
                self.assertEqual(GraphCostMixin._pairings_adjacent([teams[3], team], 8), abs(i - 3) - 1)
        return [abs(i - 3) - 1 for i in range(8)]

    def test_pairings_fold_adj_deviation(self):
        teams = [TestTeam(i+1, chr(ord('A') + i), subrank=i+1) for i in range(8)]
        methods = [self.test_pairings_fold_deviation, self.test_pairings_adjacent_deviation]
        for i, method in enumerate(methods):
            for j, (team, expected) in enumerate(zip(teams, method())):
                self.assertEqual(GraphCostMixin._pairings_fold_top_adjacent_rest([teams[3], team], 8, bracket=i), expected)

    def test_add_pullup_penalty(self):
        teams = [TestTeam(i+1, chr(ord('A') + i), subrank=i+1, pullup_debates=i+1) for i in range(2)]
        gcm = GraphPowerPairedDrawGenerator(teams)
        gcm.options = {'pullup_debates_penalty': 1, 'pairing_method': 'random', 'avoid_history': False, 'avoid_institution': False, 'side_allocations': False}
        gcm.team_flags = {teams[0]: ['pullup']}
        self.assertEqual(gcm.assignment_cost(*teams, 2), 2)

    def test_add_subrank_pullup(self):
        teams = [TestTeam(i+1, chr(ord('A') + i), subrank=(None if i else 1)) for i in range(2)]
        gcm = GraphPowerPairedDrawGenerator(teams)
        gcm.options = {'pullup_debates_penalty': 1, 'pairing_method': 'fold', 'avoid_history': False, 'avoid_institution': False, 'side_allocations': False, 'pairing_penalty': 1}
        self.assertEqual(gcm.assignment_cost(*teams, 2), 0)
        self.assertEqual(teams[1].subrank, 2)

    def test_none_self_penalty(self):
        team = TestTeam(1, 'A')
        gcm = GraphPowerPairedDrawGenerator([team, team])
        gcm.options = {'pullup_debates_penalty': 1, 'pairing_method': 'fold', 'avoid_history': False, 'avoid_institution': False, 'side_allocations': False, 'pairing_penalty': 1}
        self.assertEqual(gcm.assignment_cost(team, team, 2), None)
