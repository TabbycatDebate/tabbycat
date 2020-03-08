import copy
import unittest

from collections import OrderedDict

from .utils import TestTeam
from .. import DrawFatalError, DrawGenerator, DrawUserError
from ..generator.pairing import Pairing, ResultPairing
from ..generator.utils import partial_break_round_split

DUMMY_TEAMS = [TestTeam(1, 'A', allocated_side="aff"), TestTeam(2, 'B', allocated_side="neg")]


class TestRandomDrawGenerator(unittest.TestCase):
    """Basic unit test for random draws.
    Because it's random, you can't really do much to test it."""

    teams = [(1, 'A'), (2, 'B'), (3, 'A'), (4, 'B'), (5, 'C'), (6, 'D'),
             (7, 'E'), (8, 'A'), (9, 'D'), (10, 'E'), (11, 'D'), (12, 'A')]

    def test_invalid_option(self):
        teams = [TestTeam(*args, side_history=[0, 0]) for args in self.teams]

        def go():
            self.rd = DrawGenerator("two", "random", teams, None, random=True)
        self.assertRaises(ValueError, go)

    def test_draw(self):
        for i in range(100):
            teams = [TestTeam(*args, side_history=[0, 0]) for args in self.teams]
            self.rd = DrawGenerator("two", "random", teams, None, avoid_conflicts="on")
            _draw = self.rd.generate()
            for pairing in _draw:
                aff = pairing.teams[0]
                neg = pairing.teams[1]
                if aff.seen(neg) or neg.seen(aff) or aff.institution == neg.institution:
                    print(pairing)
                    self.assertEqual(pairing.flags, ["max_swapped"])
                else:
                    self.assertEqual(pairing.flags, [])


class TestPowerPairedDrawGeneratorParts(unittest.TestCase):
    """Basic unit test for core functionality of power-paired draws.
    Nowhere near comprehensive."""

    brackets = OrderedDict([
        (4, [1, 2, 3, 4, 5]),
        (3, [6, 7, 8, 9]),
        (2, [10, 11, 12, 13, 14]),
        (1, [15, 16]),
    ])

    def setUp(self):
        self.b2 = copy.deepcopy(self.brackets)
        self.ppd = DrawGenerator("two", "power_paired", DUMMY_TEAMS, None)

    def tearDown(self):
        del self.b2
        del self.ppd

    def bracket_resolve_odd(self, name, expected):
        self.ppd.options["odd_bracket"] = name
        self.ppd.resolve_odd_brackets(self.b2)
        self.assertDictEqual(self.b2, expected)

    def test_pullup_invalid(self):
        brackets = OrderedDict([
            (4, [1, 2, 3, 4, 5]),
            (3, [6, 7, 8]),
            (2, [9, 10, 11, 12, 13]),
            (1, [14, 15]),
        ])
        for method in ["pullup_top", "pullup_bottom", "pullup_random", "intermediate"]:
            with self.subTest(method=method):
                b2 = copy.deepcopy(brackets)
                self.ppd.options["odd_bracket"] = method
                self.assertRaises(DrawFatalError, self.ppd.resolve_odd_brackets, b2)

    def test_pullup_top(self):
        self.bracket_resolve_odd("pullup_top", OrderedDict([
            (4, [1, 2, 3, 4, 5, 6]),
            (3, [7, 8, 9, 10]),
            (2, [11, 12, 13, 14]),
            (1, [15, 16]),
        ]))

    def test_pullup_bottom(self):
        self.bracket_resolve_odd("pullup_bottom", OrderedDict([
            (4, [1, 2, 3, 4, 5, 9]),
            (3, [6, 7, 8, 14]),
            (2, [10, 11, 12, 13]),
            (1, [15, 16]),
        ]))

    def test_intermediate_brackets(self):
        self.bracket_resolve_odd("intermediate", OrderedDict([
            (4, [1, 2, 3, 4]),
            (3.5, [5, 6]),
            (3, [7, 8]),
            (2.5, [9, 10]),
            (2, [11, 12, 13, 14]),
            (1, [15, 16]),
        ]))

    def test_pullup_random(self):
        for j in range(5):
            b2 = self.b2
            self.ppd.options["odd_bracket"] = "pullup_random"
            self.ppd.resolve_odd_brackets(b2)
            self.assertTrue(all(i in b2[4] for i in [1, 2, 3, 4, 5]))
            self.assertEqual([i in b2[4] for i in [6, 7, 8, 9]].count(True), 1)
            self.assertEqual([i in b2[3] for i in [6, 7, 8, 9]].count(True), 3)
            self.assertEqual([i in b2[3] for i in [10, 11, 12, 13, 14]].count(True), 1)
            self.assertEqual([i in b2[2] for i in [10, 11, 12, 13, 14]].count(True), 4)
            self.assertEqual([15, 16], b2[1])

    def brackets_intermediate_bubble_up_down(self, brackets, expected):
        b2 = copy.deepcopy(brackets)
        expected_team_flags = dict()
        # Set up the brackets
        for p, b in b2.items():
            for i, x in enumerate(b):
                if isinstance(x[-1], str) and len(x) > 2:
                    flags = [x[-1]]
                    x = x[:-1]
                else:
                    flags = None
                if len(x) == 2:
                    t = TestTeam(x[0], x[1], p)
                else:
                    t = TestTeam(x[0], x[1], p, x[2:])
                b[i] = t
                expected_team_flags[t] = flags
        # Run the odd bracket resolution
        self.ppd.options["odd_bracket"] = "intermediate_bubble_up_down"
        self.ppd.resolve_odd_brackets(b2)
        # Check that the brackets are correct
        b3 = dict()
        for p, b in b2.items():
            b3[p] = [x.id for x in b]
        self.assertDictEqual(b3, expected)
        # Check that the team flags worked
        for team, flags in expected_team_flags.items():
            if team in self.ppd.team_flags:
                self.assertEqual(self.ppd.team_flags[team], flags)
            else:
                self.assertIsNone(flags)

    def test_intermediate_brackets_avoid_conflicts_1(self):
        brackets = OrderedDict([
            (4, [(1, 'A'), (2, 'B'), (3, 'C'), (4, 'A', 'bub_up_accom'), (5, 'C', 12, 'bub_up_inst')]),
            (3, [(6, 'C'), (7, 'D'), (8, 'A', 10), (9, 'B', 10)]),
            (2, [(10, 'D', 8, 9, 'bub_dn_hist'), (11, 'A', 'bub_dn_accom'), (12, 'C', 5), (13, 'B'), (14, 'C', 15)]),
            (1, [(15, 'C', 14), (16, 'C')]),
        ])
        expected = OrderedDict([
            (4, [1, 2, 3, 5]),
            (3.5, [4, 6]),  # Bubble-up (institution)
            (3, [7, 8]),
            (2.5, [9, 11]),  # Bubble-down (history, history)
            (2, [10, 12, 13, 14]),
            (1, [15, 16]),
        ])
        self.brackets_intermediate_bubble_up_down(brackets, expected)

    def test_intermediate_brackets_avoid_conflicts_2(self):
        brackets = OrderedDict([
            (4, [(1, 'A'), (2, 'B'), (3, 'C'), (4, 'A', 'bub_up_accom'), (5, 'C', 12, 'bub_up_inst')]),
            (3, [(6, 'C'), (7, 'D'), (8, 'A', 'bub_up_accom'), (9, 'B', 10, 'bub_up_hist')]),
            (2, [(10, 'D', 9), (11, 'A'), (12, 'C', 5), (13, 'B'), (14, 'C', 15)]),
            (1, [(15, 'C', 14), (16, 'C')]),
        ])
        expected = OrderedDict([
            (4, [1, 2, 3, 5]),
            (3.5, [4, 6]),  # Bubble-up (institution)
            (3, [7, 9]),
            (2.5, [8, 10]),  # Bubble-up (history)
            (2, [11, 12, 13, 14]),
            (1, [15, 16]),
        ])
        self.brackets_intermediate_bubble_up_down(brackets, expected)

    def test_intermediate_brackets_avoid_conflicts_3(self):
        brackets = OrderedDict([
            (4, [(1, 'A'), (2, 'B'), (3, 'C'), (4, 'A', 'bub_up_accom'), (5, 'C', 12, 'bub_up_inst')]),
            (3, [(6, 'C'), (7, 'D'), (8, 'D'), (9, 'B', 10)]),
            (2, [(10, 'D', 9, 'bub_dn_hist'), (11, 'A', 'bub_dn_accom'), (12, 'C', 5), (13, 'B'), (14, 'C', 15)]),
            (1, [(15, 'C', 14), (16, 'C')]),
        ])
        expected = OrderedDict([
            (4, [1, 2, 3, 5]),
            (3.5, [4, 6]),  # bubble-up (institution)
            (3, [7, 8]),
            (2.5, [9, 11]),  # bubble-down (history, institution)
            (2, [10, 12, 13, 14]),
            (1, [15, 16]),
        ])
        self.brackets_intermediate_bubble_up_down(brackets, expected)

    def test_intermediate_brackets_avoid_conflicts_none(self):
        brackets = OrderedDict([
            (4, [(1, 'A'), (2, 'B'), (3, 'C'), (4, 'A'), (5, 'C', 12)]),
            (3, [(6, 'B'), (7, 'D'), (8, 'D'), (9, 'B')]),
            (2, [(10, 'D'), (11, 'A'), (12, 'C', 5), (13, 'B'), (14, 'C', 15)]),
            (1, [(15, 'C', 14), (16, 'C')]),
        ])
        expected = OrderedDict([
            (4, [1, 2, 3, 4]),
            (3.5, [5, 6]),
            (3, [7, 8]),
            (2.5, [9, 10]),
            (2, [11, 12, 13, 14]),
            (1, [15, 16]),
        ])
        self.brackets_intermediate_bubble_up_down(brackets, expected)

    def test_intermediate_brackets_avoid_conflicts_exhaust(self):
        brackets = OrderedDict([
            (4, [(1, 'A'), (2, 'B'), (3, 'C'), (4, 'A', 'bub_up_accom'), (5, 'C', 12, 'bub_up_inst')]),
            (3, [(6, 'C'), (7, 'D'), (8, 'D'), (9, 'B', 10, 'no_bub_updn')]),
            (2, [(10, 'D', 9), (11, 'B'), (12, 'C', 5), (13, 'B'), (14, 'C', 15)]),
            (1, [(15, 'C', 14), (16, 'C')]),
        ])
        expected = OrderedDict([
            (4, [1, 2, 3, 5]),
            (3.5, [4, 6]),  # Bubble-up (institution)
            (3, [7, 8]),
            (2.5, [9, 10]),  # No bubble (exhausted)
            (2, [11, 12, 13, 14]),
            (1, [15, 16]),
        ])
        self.brackets_intermediate_bubble_up_down(brackets, expected)

    def pairings(self, name, expected):
        ppd = self.ppd
        ppd.options["odd_bracket"] = "pullup_top"
        ppd.options["pairing_method"] = name
        ppd.resolve_odd_brackets(self.b2)
        pairings = ppd.generate_pairings(self.b2)
        pairings_list = list()
        for bracket in pairings.values():
            pairings_list.extend(bracket)
        result = tuple(tuple(p.teams) for p in pairings_list)
        self.assertEqual(result, expected)

    def test_pairings_fold(self):
        self.pairings("fold", (
            (1, 6), (2, 5), (3, 4), (7, 10), (8, 9), (11, 14), (12, 13), (15, 16),
        ))

    def test_pairings_slide(self):
        self.pairings("slide", (
            (1, 4), (2, 5), (3, 6), (7, 9), (8, 10), (11, 13), (12, 14), (15, 16),
        ))

    def test_pairings_adjacent(self):
        self.pairings("adjacent", (
            (1, 2), (3, 4), (5, 6), (7, 8), (9, 10), (11, 12), (13, 14), (15, 16),
        ))

    def one_up_one_down(self, data, expected, **options):
        for option, value in options.items():
            self.ppd.options[option] = value
        pairings = []
        for data1, data2 in data:
            team1 = TestTeam(*data1)
            team2 = TestTeam(*data2)
            pairing = Pairing([team1, team2], None, None)
            pairings.append(pairing)
        pairings_dict = {0: pairings}
        self.ppd.avoid_conflicts(pairings_dict)
        self.assertEqual(len(expected), len(pairings))
        for (exp_teams, exp_flags), pair in zip(expected, pairings):
            self.assertEqual(tuple(t.id for t in pair.teams), exp_teams)
            self.assertEqual(pair.flags, exp_flags)

    @staticmethod
    def _1u1d_no_change(data):
        return [((t1[0], t2[0]), []) for t1, t2 in data]

    def test_no_swap(self):
        data = (((1, 'A'), (5, 'B')),
                ((2, 'C'), (6, 'A')),
                ((3, 'B'), (7, 'D')),
                ((4, 'C'), (8, 'A')))
        expected = self._1u1d_no_change(data)
        self.one_up_one_down(data, expected)

    def test_swap_institution(self):
        data = (((1, 'A'), (5, 'A')),
                ((2, 'C'), (6, 'B')),
                ((3, 'B'), (7, 'D')),
                ((4, 'C'), (8, 'A')))
        expected = [((1, 6), ["1u1d_inst"]),
                    ((2, 5), ["1u1d_other"]),
                    ((3, 7), []),
                    ((4, 8), [])]
        self.one_up_one_down(data, expected)

    def test_no_swap_institution(self):
        data = (((1, 'A'), (5, 'A')),
                ((2, 'C'), (6, 'B')),
                ((3, 'B'), (7, 'D')),
                ((4, 'C'), (8, 'A')))
        expected = self._1u1d_no_change(data)
        self.one_up_one_down(data, expected, avoid_institution=False)

    def test_swap_history(self):
        data = (((1, 'A', None, 5), (5, 'B')),
                ((2, 'C'), (6, 'A')),
                ((3, 'B'), (7, 'D')),
                ((4, 'C'), (8, 'A')))
        expected = [((1, 6), ["1u1d_hist"]),
                    ((2, 5), ["1u1d_other"]),
                    ((3, 7), []),
                    ((4, 8), [])]
        self.one_up_one_down(data, expected)

    def test_no_swap_history(self):
        data = (((1, 'A', None, 5), (5, 'B')),
                ((2, 'C'), (6, 'A')),
                ((3, 'B'), (7, 'D')),
                ((4, 'C'), (8, 'A')))
        expected = self._1u1d_no_change(data)
        self.one_up_one_down(data, expected, avoid_history=False)

    def test_last_swap(self):
        data = (((1, 'A'), (5, 'B')),
                ((2, 'C'), (6, 'A')),
                ((3, 'B'), (7, 'D')),
                ((4, 'C', None, 8), (8, 'A')))
        expected = [((1, 5), []),
                    ((2, 6), []),
                    ((3, 8), ["1u1d_other"]),
                    ((4, 7), ["1u1d_hist"])]
        self.one_up_one_down(data, expected)


class TestPowerPairedDrawGenerator(unittest.TestCase):
    """Test the entire draw functions as a black box."""

    # Yep, I spent a lot of time constructing this realistic hypothetical
    # situation with lots of swaps and manually figuring out the anticipated
    # result.
    standings = dict()
    standings[1] = [((12, 'B', 4, [26, 11, 15, 14]), {"side_history": [2, 2], "allocated_side": "aff"}),
                    ((2,  'D', 3, [22, 16, 20, 10]), {"side_history": [2, 2], "allocated_side": "aff"}),
                    ((3,  'E', 3, [23, 20, 25,  4]), {"side_history": [2, 2], "allocated_side": "aff"}),
                    ((11, 'B', 3, [1,  12, 23, 22]), {"side_history": [2, 2], "allocated_side": "neg"}),
                    ((6,  'E', 3, [19, 15, 18,  9]), {"side_history": [2, 2], "allocated_side": "neg"}),
                    ((17, 'E', 3, [21, 14,  7, 25]), {"side_history": [2, 2], "allocated_side": "neg"}),
                    ((4,  'B', 3, [18, 25,  5,  3]), {"side_history": [3, 1], "allocated_side": "aff"}),
                    ((14, 'A', 3, [24, 17,  9, 12]), {"side_history": [2, 2], "allocated_side": "aff"}),
                    ((8,  'A', 3, [15, 24,  1, 15]), {"side_history": [2, 2], "allocated_side": "neg"}),
                    ((7,  'D', 2, [16,  9, 17, 16]), {"side_history": [2, 2], "allocated_side": "aff"}),
                    ((9,  'D', 2, [5,   7, 14,  6]), {"side_history": [2, 2], "allocated_side": "aff"}),
                    ((15, 'B', 2, [8,   6, 12,  8]), {"side_history": [2, 2], "allocated_side": "neg"}),
                    ((18, 'B', 2, [4,  21,  6, 21]), {"side_history": [2, 2], "allocated_side": "neg"}),
                    ((22, 'A', 2, [2,  10, 16, 11]), {"side_history": [2, 2], "allocated_side": "neg"}),
                    ((23, 'A', 2, [3,  19, 11,  5]), {"side_history": [2, 2], "allocated_side": "aff"}),
                    ((24, 'B', 2, [14,  8, 19, 20]), {"side_history": [3, 1], "allocated_side": "aff"}),
                    ((25, 'A', 2, [10,  4,  3, 17]), {"side_history": [3, 1], "allocated_side": "aff"}),
                    ((1,  'C', 1, [11, 26,  8, 19]), {"side_history": [2, 2], "allocated_side": "neg"}),
                    ((5,  'C', 1, [9,  13,  4, 23]), {"side_history": [1, 3], "allocated_side": "neg"}),
                    ((10, 'B', 1, [25, 22, 13,  2]), {"side_history": [1, 3], "allocated_side": "aff"}),
                    ((16, 'D', 1, [7,   2, 22,  7]), {"side_history": [2, 2], "allocated_side": "neg"}),
                    ((20, 'E', 1, [13,  3,  2, 24]), {"side_history": [2, 2], "allocated_side": "aff"}),
                    ((21, 'A', 1, [17, 18, 26, 18]), {"side_history": [2, 2], "allocated_side": "aff"}),
                    ((19, 'B', 1, [6,  23, 24,  1]), {"side_history": [1, 3], "allocated_side": "neg"}),
                    ((26, 'B', 1, [12,  1, 21, 13]), {"side_history": [2, 2], "allocated_side": "neg"}),
                    ((13, 'C', 0, [20,  5, 10, 26]), {"side_history": [2, 2], "allocated_side": "neg"})]

    expected = dict()
    expected[1] = [dict(
        odd_bracket="pullup_top", pairing_method="slide", avoid_conflicts="one_up_one_down", side_allocations="balance"),
        [(12,  2, [], [], ["pullup"], True),
         (3,  14, ["1u1d_hist"], [], [], True),
         (11,  4, ["1u1d_other"], [], [], False),
         (6,   7, ["1u1d_other"], [], ["pullup"], True),
         (17,  8, ["1u1d_hist"], [], [], True),
         (9,  24, ["1u1d_other"], [], [], False),
         (15, 23, ["1u1d_inst"], [], [], True),
         (18, 25, [], [], [], False),
         (22,  1, [], [], ["pullup"], True),
         (5,  19, ["1u1d_other"], [], [], True),
         (10, 21, ["1u1d_inst"], [], [], False),
         (16, 13, ["1u1d_other"], [], ["pullup"], True),
         (20, 26, ["1u1d_hist"], [], [], True)]]

    expected[2] = [dict(
        odd_bracket="intermediate_bubble_up_down", pairing_method="slide", avoid_conflicts="one_up_one_down", side_allocations="balance"),
        [(12, 2, [], [], [], True),
         (3, 17, [], [], [], True),  # institution conflict, but swapping
                             # would give history conflict
         (11, 14, ["1u1d_inst"], [], [], True),
         (6, 4, ["1u1d_other"], [], [], False),
         (8, 7, [], [], [], True),
         (9, 22, [], [], [], True),
         (15, 23, [], [], [], True),
         (18, 24, [], [], [], False),
         (1, 25, [], [], [], False),
         (5, 20, [], [], [], False),
         (10, 21, [], [], [], False),
         (16, 26, [], [], ["bub_up_hist"], True),
         (19, 13, [], ["bub_up_accom"], [], False)]]

    expected[3] = [dict(
        odd_bracket="intermediate1", pairing_method="fold", avoid_conflicts="off", side_allocations="preallocated"),
        [(12, 11, [], [], [], False),
         (2,   8, [], [], [], False),
         (3,  17, [], [], [], False),
         (4,   6, [], [], [], False),
         (14, 15, [], [], [], False),
         (7,  22, [], [], [], False),
         (9,  18, [], [], [], False),
         (23, 16, [], [], [], False),
         (24,  5, [], [], [], False),
         (25,  1, [], [], [], False),
         (10, 26, [], [], [], False),
         (20, 19, [], [], [], False),
         (21, 13, [], [], [], False)]]

    expected[4] = [dict(
        odd_bracket="intermediate2", pairing_method="fold", avoid_conflicts="off", side_allocations="preallocated"),
        [(12, 11, [], [], [], False),
         (2,   8, [], [], [], False),
         (3,  17, [], [], [], False),
         (4,   6, [], [], [], False),
         (14, 15, [], [], [], False),
         (7,  22, [], [], [], False),
         (9,  18, [], [], [], False),
         (23, 16, [], [], [], False),
         (24,  5, [], [], [], False),
         (25,  1, [], [], [], False),
         (10, 26, [], [], [], False),
         (20, 19, [], [], [], False),
         (21, 13, [], [], [], False)]]

    combinations = [(1, 1), (1, 2), (1, 3), (1, 4)]

    def do_draw(self, standings, options):
        standings = [TestTeam(*args, **kwargs) for args, kwargs in standings]
        self.ppd = DrawGenerator("two", "power_paired", standings, None, **options)
        return self.ppd.generate()

    def test_draw(self):
        for standings_key, expected_key in self.combinations:
            with self.subTest(standings=standings_key, expected=expected_key):
                standings = self.standings[standings_key]
                kwargs, expected = self.expected[expected_key]
                draw = self.do_draw(standings, kwargs)

                for actual, (exp_aff, exp_neg, exp_flags, exp_aff_flags, exp_neg_flags, same_affs) in zip(draw, expected):
                    actual_teams = tuple([t.id for t in actual.teams])
                    expected_teams = (exp_aff, exp_neg)

                    if same_affs:
                        self.assertCountEqual(actual_teams, expected_teams)
                    else:
                        self.assertEqual(actual_teams, expected_teams)

                    self.assertEqual(actual.flags, exp_flags)

                    if exp_aff == actual.teams[0].id:
                        self.assertEqual(actual.get_team_flags(actual.teams[0]), exp_aff_flags)
                        self.assertEqual(actual.get_team_flags(actual.teams[1]), exp_neg_flags)
                    else:
                        self.assertEqual(actual.get_team_flags(actual.teams[1]), exp_aff_flags)
                        self.assertEqual(actual.get_team_flags(actual.teams[0]), exp_neg_flags)


class TestPowerPairedWithAllocatedSidesDrawGeneratorPartOddBrackets(unittest.TestCase):
    """Basic unit test for core functionality of power-paired draws with allocated
    sides. Not comprehensive."""

    # Input dictionaries, groups that may have odd brackets.
    brackets = dict()
    brackets[1] = OrderedDict([
        (5, {"aff": [1], "neg": [14]}),
        (4, {"aff": [2, 3], "neg": [15]}),
        (3, {"aff": [4, 5, 6, 7, 8], "neg": [16, 17, 18]}),
        (2, {"aff": [9, 10], "neg": [19, 20, 21]}),
        (1, {"aff": [11, 12], "neg": [22, 23, 24, 25]}),
        (0, {"aff": [13], "neg": [26]}),
    ])
    brackets[2] = OrderedDict([
        (5, {"aff": [], "neg": [16, 17]}),
        (4, {"aff": [1, 2, 3, 4], "neg": [18, 19, 20, 21]}),
        (3, {"aff": [5, 6, 7], "neg": [22, 23]}),
        (2, {"aff": [8, 9, 10], "neg": []}),
        (1, {"aff": [11, 12, 13, 14], "neg": [24, 25, 26, 27]}),
        (0, {"aff": [15], "neg": [28, 29, 30]}),
    ])
    brackets[3] = OrderedDict([
        (5, {"aff": [1, 2], "neg": []}),
        (4, {"aff": [3, 4], "neg": [13]}),
        (3, {"aff": [5, 6, 7, 8, 9], "neg": [14, 15, 16]}),
        (2, {"aff": [], "neg": [17, 18, 19]}),
        (1, {"aff": [10, 11], "neg": [20, 21, 22, 23, 24]}),
        (0, {"aff": [12], "neg": []}),
    ])
    brackets[4] = OrderedDict([
        (3, {"aff": ["Yale 2", "Stanford 2", "Yale 1"], "neg": []}),
        (2, {"aff": ["John Hopkins 1", "Stanford 1", "MIT 1", "Stanford 3", "Berkeley 1"], "neg": ["MIT 2", "Columbia 1", "Caltech 1", "Caltech 3"]}),  # noqa: E501
        (1, {"aff": ["Caltech 2", "Cornell 1", "Yale 3", "Princeton 1"], "neg": ["Chicago 2", "Chicago 1", "Pennsylvania 1", "Chicago 3", "Princeton 2"]}),  # noqa: E501
        (0, {"aff": [], "neg": ["Pennsylvania 2", "Harvard 1", "Harvard 2"]}),
    ])
    brackets[99] = OrderedDict([
        # Uneven aff/neg, should raise exception
        (5, {"aff": [1, 2], "neg": []}),
        (4, {"aff": [3, 4], "neg": [14]}),
        (3, {"aff": [5, 6, 7, 8, 9], "neg": [15, 16]}),
        (2, {"aff": [], "neg": [17, 18, 19, 20]}),
        (1, {"aff": [10, 11], "neg": [21, 22, 23, 24]}),
        (0, {"aff": [12, 13], "neg": []}),
    ])

    # Expected outputs, groups whose odd brackets should be resolved.
    # The first key is the method, the second key corresponds to the index of
    # the brackets dict above.
    expecteds = dict()
    expecteds["pullup_top"] = dict()
    expecteds["pullup_top"][1] = OrderedDict([
        (5, {"aff": [1], "neg": [14]}),
        (4, {"aff": [2, 3], "neg": [15, 16]}),
        (3, {"aff": [4, 5, 6, 7, 8], "neg": [17, 18, 19, 20, 21]}),
        (2, {"aff": [9, 10], "neg": [22, 23]}),
        (1, {"aff": [11, 12], "neg": [24, 25]}),
        (0, {"aff": [13], "neg": [26]}),
    ])
    expecteds["pullup_top"][2] = OrderedDict([
        (5, {"aff": [1, 2], "neg": [16, 17]}),
        (4, {"aff": [3, 4, 5, 6], "neg": [18, 19, 20, 21]}),
        (3, {"aff": [7, 8], "neg": [22, 23]}),
        (2, {"aff": [9, 10], "neg": [24, 25]}),
        (1, {"aff": [11, 12, 13, 14], "neg": [26, 27, 28, 29]}),
        (0, {"aff": [15], "neg": [30]}),
    ])
    expecteds["pullup_top"][3] = OrderedDict([
        (5, {"aff": [1, 2], "neg": [13, 14]}),
        (4, {"aff": [3, 4], "neg": [15, 16]}),
        (3, {"aff": [5, 6, 7, 8, 9], "neg": [17, 18, 19, 20, 21]}),
        (2, {"aff": [], "neg": []}),
        (1, {"aff": [10, 11, 12], "neg": [22, 23, 24]}),
        (0, {"aff": [], "neg": []}),
    ])
    expecteds["pullup_top"][4] = OrderedDict([
        (3, {"aff": ["Yale 2", "Stanford 2", "Yale 1"], "neg": ["MIT 2", "Columbia 1", "Caltech 1"]}),
        (2, {"aff": ["John Hopkins 1", "Stanford 1", "MIT 1", "Stanford 3", "Berkeley 1"], "neg": ["Caltech 3", "Chicago 2", "Chicago 1", "Pennsylvania 1", "Chicago 3"]}),  # noqa: E501
        (1, {"aff": ["Caltech 2", "Cornell 1", "Yale 3", "Princeton 1"], "neg": ["Princeton 2", "Pennsylvania 2", "Harvard 1", "Harvard 2"]}),  # noqa: E501
        (0, {"aff": [], "neg": []}),
    ])

    expecteds["pullup_bottom"] = dict()
    expecteds["pullup_bottom"][1] = OrderedDict([
        (5, {"aff": [1], "neg": [14]}),
        (4, {"aff": [2, 3], "neg": [15, 18]}),
        (3, {"aff": [4, 5, 6, 7, 8], "neg": [16, 17, 19, 20, 21]}),
        (2, {"aff": [9, 10], "neg": [24, 25]}),
        (1, {"aff": [11, 12], "neg": [22, 23]}),
        (0, {"aff": [13], "neg": [26]}),
    ])
    expecteds["pullup_bottom"][2] = OrderedDict([
        (5, {"aff": [3, 4], "neg": [16, 17]}),
        (4, {"aff": [1, 2, 6, 7], "neg": [18, 19, 20, 21]}),
        (3, {"aff": [5, 10], "neg": [22, 23]}),
        (2, {"aff": [8, 9], "neg": [26, 27]}),
        (1, {"aff": [11, 12, 13, 14], "neg": [24, 25, 29, 30]}),
        (0, {"aff": [15], "neg": [28]}),
    ])
    expecteds["pullup_bottom"][3] = OrderedDict([
        (5, {"aff": [1, 2], "neg": [13, 16]}),
        (4, {"aff": [3, 4], "neg": [14, 15]}),
        (3, {"aff": [5, 6, 7, 8, 9], "neg": [17, 18, 19, 23, 24]}),
        (2, {"aff": [], "neg": []}),
        (1, {"aff": [10, 11, 12], "neg": [20, 21, 22]}),
        (0, {"aff": [], "neg": []}),
    ])
    expecteds["pullup_bottom"][4] = OrderedDict([
        (3, {"aff": ["Yale 2", "Stanford 2", "Yale 1"], "neg": ["Columbia 1", "Caltech 1", "Caltech 3"]}),
        (2, {"aff": ["John Hopkins 1", "Stanford 1", "MIT 1", "Stanford 3", "Berkeley 1"], "neg": ["MIT 2", "Chicago 1", "Pennsylvania 1", "Chicago 3", "Princeton 2"]}),  # noqa: E501
        (1, {"aff": ["Caltech 2", "Cornell 1", "Yale 3", "Princeton 1"], "neg": ["Chicago 2", "Pennsylvania 2", "Harvard 1", "Harvard 2"]}),  # noqa: E501
        (0, {"aff": [], "neg": []}),
    ])

    expecteds["intermediate1"] = dict()
    expecteds["intermediate1"][1] = OrderedDict([
        (5,   {"aff": [1], "neg": [14]}),
        (4,   {"aff": [2], "neg": [15]}),
        (3.5, {"aff": [3], "neg": [16]}),
        (3,   {"aff": [4, 5], "neg": [17, 18]}),
        (2.5, {"aff": [6, 7, 8], "neg": [19, 20, 21]}),
        (2,   {"aff": [], "neg": []}),
        (1.5, {"aff": [9, 10], "neg": [22, 23]}),
        (1,   {"aff": [11, 12], "neg": [24, 25]}),
        (0,   {"aff": [13], "neg": [26]}),
    ])
    expecteds["intermediate1"][2] = OrderedDict([
        (5,   {"aff": [], "neg": []}),
        (4.5, {"aff": [1, 2], "neg": [16, 17]}),
        (4,   {"aff": [3, 4], "neg": [18, 19]}),
        (3.5, {"aff": [5, 6], "neg": [20, 21]}),
        (3,   {"aff": [7], "neg": [22]}),
        (2.5, {"aff": [8], "neg": [23]}),
        (2,   {"aff": [], "neg": []}),
        (1.5, {"aff": [9, 10], "neg": [24, 25]}),
        (1,   {"aff": [11, 12], "neg": [26, 27]}),
        (0.5, {"aff": [13, 14], "neg": [28, 29]}),
        (0,   {"aff": [15], "neg": [30]}),
    ])
    expecteds["intermediate1"][3] = OrderedDict([
        (5,   {"aff": [], "neg": []}),
        (4.5, {"aff": [1, 2], "neg": [13, 14]}),
        (4,   {"aff": [], "neg": []}),
        (3.5, {"aff": [3, 4], "neg": [15, 16]}),
        (3,   {"aff": [], "neg": []}),
        (2.5, {"aff": [5, 6, 7, 8, 9], "neg":[17, 18, 19, 20, 21]}),
        (2,   {"aff": [], "neg": []}),
        (1,   {"aff": [10, 11], "neg": [22, 23]}),
        (0.5, {"aff": [12], "neg": [24]}),
        (0,   {"aff": [], "neg": []}),
    ])
    expecteds["intermediate1"][4] = OrderedDict([
        (3,   {"aff": [], "neg": []}),
        (2.5, {"aff": ["Yale 2", "Stanford 2", "Yale 1"], "neg": ["MIT 2", "Columbia 1", "Caltech 1"]}),
        (2,   {"aff": ["John Hopkins 1"], "neg": ["Caltech 3"]}),
        (1.5, {"aff": ["Stanford 1", "MIT 1", "Stanford 3", "Berkeley 1"], "neg": ["Chicago 2", "Chicago 1", "Pennsylvania 1", "Chicago 3"]}),
        (1,   {"aff": ["Caltech 2"], "neg": ["Princeton 2"]}),
        (0.5, {"aff": ["Cornell 1", "Yale 3", "Princeton 1"], "neg": ["Pennsylvania 2", "Harvard 1", "Harvard 2"]}),
        (0,   {"aff": [], "neg": []}),
    ])

    expecteds["intermediate2"] = dict()
    expecteds["intermediate2"][1] = OrderedDict([
        (5,   {"aff": [1], "neg": [14]}),
        (4,   {"aff": [2], "neg": [15]}),
        (3.5, {"aff": [3], "neg": [16]}),
        (3,   {"aff": [4, 5], "neg": [17, 18]}),
        (2.5, {"aff": [6, 7, 8], "neg": [19, 20, 21]}),
        (2,   {"aff": [], "neg": []}),
        (1.5, {"aff": [9, 10], "neg": [22, 23]}),
        (1,   {"aff": [11, 12], "neg": [24, 25]}),
        (0,   {"aff": [13], "neg": [26]}),
    ])
    expecteds["intermediate2"][2] = OrderedDict([
        (5,   {"aff": [], "neg": []}),
        (4.5, {"aff": [1, 2], "neg": [16, 17]}),
        (4,   {"aff": [3, 4], "neg": [18, 19]}),
        (3.5, {"aff": [5, 6], "neg": [20, 21]}),
        (3,   {"aff": [7], "neg": [22]}),
        (2.5, {"aff": [8], "neg": [23]}),
        (2,   {"aff": [], "neg": []}),
        (1.5, {"aff": [9, 10], "neg": [24, 25]}),
        (1,   {"aff": [11, 12], "neg": [26, 27]}),
        (0.5, {"aff": [13, 14], "neg": [28, 29]}),
        (0,   {"aff": [15], "neg": [30]}),
    ])
    expecteds["intermediate2"][3] = OrderedDict([
        (5,      {"aff": [], "neg": []}),
        (4+2./3, {"aff": [1], "neg": [13]}),
        (4+1./3, {"aff": [2], "neg": [14]}),
        (4,      {"aff": [], "neg": []}),
        (3.5,    {"aff": [3, 4], "neg": [15, 16]}),
        (3,      {"aff": [], "neg": []}),
        (2+2./3, {"aff": [5, 6, 7], "neg":[17, 18, 19]}),
        (2+1./3, {"aff": [8, 9], "neg": [20, 21]}),
        (2,      {"aff": [], "neg": []}),
        (1,      {"aff": [10, 11], "neg": [22, 23]}),
        (0.5,    {"aff": [12], "neg": [24]}),
        (0,      {"aff": [], "neg": []}),
    ])
    expecteds["intermediate2"][4] = OrderedDict([
        (3,   {"aff": [], "neg": []}),
        (2.5, {"aff": ["Yale 2", "Stanford 2", "Yale 1"], "neg": ["MIT 2", "Columbia 1", "Caltech 1"]}),
        (2,   {"aff": ["John Hopkins 1"], "neg": ["Caltech 3"]}),
        (1.5, {"aff": ["Stanford 1", "MIT 1", "Stanford 3", "Berkeley 1"], "neg": ["Chicago 2", "Chicago 1", "Pennsylvania 1", "Chicago 3"]}),
        (1,   {"aff": ["Caltech 2"], "neg": ["Princeton 2"]}),
        (0.5, {"aff": ["Cornell 1", "Yale 3", "Princeton 1"], "neg": ["Pennsylvania 2", "Harvard 1", "Harvard 2"]}),
        (0,   {"aff": [], "neg": []}),
    ])

    def test_odd_bracket_resolution(self):
        for method, expected_results in self.expecteds.items():
            for index, expected in expected_results.items():
                with self.subTest(method=method, index=index):
                    ppd = DrawGenerator("two", "power_paired", DUMMY_TEAMS, None, side_allocations="preallocated", odd_bracket=method)
                    brackets = copy.deepcopy(self.brackets[index])
                    ppd.resolve_odd_brackets(brackets)
                    self.assertDictEqual(brackets, expected)

    def test_pullup_invalid(self):
        for method in ["pullup_top", "pullup_bottom", "pullup_random", "intermediate1", "intermediate2"]:
            with self.subTest(method=method):
                ppd = DrawGenerator("two", "power_paired", DUMMY_TEAMS, None, side_allocations="preallocated", odd_bracket=method)
                brackets = copy.deepcopy(self.brackets[99])
                self.assertRaises(DrawFatalError, ppd.resolve_odd_brackets, brackets)

    def test_pullup_random(self):
        for j in range(10):
            # Just doing the third one because it's hardest, too lazy to write
            # random tests for the others.
            b2 = copy.deepcopy(self.brackets[3])
            ppd = DrawGenerator("two", "power_paired", DUMMY_TEAMS, None, side_allocations="preallocated", odd_bracket="pullup_random")
            ppd.resolve_odd_brackets(b2)

            self.assertEqual(b2[5]["aff"], [1, 2])
            self.assertIn(13, b2[5]["neg"])
            self.assertEqual([i in b2[5]["neg"] for i in [14, 15, 16]].count(True), 1)
            self.assertEqual(b2[4]["aff"], [3, 4])
            self.assertEqual([i in b2[4]["neg"] for i in [14, 15, 16]].count(True), 2)
            self.assertCountEqual(b2[5]["neg"] + b2[4]["neg"], [13, 14, 15, 16])
            self.assertEqual(b2[3]["aff"], [5, 6, 7, 8, 9])
            self.assertTrue(all(i in b2[3]["neg"] for i in [17, 18, 19]))
            self.assertEqual([i in b2[3]["neg"] for i in [20, 21, 22, 23, 24]].count(True), 2)
            self.assertEqual(b2[2], {"aff": [], "neg": []})
            self.assertEqual(b2[1]["aff"], [10, 11, 12])
            self.assertEqual([i in b2[1]["neg"] for i in [20, 21, 22, 23, 24]].count(True), 3)
            self.assertEqual(b2[0], {"aff": [], "neg": []})


class TestPartialBreakRoundSplit(unittest.TestCase):

    def test_split(self):
        self.assertRaises(AssertionError, partial_break_round_split, -1)
        self.assertRaises(AssertionError, partial_break_round_split, 0)
        self.assertRaises(AssertionError, partial_break_round_split, 1)
        self.assertEqual(partial_break_round_split(2),  (1, 0))
        self.assertEqual(partial_break_round_split(3),  (1, 1))
        self.assertEqual(partial_break_round_split(4),  (2, 0))
        self.assertEqual(partial_break_round_split(5),  (1, 3))
        self.assertEqual(partial_break_round_split(6),  (2, 2))
        self.assertEqual(partial_break_round_split(7),  (3, 1))
        self.assertEqual(partial_break_round_split(8),  (4, 0))
        self.assertEqual(partial_break_round_split(11), (3, 5))
        self.assertEqual(partial_break_round_split(21), (5, 11))
        self.assertEqual(partial_break_round_split(24), (8, 8))
        self.assertEqual(partial_break_round_split(27), (11, 5))
        self.assertEqual(partial_break_round_split(31), (15, 1))
        self.assertEqual(partial_break_round_split(32), (16, 0))
        self.assertEqual(partial_break_round_split(45), (13, 19))
        self.assertEqual(partial_break_round_split(48), (16, 16))
        self.assertEqual(partial_break_round_split(61), (29, 3))
        self.assertEqual(partial_break_round_split(64), (32, 0))
        self.assertEqual(partial_break_round_split(99), (35, 29))


class BaseTestEliminationDrawGenerator(unittest.TestCase):

    # (Team Name, Team Institution)
    team_data = [(1, 'A'), (2, 'B'), (3, 'A'), (4, 'B'), (5, 'C'), (6, 'D'),
             (7, 'E'), (8, 'A'), (9, 'D'), (10, 'E'), (11, 'D'), (12, 'A')]

    def assertPairingsEqual(self, actual, expected):  # noqa: N802
        """Checks pairings without regard to sides."""
        for a, p in zip(actual, expected):
            self.assertCountEqual([team.id for team in a.teams], p)


class TestPartialEliminationDrawGenerator(BaseTestEliminationDrawGenerator):

    def test_even_numbers(self):
        # Run a draw with break size of 2; expect the each team's ID to be paired up as follows
        self.run_draw(2, [(1, 2)])
        self.run_draw(4, [(1, 4), (2, 3)])
        self.run_draw(8, [(1, 8), (2, 7), (3, 6), (4, 5)])

    def test_weird_numbers(self):
        self.run_draw(3, [(2, 3)])
        self.run_draw(5, [(4, 5)])
        self.run_draw(6, [(3, 6), (4, 5)])
        self.run_draw(12, [(5, 12), (6, 11), (7, 10), (8, 9)])

    def run_draw(self, break_size, expected):
        # Make the test team objects and generate their pairings
        teams = [TestTeam(*args) for args in self.team_data][:break_size]
        self.fed = DrawGenerator("two", "first_elimination", teams)
        pairings = self.fed.generate()
        self.assertPairingsEqual(pairings, expected)


class TestEliminationDrawGenerator(BaseTestEliminationDrawGenerator):

    def setUp(self):
        self.teams = [TestTeam(*args) for args in self.team_data]

    def t(self, teams):
        return lambda id: teams[id-1]

    def p(self, t):
        return lambda ids: list(map(t, ids))

    def _results(self, start_rank, *args):

        _t = self.t(self.teams)
        _p = self.p(_t)

        pairings = list()
        for i, (teams, winner) in enumerate(args, start=start_rank):
            pairing = ResultPairing(_p(teams), 0, i, winner=_t(winner))
            pairings.append(pairing)
        return pairings

    def _teams(self, *args):
        _t = self.t(self.teams)
        return list(map(_t, args))

    def test_no_bypass(self):
        teams = self._teams(1, 3, 4, 2, 5, 8, 9, 11, 10, 12) # it should take none of these
        results = self._results(1, ([1, 5], 1), ([6, 7], 7), ([3, 2], 3), ([4, 8], 8))
        self.run_draw(teams, results, [(1, 8), (7, 3)])

    def test_bypass(self):
        # teams 9 through 12 qualified 1st through 4th, so bypassed the first round
        teams = self._teams(9, 11, 10, 12, 1, 2, 3, 4, 5, 6, 7, 8)
        results = self._results(5, ([1, 5], 1), ([6, 7], 7), ([3, 2], 3), ([4, 8], 8))
        self.run_draw(teams, results, [(9, 8), (11, 3), (10, 7), (12, 1)])

    def test_error(self):
        # Test when number of teams is not a power of two
        teams = self._teams(1, 7, 3, 8, 9, 11)
        results = self._results(3, ([1, 5], 1), ([6, 7], 7), ([3, 2], 3), ([4, 8], 8))
        self.ed = DrawGenerator("two", "elimination", teams, results=results)
        self.assertRaises(DrawUserError, self.ed.generate)

    def run_draw(self, teams, results, expected):
        self.ed = DrawGenerator("two", "elimination", teams, results=results)
        pairings = self.ed.generate()
        self.assertPairingsEqual(pairings, expected)


if __name__ == '__main__':
    unittest.main()
