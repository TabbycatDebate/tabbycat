import unittest

from ..utils import opposite_side


class TestOppositeSide(unittest.TestCase):
    """Tests the opposite_side function."""

    def test_two_team_aff_to_neg(self):
        """Test that opposite_side(0, 2) returns 1 (AFF -> NEG)."""
        self.assertEqual(opposite_side(0, 2), 1)

    def test_two_team_neg_to_aff(self):
        """Test that opposite_side(1, 2) returns 0 (NEG -> AFF)."""
        self.assertEqual(opposite_side(1, 2), 0)

    def test_bp_og_to_co(self):
        """Test that opposite_side(0, 4) returns 3 (OG -> CO)."""
        self.assertEqual(opposite_side(0, 4), 3)

    def test_bp_co_to_og(self):
        """Test that opposite_side(3, 4) returns 0 (CO -> OG)."""
        self.assertEqual(opposite_side(3, 4), 0)

    def test_bp_oo_to_cg(self):
        """Test that opposite_side(1, 4) returns 2 (OO -> CG)."""
        self.assertEqual(opposite_side(1, 4), 2)

    def test_bp_cg_to_oo(self):
        """Test that opposite_side(2, 4) returns 1 (CG -> OO)."""
        self.assertEqual(opposite_side(2, 4), 1)

    def test_involution_two_team(self):
        """Test that applying opposite_side twice returns the original side for 2-team format."""
        for side in range(2):
            with self.subTest(side=side):
                result = opposite_side(opposite_side(side, 2), 2)
                self.assertEqual(result, side)

    def test_involution_bp(self):
        """Test that applying opposite_side twice returns the original side for BP (4-team) format."""
        for side in range(4):
            with self.subTest(side=side):
                result = opposite_side(opposite_side(side, 4), 4)
                self.assertEqual(result, side)
