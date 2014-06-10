import unittest
from collections import OrderedDict
import draw
import copy

class TestDraw(unittest.TestCase):

    brackets = OrderedDict([
        (4, [1, 2, 3, 4, 5]),
        (3, [6, 7, 8, 9]),
        (2, [10, 11, 12, 13, 14]),
        (1, [15, 16])
    ])

    def test_pullup_top(self):
        self.bracket(self.brackets, "pullup_top", OrderedDict([
            (4, [1, 2, 3, 4, 5, 6]),
            (3, [7, 8, 9, 10]),
            (2, [11, 12, 13, 14]),
            (1, [15, 16])
        ]))

    def test_pullup_bottom(self):
        self.bracket(self.brackets, "pullup_bottom", OrderedDict([
            (4, [1, 2, 3, 4, 5, 9]),
            (3, [6, 7, 8, 14]),
            (2, [10, 11, 12, 13]),
            (1, [15, 16])
        ]))

    def test_pullup_intermediate(self):
        self.bracket(self.brackets, "intermediate", OrderedDict([
            (4, [1, 2, 3, 4]),
            (3.5, [5, 6]),
            (3, [7, 8]),
            (2.5, [9, 10]),
            (2, [11, 12, 13, 14]),
            (1, [15, 16])
        ]))

    @unittest.skip("Haven't figure out how to test random yet")
    def test_pullup_random(self):
        b2 = copy.deepcopy(self.brackets)
        ppd.options["odd_bracket"] = "pullup_random"
        ppd.resolve_odd_brackets(b2)
        self.assertIn([1, 2, 3, 4, 5], b2[4])
        self.assertIn([1, 2, 3, 4], b2[3])
        self.assertIn([1, 2, 3, 4], b2[2])
        self.assertIn([1, 2, 3, 4], b2[1])

    def bracket(self, brackets, name, result):
        b2 = copy.deepcopy(brackets)
        ppd = draw.PowerPairedDraw(None)
        ppd.options["odd_bracket"] = name
        ppd.resolve_odd_brackets(b2)
        self.assertEqual(b2, result)
        return b2

    def test_pairings_fold(self):
        self.pairings(self.brackets, "fold", (
            (1, 6), (2, 5), (3, 4), (7, 10), (8, 9), (11, 14), (12, 13), (15, 16)
        ))

    def test_pairings_slide(self):
        self.pairings(self.brackets, "slide", (
            (1, 4), (2, 5), (3, 6), (7, 9), (8, 10), (11, 13), (12, 14), (15, 16)
        ))

    def pairings(self, brackets, name, result):
        b2 = copy.deepcopy(brackets)
        ppd = draw.PowerPairedDraw(None)
        ppd.options["odd_bracket"] = "pullup_top"
        ppd.options["pairing_method"] = name
        ppd.resolve_odd_brackets(b2)
        pairings = ppd.generate_pairings(b2)
        self.assertEqual(tuple(p.teams for p in pairings), result)


if __name__ == '__main__':
    unittest.main()