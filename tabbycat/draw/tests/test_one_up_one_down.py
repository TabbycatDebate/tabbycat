import unittest

from .utils import TestTeam
from ..generator.one_up_one_down import OneUpOneDownSwapper


class TestOneUpOneDown(unittest.TestCase):

    @staticmethod
    def _1u1d_no_change(data):
        return [(t1[0], t2[0]) for t1, t2 in data]

    def test_no_swap(self):
        data = (((1, 'A'), (5, 'B')),
                ((2, 'C'), (6, 'A')),
                ((3, 'B'), (7, 'D')),
                ((4, 'C'), (8, 'A')))
        result = self._1u1d_no_change(data)
        self.assertEqual(result, self.draw(data))
        return self.draw(data)

    def test_swap_inst(self):
        data = (((1, 'A'), (5, 'A')),
                ((2, 'C'), (6, 'B')),
                ((3, 'B'), (7, 'D')),
                ((4, 'C'), (8, 'A')))
        result = [(1, 6), (2, 5), (3, 7), (4, 8)]
        self.assertEqual(result, self.draw(data))
        return self.draw(data)

    def test_swap_inst_none(self):
        data = (((1, None), (5, None)),
                ((2, 'C'), (6, 'B')),
                ((3, 'B'), (7, 'D')),
                ((4, 'C'), (8, 'A')))
        result = [(1, 5), (2, 6), (3, 7), (4, 8)]
        self.assertEqual(result, self.draw(data))
        return self.draw(data)

    def test_no_swap_inst(self):
        data = (((1, 'A'), (5, 'A')),
                ((2, 'C'), (6, 'B')),
                ((3, 'B'), (7, 'D')),
                ((4, 'C'), (8, 'A')))
        result = self._1u1d_no_change(data)
        self.assertEqual(result, self.draw(data, avoid_institution=False))
        return self.draw(data)

    def test_swap_hist(self):
        data = (((1, 'A', None, 5), (5, 'B')),
                ((2, 'C'), (6, 'A')),
                ((3, 'B'), (7, 'D')),
                ((4, 'C'), (8, 'A')))
        result = [(1, 6), (2, 5), (3, 7), (4, 8)]
        self.assertEqual(result, self.draw(data))
        return self.draw(data)

    def test_no_swap_hist(self):
        data = (((1, 'A', None, 5), (5, 'B')),
                ((2, 'C'), (6, 'A')),
                ((3, 'B'), (7, 'D')),
                ((4, 'C'), (8, 'A')))
        result = self._1u1d_no_change(data)
        self.assertEqual(result, self.draw(data, avoid_history=False))
        return self.draw(data)

    def test_last_swap(self):
        data = (((1, 'A'), (5, 'B')),
                ((2, 'C'), (6, 'A')),
                ((3, 'B'), (7, 'D')),
                ((4, 'C', None, 8), (8, 'A')))
        result = [(1, 5), (2, 6), (3, 8), (4, 7)]
        self.assertEqual(result, self.draw(data))
        return self.draw(data)

    def test_exhaust_institution_1(self):
        data = (((1, 'C'), (5, 'A')),
                ((2, 'A'), (6, 'A')),
                ((3, 'C'), (7, 'A')),
                ((4, 'B'), (8, 'D')))
        result = self._1u1d_no_change(data)
        self.assertEqual(result, self.draw(data))
        return self.draw(data)

    def test_exhaust_institution_2(self):
        data = (((1, 'A'), (5, 'C')),
                ((2, 'A'), (6, 'A')),
                ((3, 'A'), (7, 'D')),
                ((4, 'B'), (8, 'D')))
        result = self._1u1d_no_change(data)
        self.assertEqual(result, self.draw(data))
        return self.draw(data)

    def test_exhaust_institution_3(self):
        data = (((1, 'A'), (5, 'C')),
                ((2, 'A'), (6, 'A')),
                ((3, 'B'), (7, 'A')),
                ((4, 'B'), (8, 'D')))
        result = self._1u1d_no_change(data)
        self.assertEqual(result, self.draw(data))
        return self.draw(data)

    def test_exhaust_history_1(self):
        data = (((1, 'C'), (5, 'B')),
                ((2, 'A', None, (5, 6, 7)), (6, 'C')),
                ((3, 'C'), (7, 'D')),
                ((4, 'B'), (8, 'D')))
        result = self._1u1d_no_change(data)
        self.assertEqual(result, self.draw(data))
        return self.draw(data)

    def test_exhaust_history_2(self):
        data = (((1, 'C'), (5, 'B')),
                ((2, 'A', None, (5, 6)), (6, 'C')),
                ((3, 'C', None, 6), (7, 'D')),
                ((4, 'B'), (8, 'D')))
        result = self._1u1d_no_change(data)
        self.assertEqual(result, self.draw(data))
        return self.draw(data)

    def test_prefer_institution_to_history(self):
        data = (((1, 'C'), (5, 'B')),
                ((2, 'A', None, (5, 7)), (6, 'A')),
                ((3, 'C'), (7, 'D')),
                ((4, 'B'), (8, 'D')))
        result = self._1u1d_no_change(data)
        self.assertEqual(result, self.draw(data))
        return self.draw(data)

    def test_prefer_fewer_swaps(self):
        # It should swap the middle two debates, as opposed to the top two and
        # last two.
        data = (((1, 'C'), (5, 'B')),
                ((2, 'A'), (6, 'A')),
                ((3, 'C'), (7, 'C')),
                ((4, 'B'), (8, 'D')))
        result = [(1, 5), (2, 7), (3, 6), (4, 8)]
        self.assertEqual(result, self.draw(data))
        return self.draw(data)

    def draw(self, data, **options):
        d = []
        for data1, data2 in data:
            d.append((TestTeam(*data1), TestTeam(*data2)))
        r = OneUpOneDownSwapper(**options).run(d)
        return [(a.id, b.id) for (a, b) in r]


if __name__ == '__main__':
    unittest.main()
