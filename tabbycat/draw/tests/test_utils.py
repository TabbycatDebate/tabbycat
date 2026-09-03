import unittest

from ..utils import opposite_side


class TestOppositeSide(unittest.TestCase):
    """Tests the opposite_side function."""

    def test_opposite_side(self):
        cases = (
            (0, 2, 1),
            (1, 2, 0),
            (0, 4, 3),
            (1, 4, 2),
            (2, 4, 1),
            (3, 4, 0),
        )
        for side, teams_in_debate, expected in cases:
            with self.subTest(side=side, teams_in_debate=teams_in_debate):
                self.assertEqual(opposite_side(side, teams_in_debate), expected)

    def test_involution(self):
        for teams_in_debate in (2, 4):
            for side in range(teams_in_debate):
                with self.subTest(side=side, teams_in_debate=teams_in_debate):
                    result = opposite_side(opposite_side(side, teams_in_debate), teams_in_debate)
                    self.assertEqual(result, side)
