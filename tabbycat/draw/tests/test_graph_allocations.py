import unittest

from .utils import TestTeam
from ..generator.powerpair import GraphCostMixin, GraphPowerPairedDrawGenerator, SingleGraphPowerPairedDrawGenerator
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
                self.assertEqual(GraphCostMixin._pairings_slide([teams[0].subrank, team.subrank], 8), abs(i - 4))

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
                self.assertEqual(GraphCostMixin._pairings_slide([teams[3].subrank, team.subrank], 8), 4 - abs(i - 3))

    def test_pairings_fold_deviation_top(self):
        teams = [TestTeam(i+1, chr(ord('A') + i), subrank=i+1) for i in range(8)]

        for i, team in enumerate(teams):
            """Expected:
            (A-A): 49
            A - B: 36
            A - C: 25
            A - D: 16
            A - E: 9
            A - F: 4
            A - G: 1
            A - H: 0"""
            with self.subTest(i=i):
                self.assertEqual(GraphCostMixin._pairings_fold([teams[0].subrank, team.subrank], 8), (7-i) ** 2)

    def test_pairings_fold_deviation(self):
        teams = [TestTeam(i+1, chr(ord('A') + i), subrank=i+1) for i in range(8)]

        for i, team in enumerate(teams):
            """Expected:
            D - A: 16
            D - B: 9
            D - C: 4
            (D-D): 1
            D - E: 0
            D - F: 1
            D - G: 4
            D - H: 9"""
            with self.subTest(i=i):
                self.assertEqual(GraphCostMixin._pairings_fold([teams[3].subrank, team.subrank], 8), abs(4-i) ** 2)
        return [abs(4-i) ** 2 for i in range(8)]

    def test_pairings_random_deviation_zero(self):
        teams = [TestTeam(i+1, chr(ord('A') + i), subrank=i+1) for i in range(8)]
        # Always 0
        self.assertAlmostEqual(GraphCostMixin._pairings_random([teams[0].subrank, teams[1].subrank], 8), 0, delta=1e-6)

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
                self.assertEqual(GraphCostMixin._pairings_adjacent([teams[0].subrank, team.subrank], 8), i-1)

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
                self.assertEqual(GraphCostMixin._pairings_adjacent([teams[3].subrank, team.subrank], 8), abs(i - 3) - 1)
        return [abs(i - 3) - 1 for i in range(8)]

    def test_pairings_fold_adj_deviation(self):
        teams = [TestTeam(i+1, chr(ord('A') + i), subrank=i+1) for i in range(8)]
        methods = [self.test_pairings_fold_deviation, self.test_pairings_adjacent_deviation]
        for i, method in enumerate(methods):
            for j, (team, expected) in enumerate(zip(teams, method())):
                self.assertEqual(GraphCostMixin._pairings_fold_top_adjacent_rest([teams[3].subrank, team.subrank], 8, bracket=i), expected)

    def test_add_pullup_penalty(self):
        teams = [TestTeam(i+1, chr(ord('A') + i), points=i, subrank=i+1, pullup_debates=i+1) for i in range(2)]
        gcm = GraphPowerPairedDrawGenerator(teams)
        gcm.options = {'pullup_debates_penalty': 1, 'pairing_method': 'random', 'pairing_penalty': 1, 'avoid_history': False, 'avoid_institution': False, 'side_allocations': False}
        gcm.team_flags = {teams[0]: ['pullup']}
        self.assertAlmostEqual(gcm.assignment_cost(*teams, 2), 2, delta=1e-6)

    def test_add_subrank_pullup(self):
        teams = [TestTeam(i+1, chr(ord('A') + i), subrank=(None if i else 1)) for i in range(2)]
        gcm = GraphPowerPairedDrawGenerator(teams)
        gcm.options = {'pullup_debates_penalty': 1, 'pairing_method': 'fold', 'avoid_history': False, 'avoid_institution': False, 'side_allocations': False, 'pairing_penalty': 1}
        self.assertEqual(gcm.assignment_cost(*teams, 2), 0)

    def test_none_self_penalty(self):
        team = TestTeam(1, 'A')
        gcm = GraphPowerPairedDrawGenerator([team, team])
        gcm.options = {'pullup_debates_penalty': 1, 'pairing_method': 'fold', 'avoid_history': False, 'avoid_institution': False, 'side_allocations': False, 'pairing_penalty': 1}
        self.assertEqual(gcm.assignment_cost(team, team, 2), None)

    def test_none_max_side_balance_penalty(self):
        teams = [TestTeam(1, 'A', side_history=(2, 0), subrank=1), TestTeam(2, 'B', side_history=(1, 1), subrank=2)]
        gcm = GraphPowerPairedDrawGenerator(teams)
        gcm.options = {'side_allocations': 'balance', 'max_times_on_one_side': 1,
                       'avoid_history': False, 'avoid_institution': False, 'side_penalty': 1, 'pairing_method': 'fold', 'pairing_penalty': 1, 'pullup_debates_penalty': 1}
        cost = gcm.assignment_cost(*teams, 2)
        self.assertEqual(cost, None)

    def test_graph_avoid_history_bans_rematch(self):
        teams = [TestTeam(1, 'A', hist=[2]), TestTeam(2, 'B', hist=[1])]
        gcm = GraphPowerPairedDrawGenerator(teams)
        gcm.options = {'avoid_history': True, 'avoid_institution': False, 'side_allocations': False,
                       'pairing_method': 'random', 'pullup_debates_penalty': 0}
        self.assertEqual(gcm.assignment_cost(*teams, 2), None)

    def test_bracket_penalty_cross_bracket(self):
        teams = [TestTeam(1, 'A', points=3, subrank=1, pullup_magnitude=0),
                 TestTeam(2, 'B', points=2, subrank=1, pullup_magnitude=0)]
        gcm = SingleGraphPowerPairedDrawGenerator(teams)
        gcm.n_teams_per_points = {2: 5, 3: 3}
        base_options = {'avoid_history': False, 'avoid_institution': False, 'side_allocations': False,
                        'pairing_method': 'random', 'pairing_penalty': 1, 'pullup_penalty': 0, 'pullup_debates_penalty': 0}
        gcm.options = {**base_options, 'bracket_penalty': 0}
        cost_without = gcm.assignment_cost(*teams, 8)
        gcm.options = {**base_options, 'bracket_penalty': 1}
        cost_with = gcm.assignment_cost(*teams, 8)
        self.assertAlmostEqual(cost_without, 0, delta=1e-6)
        self.assertAlmostEqual(cost_with, 1, delta=1e-6)

    def test_bracket_penalty_scales_with_pullup_buckets(self):
        teams = [TestTeam(1, 'A', points=3, subrank=1, pullup_magnitude=0),
                 TestTeam(2, 'B', points=2, subrank=1, pullup_magnitude=0)]
        gcm = SingleGraphPowerPairedDrawGenerator(teams)
        gcm.n_teams_per_points = {2: 5, 3: 3}
        gcm.options = {'avoid_history': False, 'avoid_institution': False, 'side_allocations': False,
                       'pairing_method': 'random', 'pairing_penalty': 1, 'pullup_penalty': 10, 'pullup_debates_penalty': 0,
                       'bracket_penalty': 1}
        # gap=1, scale=(2-1)*10+1=11
        self.assertAlmostEqual(gcm.assignment_cost(*teams, 8), 11, delta=1e-6)

    def test_bracket_penalty_same_bracket(self):
        teams = [TestTeam(1, 'A', points=3, subrank=1), TestTeam(2, 'B', points=3, subrank=2)]
        gcm = SingleGraphPowerPairedDrawGenerator(teams)
        gcm.n_teams_per_points = {3: 2}
        gcm.options = {'avoid_history': False, 'avoid_institution': False, 'side_allocations': False,
                       'pairing_method': 'random', 'pairing_penalty': 1, 'pullup_penalty': 0, 'pullup_debates_penalty': 0,
                       'bracket_penalty': 1}
        self.assertAlmostEqual(gcm.assignment_cost(*teams, 2), 0, delta=1e-6)

    def test_pullup_lowest_ds_rank_none_first(self):
        teams = [
            TestTeam(1, 'A', draw_strength_rank=5.0),
            TestTeam(2, 'B', draw_strength_rank=None),
            TestTeam(3, 'C', draw_strength_rank=3.0),
        ]
        sort_key = SingleGraphPowerPairedDrawGenerator._pullup_lowest_ds_rank
        sorted_teams = sorted(teams, key=sort_key)
        self.assertEqual(sorted_teams[0], teams[1])
        self.assertEqual(sorted_teams[1], teams[0])
        self.assertEqual(sorted_teams[2], teams[2])

    def test_pullup_lowest_ds_rank_npulls_none_first(self):
        teams = [
            TestTeam(1, 'A', npullups=0, draw_strength_rank=5.0),
            TestTeam(2, 'B', npullups=0, draw_strength_rank=None),
            TestTeam(3, 'C', npullups=1, draw_strength_rank=None),
        ]
        sort_key = SingleGraphPowerPairedDrawGenerator._pullup_lowest_ds_rank_npulls
        sorted_teams = sorted(teams, key=sort_key)
        self.assertEqual(sorted_teams[0], teams[1])
        self.assertEqual(sorted_teams[1], teams[0])
        self.assertEqual(sorted_teams[2], teams[2])

    def test_bracket_penalty_scales_with_gap_and_pairing(self):
        teams = [TestTeam(1, 'A', points=3, subrank=1, pullup_magnitude=0),
                 TestTeam(2, 'B', points=1, subrank=1, pullup_magnitude=0)]
        gcm = SingleGraphPowerPairedDrawGenerator(teams, pairing_method='fold', pairing_penalty=10,
            avoid_history=False, avoid_institution=False, side_allocations='none')
        gcm.n_teams_per_points = {1: 2, 2: 0, 3: 2}
        cost_without = gcm.assignment_cost(*teams, 4)
        gcm.options['bracket_penalty'] = 2
        self.assertEqual(gcm.assignment_cost(*teams, 4) - cost_without, 2 ** 2 * 2 * (2 * 10 + 1))

    def test_single_graph_uses_cross_bracket_pairs_to_avoid_rematches(self):
        teams = [TestTeam(1, 'A', points=3, subrank=1, hist=[2]),
                 TestTeam(2, 'B', points=3, subrank=2, hist=[1]),
                 TestTeam(3, 'C', points=2, subrank=1),
                 TestTeam(4, 'D', points=2, subrank=2)]
        generator = SingleGraphPowerPairedDrawGenerator(teams, pairing_method='fold',
            odd_bracket='pullup_top', bracket_penalty=100, avoid_institution=False, side_allocations='none')
        draw = generator.generate()
        self.assertEqual(len(draw), 2)
        self.assertEqual({team.id for pairing in draw for team in pairing.teams}, {1, 2, 3, 4})
        for pairing in draw:
            first, second = pairing.teams
            self.assertFalse(first.seen(second))
            self.assertNotEqual(first.points, second.points)
