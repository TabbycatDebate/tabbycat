import os.path, sys
if os.path.abspath("..") not in sys.path: sys.path.append(os.path.abspath(".."))
import unittest
from collections import OrderedDict
from draw import DrawGenerator, Pairing, DrawError
import copy
from test_one_up_one_down import TestTeam

DUMMY_TEAMS = [TestTeam(1, 'A', allocated_side="aff"), TestTeam(2, 'B', allocated_side="neg")]

class TestRandomDrawGenerator(unittest.TestCase):
    """Basic unit test for random draws.
    Because it's random, you can't really do much to test it."""

    teams = [(1, 'A'), (2, 'B'), (3, 'A'), (4, 'B'), (5, 'C'), (6, 'D'),
             (7, 'E'), (8, 'A'), (9, 'D'), (10, 'E'), (11, 'D'), (12, 'A')]

    def test_invalid_option(self):
        teams = [TestTeam(*args) for args in self.teams]
        def go():
            self.rd = DrawGenerator("random", teams, random=True)
        self.assertRaises(ValueError, go)

    def test_draw(self):
        for i in xrange(100):
            teams = [TestTeam(*args) for args in self.teams]
            self.rd = DrawGenerator("random", teams)
            _draw = self.rd.make_draw()
            for pairing in _draw:
                if pairing.aff_team.seen(pairing.neg_team) or \
                        pairing.neg_team.seen(pairing.aff_team) or \
                        pairing.aff_team.institution == pairing.neg_team.institution:
                    print pairing
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
        (1, [15, 16])
    ])

    def setUp(self):
        self.b2 = copy.deepcopy(self.brackets)
        self.ppd = DrawGenerator("power_paired", DUMMY_TEAMS)

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
            (1, [14, 15])
        ])
        for name in ["pullup_top", "pullup_bottom", "pullup_random", "intermediate"]:
            b2 = copy.deepcopy(brackets)
            self.ppd.options["odd_bracket"] = name
            self.assertRaises(DrawError, self.ppd.resolve_odd_brackets, b2)

    def test_pullup_top(self):
        self.bracket_resolve_odd("pullup_top", OrderedDict([
            (4, [1, 2, 3, 4, 5, 6]),
            (3, [7, 8, 9, 10]),
            (2, [11, 12, 13, 14]),
            (1, [15, 16])
        ]))

    def test_pullup_bottom(self):
        self.bracket_resolve_odd("pullup_bottom", OrderedDict([
            (4, [1, 2, 3, 4, 5, 9]),
            (3, [6, 7, 8, 14]),
            (2, [10, 11, 12, 13]),
            (1, [15, 16])
        ]))

    def test_intermediate_brackets(self):
        self.bracket_resolve_odd("intermediate", OrderedDict([
            (4, [1, 2, 3, 4]),
            (3.5, [5, 6]),
            (3, [7, 8]),
            (2.5, [9, 10]),
            (2, [11, 12, 13, 14]),
            (1, [15, 16])
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

    def brackets_intermediate_avoid_conflicts(self, brackets, expected):
        b2 = copy.deepcopy(brackets)
        expected_team_flags = dict()
        # Set up the brackets
        for p, b in b2.iteritems():
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
        self.ppd.options["odd_bracket"] = "intermediate_avoid_conflicts"
        self.ppd.resolve_odd_brackets(b2)
        # Check that the brackets are correct
        b3 = dict()
        for p, b in b2.iteritems():
            b3[p] = map(lambda x: x.id, b)
        self.assertDictEqual(b3, expected)
        # Check that the team flags worked
        for team, flags in expected_team_flags.iteritems():
            if team in self.ppd.team_flags:
                self.assertEqual(self.ppd.team_flags[team], flags)
            else:
                self.assertIsNone(flags)

    def test_intermediate_brackets_avoid_conflicts_1(self):
        brackets = OrderedDict([
            (4, [(1, 'A'), (2, 'B'), (3, 'C'), (4, 'A', 'bub_up_accom'), (5, 'C', 12, 'bub_up_inst')]),
            (3, [(6, 'C'), (7, 'D'), (8, 'A', 10), (9, 'B', 10)]),
            (2, [(10, 'D', 8, 9, 'bub_dn_hist'), (11, 'A', 'bub_dn_accom'), (12, 'C', 5), (13, 'B'), (14, 'C', 15)]),
            (1, [(15, 'C', 14), (16, 'C')])
        ])
        expected = OrderedDict([
            (4, [1, 2, 3, 5]),
            (3.5, [4, 6]), # bubble-up (institution)
            (3, [7, 8]),
            (2.5, [9, 11]), # bubble-down (history, history)
            (2, [10, 12, 13, 14]),
            (1, [15, 16])
        ])
        self.brackets_intermediate_avoid_conflicts(brackets, expected)

    def test_intermediate_brackets_avoid_conflicts_2(self):
        brackets = OrderedDict([
            (4, [(1, 'A'), (2, 'B'), (3, 'C'), (4, 'A', 'bub_up_accom'), (5, 'C', 12, 'bub_up_inst')]),
            (3, [(6, 'C'), (7, 'D'), (8, 'A', 'bub_up_accom'), (9, 'B', 10, 'bub_up_hist')]),
            (2, [(10, 'D', 9), (11, 'A'), (12, 'C', 5), (13, 'B'), (14, 'C', 15)]),
            (1, [(15, 'C', 14), (16, 'C')])
        ])
        expected = OrderedDict([
            (4, [1, 2, 3, 5]),
            (3.5, [4, 6]), # bubble-up (institution)
            (3, [7, 9]),
            (2.5, [8, 10]), # bubble-up (history)
            (2, [11, 12, 13, 14]),
            (1, [15, 16])
        ])
        self.brackets_intermediate_avoid_conflicts(brackets, expected)

    def test_intermediate_brackets_avoid_conflicts_3(self):
        brackets = OrderedDict([
            (4, [(1, 'A'), (2, 'B'), (3, 'C'), (4, 'A', 'bub_up_accom'), (5, 'C', 12, 'bub_up_inst')]),
            (3, [(6, 'C'), (7, 'D'), (8, 'D'), (9, 'B', 10)]),
            (2, [(10, 'D', 9, 'bub_dn_hist'), (11, 'A', 'bub_dn_accom'), (12, 'C', 5), (13, 'B'), (14, 'C', 15)]),
            (1, [(15, 'C', 14), (16, 'C')])
        ])
        expected = OrderedDict([
            (4, [1, 2, 3, 5]),
            (3.5, [4, 6]), # bubble-up (institution)
            (3, [7, 8]),
            (2.5, [9, 11]), # bubble-down (history, institution)
            (2, [10, 12, 13, 14]),
            (1, [15, 16])
        ])
        self.brackets_intermediate_avoid_conflicts(brackets, expected)

    def test_intermediate_brackets_avoid_conflicts_none(self):
        brackets = OrderedDict([
            (4, [(1, 'A'), (2, 'B'), (3, 'C'), (4, 'A'), (5, 'C', 12)]),
            (3, [(6, 'B'), (7, 'D'), (8, 'D'), (9, 'B')]),
            (2, [(10, 'D'), (11, 'A'), (12, 'C', 5), (13, 'B'), (14, 'C', 15)]),
            (1, [(15, 'C', 14), (16, 'C')])
        ])
        expected = OrderedDict([
            (4, [1, 2, 3, 4]),
            (3.5, [5, 6]),
            (3, [7, 8]),
            (2.5, [9, 10]),
            (2, [11, 12, 13, 14]),
            (1, [15, 16])
        ])
        self.brackets_intermediate_avoid_conflicts(brackets, expected)

    def test_intermediate_brackets_avoid_conflicts_exhaust(self):
        brackets = OrderedDict([
            (4, [(1, 'A'), (2, 'B'), (3, 'C'), (4, 'A', 'bub_up_accom'), (5, 'C', 12, 'bub_up_inst')]),
            (3, [(6, 'C'), (7, 'D'), (8, 'D'), (9, 'B', 10, 'no_bub_updn')]),
            (2, [(10, 'D', 9), (11, 'B'), (12, 'C', 5), (13, 'B'), (14, 'C', 15)]),
            (1, [(15, 'C', 14), (16, 'C')])
        ])
        expected = OrderedDict([
            (4, [1, 2, 3, 5]),
            (3.5, [4, 6]), # bubble-up (institution)
            (3, [7, 8]),
            (2.5, [9, 10]), # no bubble (exhausted)
            (2, [11, 12, 13, 14]),
            (1, [15, 16])
        ])
        self.brackets_intermediate_avoid_conflicts(brackets, expected)

    def pairings(self, name, expected):
        ppd = self.ppd
        ppd.options["odd_bracket"] = "pullup_top"
        ppd.options["pairing_method"] = name
        ppd.resolve_odd_brackets(self.b2)
        pairings = ppd.generate_pairings(self.b2)
        pairings_list = list()
        for bracket in pairings.itervalues():
            pairings_list.extend(bracket)
        result = tuple(tuple(p.teams) for p in pairings_list)
        self.assertEqual(result, expected)

    def test_pairings_fold(self):
        self.pairings("fold", (
            (1, 6), (2, 5), (3, 4), (7, 10), (8, 9), (11, 14), (12, 13), (15, 16)
        ))

    def test_pairings_slide(self):
        self.pairings("slide", (
            (1, 4), (2, 5), (3, 6), (7, 9), (8, 10), (11, 13), (12, 14), (15, 16)
        ))


    def one_up_one_down(self, data, expected, **options):
        for option, value in options.iteritems():
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
    standings[1] = [(12, 'B', 4, [26, 11, 15, 14], 2),
                    (2, 'D', 3, [22, 16, 20, 10], 2),
                    (3, 'E', 3, [23, 20, 25, 4], 2),
                    (11, 'B', 3, [1, 12, 23, 22], 2),
                    (6, 'E', 3, [19, 15, 18, 9], 2),
                    (17, 'E', 3, [21, 14, 7, 25], 2),
                    (4, 'B', 3, [18, 25, 5, 3], 3),
                    (14, 'A', 3, [24, 17, 9, 12], 2),
                    (8, 'A', 3, [15, 24, 1, 15], 2),
                    (7, 'D', 2, [16, 9, 17, 16], 2),
                    (9, 'D', 2, [5, 7, 14, 6], 2),
                    (15, 'B', 2, [8, 6, 12, 8], 2),
                    (18, 'B', 2, [4, 21, 6, 21], 2),
                    (22, 'A', 2, [2, 10, 16, 11], 2),
                    (23, 'A', 2, [3, 19, 11, 5], 2),
                    (24, 'B', 2, [14, 8, 19, 20], 3),
                    (25, 'A', 2, [10, 4, 3, 17], 3),
                    (1, 'C', 1, [11, 26, 8, 19], 2),
                    (5, 'C', 1, [9, 13, 4, 23], 1),
                    (10, 'B', 1, [25, 22, 13, 2], 1),
                    (16, 'D', 1, [7, 2, 22, 7], 2),
                    (20, 'E', 1, [13, 3, 2, 24], 2),
                    (21, 'A', 1, [17, 18, 26, 18], 2),
                    (19, 'B', 1, [6, 23, 24, 1], 1),
                    (26, 'B', 1, [12, 1, 21, 13], 2),
                    (13, 'C', 0, [20, 5, 10, 26], 2)]

    expected = dict()
    expected[1] = [dict(odd_bracket="pullup_top", pairing_method="slide",
                        avoid_conflicts="one_up_one_down"), [
                    (12,  2, ["pullup"], True),
                    ( 3, 14, ["1u1d_hist"], True),
                    (11,  4, ["1u1d_other"], False),
                    ( 6,  7, ["1u1d_other", "pullup"], True),
                    (17,  8, ["1u1d_hist"], True),
                    ( 9, 24, ["1u1d_other"], False),
                    (15, 23, ["1u1d_inst"], True),
                    (18, 25, [], False),
                    (22,  1, ["pullup"], True),
                    ( 5, 19, ["1u1d_other"], True),
                    (10, 21, ["1u1d_inst"], False),
                    (16, 13, ["1u1d_other", "pullup"], True),
                    (20, 26, ["1u1d_hist"], True)]]
    expected[2] = [dict(odd_bracket="intermediate_avoid_conflicts",
                        pairing_method="slide", avoid_conflicts="one_up_one_down"), [
                    (12, 2, [], True),
                    (3, 17, [], True), # institution conflict, but swapping
                                       # would give history conflict
                    (11, 14, ["1u1d_inst"], True),
                    (6, 4, ["1u1d_other"], False),
                    (8, 7, [], True),
                    (9, 22, [], True),
                    (15, 23, [], True),
                    (18, 24, [], False),
                    (1, 25, [], False),
                    (5, 20, [], False),
                    (10, 21, [], False),
                    (16, 26, ["bub_up_hist"], True),
                    (19, 13, ["bub_up_accom"], False)]]

    # indices: (standings, expected)
    cases = [(1, 1), (1, 2)]

    def do_draw(self, standings, options):
        standings = [TestTeam(*args) for args in standings]
        self.ppd = DrawGenerator("power_paired", standings, **options)
        return self.ppd.make_draw()

    def test_draw(self):
        for s, e in self.cases:
            standings = self.standings[s]
            kwargs, expected = self.expected[e]
            draw = self.do_draw(standings, kwargs)
            for actual, (exp_aff, exp_neg, exp_flags, same_affs) in zip(draw, expected):
                actual_teams = (actual.aff_team.id, actual.neg_team.id)
                expected_teams = (exp_aff, exp_neg)
                if same_affs:
                    self.assertItemsEqual(actual_teams, expected_teams)
                else:
                    self.assertEqual(actual_teams, expected_teams)
                self.assertEqual(actual.flags, exp_flags)


class TestPowerPairedWithSideConstraintsDrawGeneratorPartOddBrackets(unittest.TestCase):
    """Basic unit test for core functionality of power-paired draws with side
    constraints. Not comprehensive."""

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
    brackets[99] = OrderedDict([ # Uneven aff/neg, should raise exception
        (5, {"aff": [1, 2], "neg": []}),
        (4, {"aff": [3, 4], "neg": [14]}),
        (3, {"aff": [5, 6, 7, 8, 9], "neg": [15, 16]}),
        (2, {"aff": [], "neg": [17, 18, 19, 20]}),
        (1, {"aff": [10, 11], "neg": [21, 22, 23, 24]}),
        (0, {"aff": [12, 13], "neg": []}),
    ])

    def setUp(self):
        self.ppd = DrawGenerator("power_paired", DUMMY_TEAMS, side_constraints=True)

    def tearDown(self):
        del self.ppd

    def bracket_resolve_odd(self, name, expecteds):
        self.ppd.options["odd_bracket"] = name
        for index, expected in expecteds.iteritems():
            self.b2 = copy.deepcopy(self.brackets[index])
            self.ppd.resolve_odd_brackets(self.b2)
            self.assertDictEqual(self.b2, expected)
            del self.b2

    def test_pullup_invalid(self):
        for name in ["pullup_top", "pullup_bottom", "pullup_random", "intermediate"]:
            self.b2 = copy.deepcopy(self.brackets[99])
            self.assertRaises(DrawError, self.ppd.resolve_odd_brackets, self.b2)

    def test_pullup_top(self):
        expecteds = dict()
        expecteds[1] = OrderedDict([
            (5, {"aff": [1], "neg": [14]}),
            (4, {"aff": [2, 3], "neg": [15, 16]}),
            (3, {"aff": [4, 5, 6, 7, 8], "neg": [17, 18, 19, 20, 21]}),
            (2, {"aff": [9, 10], "neg": [22, 23]}),
            (1, {"aff": [11, 12], "neg": [24, 25]}),
            (0, {"aff": [13], "neg": [26]}),
        ])
        expecteds[2] = OrderedDict([
            (5, {"aff": [1, 2], "neg": [16, 17]}),
            (4, {"aff": [3, 4, 5, 6], "neg": [18, 19, 20, 21]}),
            (3, {"aff": [7, 8], "neg": [22, 23]}),
            (2, {"aff": [9, 10], "neg": [24, 25]}),
            (1, {"aff": [11, 12, 13, 14], "neg": [26, 27, 28, 29]}),
            (0, {"aff": [15], "neg": [30]}),
        ])
        expecteds[3] = OrderedDict([
            (5, {"aff": [1, 2], "neg": [13, 14]}),
            (4, {"aff": [3, 4], "neg": [15, 16]}),
            (3, {"aff": [5, 6, 7, 8, 9], "neg": [17, 18, 19, 20, 21]}),
            (2, {"aff": [], "neg": []}),
            (1, {"aff": [10, 11, 12], "neg": [22, 23, 24]}),
            (0, {"aff": [], "neg": []}),
        ])
        self.bracket_resolve_odd("pullup_top", expecteds)

    def test_pullup_bottom(self):
        expecteds = dict()
        expecteds[1] = OrderedDict([
            (5, {"aff": [1], "neg": [14]}),
            (4, {"aff": [2, 3], "neg": [15, 18]}),
            (3, {"aff": [4, 5, 6, 7, 8], "neg": [16, 17, 19, 20, 21]}),
            (2, {"aff": [9, 10], "neg": [24, 25]}),
            (1, {"aff": [11, 12], "neg": [22, 23]}),
            (0, {"aff": [13], "neg": [26]}),
        ])
        expecteds[2] = OrderedDict([
            (5, {"aff": [3, 4], "neg": [16, 17]}),
            (4, {"aff": [1, 2, 6, 7], "neg": [18, 19, 20, 21]}),
            (3, {"aff": [5, 10], "neg": [22, 23]}),
            (2, {"aff": [8, 9], "neg": [26, 27]}),
            (1, {"aff": [11, 12, 13, 14], "neg": [24, 25, 29, 30]}),
            (0, {"aff": [15], "neg": [28]}),
        ])
        expecteds[3] = OrderedDict([
            (5, {"aff": [1, 2], "neg": [13, 16]}),
            (4, {"aff": [3, 4], "neg": [14, 15]}),
            (3, {"aff": [5, 6, 7, 8, 9], "neg": [17, 18, 19, 23, 24]}),
            (2, {"aff": [], "neg": []}),
            (1, {"aff": [10, 11, 12], "neg": [20, 21, 22]}),
            (0, {"aff": [], "neg": []}),
        ])
        self.bracket_resolve_odd("pullup_bottom", expecteds)

    def test_intermediate_brackets(self):
        expecteds = dict()
        expecteds[1] = OrderedDict([
            (5, {"aff": [1], "neg": [14]}),
            (4, {"aff": [2], "neg": [15]}),
            (3.5, {"aff": [3], "neg": [16]}),
            (3, {"aff": [4, 5], "neg": [17, 18]}),
            (2.5, {"aff": [6, 7, 8], "neg": [19, 20, 21]}),
            (2, {"aff": [], "neg": []}),
            (1.5, {"aff": [9, 10], "neg": [22, 23]}),
            (1, {"aff": [11, 12], "neg": [24, 25]}),
            (0, {"aff": [13], "neg": [26]}),
        ])
        expecteds[2] = OrderedDict([
            (5, {"aff": [], "neg": []}),
            (4.5, {"aff": [1, 2], "neg": [16, 17]}),
            (4, {"aff": [3, 4], "neg": [18, 19]}),
            (3.5, {"aff": [5, 6], "neg": [20, 21]}),
            (3, {"aff": [7], "neg": [22]}),
            (2.5, {"aff": [8], "neg": [23]}),
            (2, {"aff": [], "neg": []}),
            (1.5, {"aff": [9, 10], "neg": [24, 25]}),
            (1, {"aff": [11, 12], "neg": [26, 27]}),
            (0.5, {"aff": [13, 14], "neg": [28, 29]}),
            (0, {"aff": [15], "neg": [30]}),
        ])
        expecteds[3] = OrderedDict([
            (5, {"aff": [], "neg": []}),
            (4.5, {"aff": [1, 2], "neg": [13, 14]}),
            (4, {"aff": [], "neg": []}),
            (3.5, {"aff": [3, 4], "neg": [15, 16]}),
            (3, {"aff": [], "neg": []}),
            (2.5, {"aff": [5, 6, 7, 8, 9], "neg":[17, 18, 19, 20, 21]}),
            (2, {"aff": [], "neg": []}),
            (1, {"aff": [10, 11], "neg": [22, 23]}),
            (0.5, {"aff": [12], "neg": [24]}),
            (0, {"aff": [], "neg": []}),
        ])
        self.bracket_resolve_odd("intermediate", expecteds)

    def test_pullup_random(self):
        for j in range(10):
            # Just doing the third one because it's hardest, too lazy to write
            # random tests for the others.
            b2 = copy.deepcopy(self.brackets[3])
            self.ppd.options["odd_bracket"] = "pullup_random"
            self.ppd.resolve_odd_brackets(b2)

            self.assertEqual(b2[5]["aff"], [1, 2])
            self.assertIn(13, b2[5]["neg"])
            self.assertEqual([i in b2[5]["neg"] for i in [14, 15, 16]].count(True), 1)
            self.assertEqual(b2[4]["aff"], [3, 4])
            self.assertEqual([i in b2[4]["neg"] for i in [14, 15, 16]].count(True), 2)
            self.assertItemsEqual(b2[5]["neg"] + b2[4]["neg"], [13, 14, 15, 16])
            self.assertEqual(b2[3]["aff"], [5, 6, 7, 8, 9])
            self.assertTrue(all(i in b2[3]["neg"] for i in [17, 18, 19]))
            self.assertEqual([i in b2[3]["neg"] for i in [20, 21, 22, 23, 24]].count(True), 2)
            self.assertEqual(b2[2], {"aff": [], "neg": []})
            self.assertEqual(b2[1]["aff"], [10, 11, 12])
            self.assertEqual([i in b2[1]["neg"] for i in [20, 21, 22, 23, 24]].count(True), 3)
            self.assertEqual(b2[0], {"aff": [], "neg": []})


class TestPartialEliminationDrawGenerator(unittest.TestCase):

    teams = [(1, 'A'), (2, 'B'), (3, 'A'), (4, 'B'), (5, 'C'), (6, 'D'),
             (7, 'E'), (8, 'A'), (9, 'D'), (10, 'E'), (11, 'D'), (12, 'A')]

    def test_split(self):
        self.fed = DrawGenerator("first_elimination", DUMMY_TEAMS)
        self.assertEqual(self.fed._bypass_debate_split( 3), ( 1,  2))
        self.assertEqual(self.fed._bypass_debate_split( 5), ( 3,  2))
        self.assertEqual(self.fed._bypass_debate_split( 8), ( 8,  0))
        self.assertEqual(self.fed._bypass_debate_split(11), ( 5,  6))
        self.assertEqual(self.fed._bypass_debate_split(21), (11, 10))
        self.assertEqual(self.fed._bypass_debate_split(24), ( 8, 16))
        self.assertEqual(self.fed._bypass_debate_split(31), ( 1, 30))
        self.assertEqual(self.fed._bypass_debate_split(32), (32,  0))
        del self.fed

    def test_even_numbers(self):
        self.run_draw(2, [(1, 2)])
        self.run_draw(4, [(1, 4), (2, 3)])
        self.run_draw(8, [(1, 8), (2, 7), (3, 6), (4, 5)])

    def test_weird_numbers(self):
        self.run_draw(3, [(2, 3)], [1])
        self.run_draw(5, [(4, 5)], [1, 2, 3])
        self.run_draw(6, [(3, 6), (4, 5)], [1, 2])
        self.run_draw(12, [(5, 12), (6, 11), (7, 10), (8, 9)], [1, 2, 3, 4])

    def run_draw(self, break_size, expected, exp_bypassing=None):
        teams = [TestTeam(*args) for args in self.teams]
        self.fed = DrawGenerator("first_elimination", teams, break_size=break_size)
        pairings = self.fed.make_draw()
        self.assertEqual([(p.aff_team.id, p.neg_team.id) for p in pairings], expected)
        if exp_bypassing is not None:
            bypassing = [t.id for t in self.fed.get_bypassing_teams()]
            self.assertEqual(bypassing, exp_bypassing)

class TestEliminationDrawGenerator(unittest.TestCase):

    team_data = [(1, 'A'), (2, 'B'), (3, 'A'), (4, 'B'), (5, 'C'), (6, 'D'),
                 (7, 'E'), (8, 'A'), (9, 'D'), (10, 'E'), (11, 'D'), (12, 'A')]

    def setUp(self):
        self.teams = [TestTeam(*args) for args in self.team_data]

    def _results(self, *args):
        _t = lambda id: self.teams[id-1]
        _p = lambda ids: map(_t, ids)
        from draw import Pairing
        pairings = list()
        for i, (teams, winner) in enumerate(args):
            pairing = Pairing(_p(teams), 0, i, winner=_t(winner))
            pairings.append(pairing)
        return pairings

    def _teams(self, *args):
        _t = lambda id: self.teams[id-1]
        return map(_t, args)

    def test_no_bypass(self):
        teams = list()
        results = self._results(([1, 5], 1), ([6, 7], 7), ([3, 2], 3), ([4, 8], 8))
        self.run_draw(teams, results, [(1, 8), (7, 3)])

    def test_bypass(self):
        teams = self._teams(9, 11, 10, 12)
        results = self._results(([1, 5], 1), ([6, 7], 7), ([3, 2], 3), ([4, 8], 8))
        self.run_draw(teams, results, [(9, 8), (11, 3), (10, 7), (12, 1)])

    def test_error(self):
        teams = self._teams(9, 11, 12)
        results = self._results(([1, 5], 1), ([6, 7], 7), ([3, 2], 3), ([4, 8], 8))
        self.ed = DrawGenerator("elimination", teams, results)
        self.assertRaises(RuntimeError, self.ed.make_draw)

    def run_draw(self, teams, results, expected):
        self.ed = DrawGenerator("elimination", teams, results)
        pairings = self.ed.make_draw()
        self.assertEqual([(p.aff_team.id, p.neg_team.id) for p in pairings], expected)

if __name__ == '__main__':
    unittest.main()