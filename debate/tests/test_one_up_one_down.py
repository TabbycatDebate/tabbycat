import os.path, sys
if os.path.abspath("..") not in sys.path: sys.path.append(os.path.abspath(".."))
import unittest
from one_up_one_down import OneUpOneDownSwapper

class TestTeam(object):
    def __init__(self, id, inst, hist):
        self.id = id
        self.institution = inst
        self.hist = hist

    def __repr__(self):
        return "<Team {0} of {1} ({2:#x})>".format(self.id, self.institution,
            hash(self))

    def seen(self, other):
        return self.hist.count(other.id)

class TestOneUpOneDown(unittest.TestCase):

    @staticmethod
    def _1u1d_no_change(data):
        return [(id1, id2) for ((id1, inst1, hist1), (id2, inst2, hist2))
                in data]

    def testNoSwap(self):
        data = (((1, 'A', ()), (5, 'B', ())),
                ((2, 'C', ()), (6, 'A', ())),
                ((3, 'B', ()), (7, 'D', ())),
                ((4, 'C', ()), (8, 'A', ())))
        result = self._1u1d_no_change(data)
        self.assertEqual(result, self.draw(data))
        return self.draw(data)

    def testSwapInst(self):
        data = (((1, 'A', ()), (5, 'A', ())),
                ((2, 'C', ()), (6, 'B', ())),
                ((3, 'B', ()), (7, 'D', ())),
                ((4, 'C', ()), (8, 'A', ())))
        result = [(1, 6), (2, 5), (3, 7), (4, 8)]
        self.assertEqual(result, self.draw(data))
        return self.draw(data)

    def testNoSwapInst(self):
        data = (((1, 'A', ()), (5, 'A', ())),
                ((2, 'C', ()), (6, 'B', ())),
                ((3, 'B', ()), (7, 'D', ())),
                ((4, 'C', ()), (8, 'A', ())))
        result = self._1u1d_no_change(data)
        self.assertEqual(result, self.draw(data, avoid_institution=False))
        return self.draw(data)

    def testSwapHist(self):
        data = (((1, 'A', (5,)), (5, 'B', ())),
                ((2, 'C', ()), (6, 'A', ())),
                ((3, 'B', ()), (7, 'D', ())),
                ((4, 'C', ()), (8, 'A', ())))
        result = [(1, 6), (2, 5), (3, 7), (4, 8)]
        self.assertEqual(result, self.draw(data))
        return self.draw(data)

    def testNoSwapHist(self):
        data = (((1, 'A', (5,)), (5, 'B', ())),
                ((2, 'C', ()), (6, 'A', ())),
                ((3, 'B', ()), (7, 'D', ())),
                ((4, 'C', ()), (8, 'A', ())))
        result = self._1u1d_no_change(data)
        self.assertEqual(result, self.draw(data, avoid_history=False))
        return self.draw(data)

    def testLastSwap(self):
        data = (((1, 'A', ()), (5, 'B', ())),
                ((2, 'C', ()), (6, 'A', ())),
                ((3, 'B', ()), (7, 'D', ())),
                ((4, 'C', (8,)), (8, 'A', ())))
        result = [(1, 5), (2, 6), (3, 8), (4, 7)]
        self.assertEqual(result, self.draw(data))
        return self.draw(data)

    def draw(self, data, **options):
        d = []
        for ((p1, in1, hist1), (p2, in2, hist2)) in data:
            d.append((TestTeam(p1, in1, hist1), TestTeam(p2, in2, hist2)))
        r = OneUpOneDownSwapper(**options).run(d)
        return [(a.id, b.id) for (a, b) in r]

if __name__ == '__main__':
    unittest.main()