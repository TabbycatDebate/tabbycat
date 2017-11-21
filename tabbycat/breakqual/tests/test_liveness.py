from django.test import TestCase

from ..utils import calculate_bp, calculate_2vs2


class TestFeedbackProgress(TestCase):
    """ Params are:
    is_general, current round, break size, elgibile teams, total_rounds, scores
    """

    # 2vs2
    def test_case_australs_2017_open(self):
        safe, dead = calculate_2vs2(True, 8, 16, 79, 8, None)
        self.assertEqual(safe, 6) # All on 6 broke
        self.assertEqual(dead, 3) # Some on 5 broke

    def test_case_australs_2017_esl(self):
        # Note 2 teams bypassed ESL break; 8 eligible
        safe, dead = calculate_2vs2(False, 8, 4, 8, 8, [5,4,3,3,1,1])
        self.assertEqual(safe, 3) # All on 4 broke
        self.assertEqual(dead, 1) # Some (all?) on 3 broke

    def test_case_easters_2017_open(self):
        safe, dead = calculate_2vs2(True, 6, 16, 100, 6, None)
        self.assertEqual(safe, 5) # All on 5 broke
        self.assertEqual(dead, 2) # Some on 4 broke

    def test_case_australs_2016_open(self):
        safe, dead = calculate_2vs2(True, 8, 16, 74, 8, None)
        self.assertEqual(safe, 6)
        self.assertEqual(dead, 3)

    def test_case_australs_2016_esl(self):
        # Note 2 teams bypassed ESL break
        break_cat_scores = [6,5,3,3,3,1] # Worst case (-1 on finishing scores)
        safe, dead = calculate_2vs2(False, 8, 4, 8, 8, break_cat_scores)
        self.assertEqual(safe, 5)
        self.assertEqual(dead, 1)

    def test_case_australs_2015_open(self):
        safe, dead = calculate_2vs2(True, 8, 16, 78, 8, None)
        self.assertEqual(safe, 6)
        self.assertEqual(dead, 3)

    # BP
    def test_case_abp_2017_open(self):
        safe, dead = calculate_bp(True, 6, 24, 100, 6, None)
        self.assertEqual(safe, 12) # All teams on 12 broke
        self.assertEqual(dead, 7) # Some teams on 11 broke

    def test_case_awdc_2017_open(self):
        safe, dead = calculate_bp(True, 6, 16, 68, 6, None)
        self.assertEqual(safe, 12) # All teams on 12 broke
        self.assertEqual(dead, 7) # Some teams on 11 broke

    def test_case_yale_2017_open(self):
        safe, dead = calculate_bp(True, 6, 16, 172, 6, None)
        self.assertEqual(safe, 14) # All teams on 14 broke
        self.assertEqual(dead, 9) # Some teams on 13 broke

    def test_case_wudc_2017_open(self):
        safe, dead = calculate_bp(True, 9, 48, 378, 9, None)
        self.assertEqual(safe, 18) # All teams on 18 broke
        self.assertEqual(dead, 13) # Some teams on 17 broke

    def test_case_wudc_2016_open(self):
        safe, dead = calculate_bp(True, 9, 48, 386, 9, None)
        self.assertEqual(safe, 18) # All teams on 18 broke
        self.assertEqual(dead, 13) # Some teams on 17 broke

    # def test_case_abp_2017_efl(self):
    #     safe, dead = calculate_bp(False, 6, 8, 21, 6, [10,9,9,8,7,7,7,6,6])
    #     self.assertEqual(safe, 8) # All teams on 8 broke
    #     self.assertEqual(dead, 3) # Some teams on 7 broke

    # def test_case_wudc_2017_esl(self):
    #     safe, dead = calculate_bp(True, 9, 16, 131, 9, None)
    #     self.assertEqual(safe, 16) # All teams on 16 broke
    #     self.assertEqual(dead, 12) # No teams on 15 broke

    # def test_case_wudc_2017_efl(self):
    #     safe, dead = calculate_bp(True, 9, 8, 58, 9, None)
    #     self.assertEqual(safe, 15) # All teams on 15 broke
    #     self.assertEqual(dead, 10) # No teams on 13 broke

    # def test_case_wudc_2016_esl(self):
    #     safe, dead = calculate_bp(True, 9, 16, 164, 9, None)
    #     self.assertEqual(safe, 16) # All teams on  broke
    #     self.assertEqual(dead, 11) # No teams on 14 broke

    # def test_case_wudc_2016_efl(self):
    #     safe, dead = calculate_bp(True, 9, 8, 65, 9, None)
    #     self.assertEqual(safe, 15) # All teams on 15 broke
    #     self.assertEqual(dead, 10) # No teams on 13 broke
