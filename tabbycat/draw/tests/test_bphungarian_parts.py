import unittest

from .utils import TestTeam
from ..generator.bphungarian import BPHungarianDrawGenerator

DUMMY_TEAMS = [TestTeam(1, 'A', side_history=[0, 0, 0, 0]),
               TestTeam(2, 'B', side_history=[0, 0, 0, 0]),
               TestTeam(3, 'C', side_history=[0, 0, 0, 0]),
               TestTeam(4, 'D', side_history=[0, 0, 0, 0])]


class TestDefineRooms(unittest.TestCase):
    """Tests the `_define_rooms_*` functions of BPHungarianDrawGenerator."""

    testdata = dict()
    anywhere = dict()
    one_room = dict()
    testdata[1] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    anywhere[1] = [(11, {8, 9, 10, 11}), (7, {4, 5, 6, 7}), (3, {0, 1, 2, 3})]
    one_room[1] = [(11, {8, 9, 10, 11}), (7, {4, 5, 6, 7}), (3, {0, 1, 2, 3})]
    testdata[2] = [3, 3, 2, 2, 2, 2, 1, 1, 1, 1, 0, 0]
    anywhere[2] = [(3, {3, 2}), (2, {2, 1}), (1, {1, 0})]
    one_room[2] = [(3, {3, 2}), (2, {2, 1}), (1, {1, 0})]
    testdata[3] = [4, 4, 4, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 0]
    anywhere[3] = [(4, {4, 3}), (3, {3}), (2, {2, 1}), (2, {2, 1}), (2, {2, 1}), (1, {1, 0})]
    one_room[3] = [(4, {4, 3}), (3, {3}), (2, {2}), (2, {2}), (2, {2, 1}), (1, {1, 0})]
    testdata[4] = [4, 3, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0]
    anywhere[4] = [(4, {4, 3, 2}), (2, {2}), (0, {0})]
    one_room[4] = [(4, {4, 3, 2}), (2, {2}), (0, {0})]
    testdata[5] = [7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 6, 6, 6, 6, 6]
    anywhere[5] = [(7, {7, 6}), (7, {7, 6}), (7, {7, 6}), (6, {6})]
    one_room[5] = [(7, {7}), (7, {7}), (7, {7, 6}), (6, {6})]

    def _test_define_rooms(self, method, expected):
        generator = BPHungarianDrawGenerator(DUMMY_TEAMS, pullup=method)
        for key in self.testdata.keys():
            with self.subTest(case=key):
                result = generator.define_rooms(self.testdata[key])
                for (al, ab), (el, eb) in zip(result, expected[key]):
                    self.assertEqual(al, el)
                    self.assertCountEqual(ab, eb)

    def test_pullup_anywhere(self):
        self._test_define_rooms("anywhere", self.anywhere)

    def test_pullup_one_room(self):
        self._test_define_rooms("one_room", self.one_room)
