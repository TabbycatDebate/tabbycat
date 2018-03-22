from unittest import TestCase

from .liveness import liveness_twoteam, liveness_bp


class TestLiveness(TestCase):
    """ Params are:
    is_general, current round, break size, total_teams, total_rounds, scores
    """

    # 2vs2
    def test_case_australs_2017_open_penultimate(self):
        safe, dead = liveness_twoteam(True, 7, 16, 79, 8, None)
        self.assertGreaterEqual(safe, 6) # All on 6 broke
        self.assertLessEqual(dead, 2) # Some on 5 broke

    def test_case_australs_2017_open(self):
        safe, dead = liveness_twoteam(True, 8, 16, 79, 8, None)
        self.assertGreaterEqual(safe, 6) # All on 6 broke
        self.assertLessEqual(dead, 3) # Some on 5 broke

    def test_case_australs_2017_esl_penultimate(self):
        # Note 2 teams bypassed ESL break; 8 eligible
        safe, dead = liveness_twoteam(False, 7, 4, 79, 8, [5,4,3,3,1,1])
        self.assertGreaterEqual(safe, 4) # All on 4 broke
        self.assertLessEqual(dead, 0) # Some (all?) on 3 broke

    def test_case_australs_2017_esl(self):
        # Note 2 teams bypassed ESL break; 8 eligible
        safe, dead = liveness_twoteam(False, 8, 4, 79, 8, [5,4,3,3,1,1])
        self.assertGreaterEqual(safe, 3) # All on 4 broke
        self.assertLessEqual(dead, 1) # Some (all?) on 3 broke

    def test_case_easters_2017_open_penultimate(self):
        safe, dead = liveness_twoteam(True, 6, 16, 100, 6, None)
        self.assertGreaterEqual(safe, 5) # All on 5 broke
        self.assertLessEqual(dead, 2) # Some on 4 broke

    def test_case_easters_2017_open(self):
        safe, dead = liveness_twoteam(True, 6, 16, 100, 6, None)
        self.assertGreaterEqual(safe, 5) # All on 5 broke
        self.assertLessEqual(dead, 2) # Some on 4 broke

    def test_case_australs_2016_open(self):
        safe, dead = liveness_twoteam(True, 8, 16, 74, 8, None)
        self.assertGreaterEqual(safe, 6)
        self.assertLessEqual(dead, 3)

    def test_case_australs_2016_esl(self):
        # Note 2 teams bypassed ESL break
        # Worst case (-1 on finishing scores)
        safe, dead = liveness_twoteam(False, 8, 4, 74, 8, [6,5,3,3,3,1])
        self.assertGreaterEqual(safe, 5)
        self.assertLessEqual(dead, 1)

    def test_case_australs_2015_open(self):
        safe, dead = liveness_twoteam(True, 8, 16, 78, 8, None)
        self.assertGreaterEqual(safe, 6)
        self.assertLessEqual(dead, 3)

    # BP
    def test_case_abp_2017_open_penultimate(self):
        safe, dead = liveness_bp(True, 5, 24, 100, 6, None)
        self.assertGreaterEqual(safe, 12) # All teams on 12 broke
        self.assertLessEqual(dead, 4) # Some teams on 11 broke

    def test_case_abp_2017_open(self):
        safe, dead = liveness_bp(True, 6, 24, 100, 6, None)
        self.assertGreaterEqual(safe, 12) # All teams on 12 broke
        self.assertLessEqual(dead, 7) # Some teams on 11 broke

    def test_case_awdc_2017_open_penultimate(self):
        safe, dead = liveness_bp(True, 5, 16, 68, 6, None)
        self.assertGreaterEqual(safe, 12) # All teams on 12 broke
        self.assertLessEqual(dead, 4) # Some teams on 11 broke

    def test_case_awdc_2017_open(self):
        safe, dead = liveness_bp(True, 6, 16, 68, 6, None)
        self.assertGreaterEqual(safe, 12) # All teams on 12 broke
        self.assertLessEqual(dead, 7) # Some teams on 11 broke

    def test_case_yale_2017_open(self):
        safe, dead = liveness_bp(True, 6, 16, 172, 6, None)
        self.assertGreaterEqual(safe, 14) # All teams on 14 broke
        self.assertLessEqual(dead, 9) # Some teams on 13 broke

    def test_case_melbourne_mini_2017_penultimate(self):
        safe, dead = liveness_bp(True, 5, 8, 20, 6, None)
        self.assertGreaterEqual(safe, 11) # All teams on 13 will break (worst case)
        self.assertLessEqual(dead, 3) # Some teams on 10 will break (best case)

    def test_case_melbourne_mini_2017(self):
        safe, dead = liveness_bp(True, 6, 8, 20, 6, None)
        self.assertGreaterEqual(safe, 11) # All teams on 13 will break (worst case)
        self.assertLessEqual(dead, 6) # Some teams on 10 will break (best case)

    def test_case_usu_iv_2016_penultimate(self):
        safe, dead = liveness_bp(True, 4, 8, 30, 5, None)
        self.assertGreaterEqual(safe, 10) # All teams on 11 will break (worst case)
        self.assertLessEqual(dead, 2) # Some teams on 9 will break (best case)

    def test_case_usu_iv_2016(self):
        safe, dead = liveness_bp(True, 5, 8, 30, 5, None)
        self.assertGreaterEqual(safe, 10) # All teams on 11 will break (worst case)
        self.assertLessEqual(dead, 5) # Some teams on 9 will break (best case)

    def test_case_abp_2017_efl(self):
        safe, dead = liveness_bp(False, 6, 8, 21, 6, [10,9,9,8,7,7,7,6,6])
        self.assertGreaterEqual(safe, 8) # All teams on 8 broke
        self.assertLessEqual(dead, 3) # Some teams on 7 broke

    # WUDC

    def test_wudc_2016_open_round_9(self):
        safe, dead = liveness_bp(True, 9, 48, 382, 9, None)
        self.assertGreaterEqual(safe, 18)
        self.assertLessEqual(dead, 13)

    def test_wudc_2016_open_round_8(self):
        safe, dead = liveness_bp(True, 8, 48, 382, 9, None)
        self.assertGreaterEqual(safe, 18)
        self.assertLessEqual(dead, 10)

    def test_wudc_2016_open_round_7(self):
        safe, dead = liveness_bp(True, 7, 48, 382, 9, None)
        self.assertGreaterEqual(safe, 18)
        self.assertLessEqual(dead, 7)

    def test_wudc_2016_open_round_6(self):
        safe, dead = liveness_bp(True, 6, 48, 382, 9, None)
        self.assertGreaterEqual(safe, 18)
        self.assertLessEqual(dead, 4)

    def test_wudc_2016_open_round_5(self):
        safe, dead = liveness_bp(True, 5, 48, 382, 9, None)
        self.assertGreaterEqual(safe, 18)
        self.assertLessEqual(dead, 1)

    def test_wudc_2016_open_round_4(self):
        safe, dead = liveness_bp(True, 4, 48, 382, 9, None)
        self.assertGreaterEqual(safe, 18)
        self.assertLessEqual(dead, -2)

    def test_wudc_2016_esl_round_9(self):
        safe, dead = liveness_bp(False, 9, 16, 382, 9, [16, 16, 16, 15, 15, 15, 15, 16, 15, 16, 15, 13, 13, 14, 14, 12, 14, 13, 13, 12, 13, 12, 12, 12, 12, 14, 12, 12, 11, 13, 12, 12, 13, 11, 12, 11, 11, 11, 11, 11, 13, 11, 13, 11, 12, 12, 12, 13, 12, 13, 12, 10, 13, 11, 10, 12, 10, 11, 12, 13, 10, 10, 10, 11, 12, 12, 11, 12, 9, 11, 11, 10, 9, 12, 10, 12, 9, 10, 10, 9, 11, 11, 9, 10, 11, 10, 10, 10, 9, 12, 10, 11, 10, 10, 11, 11, 11, 10, 10, 11, 8, 8, 9, 11, 8, 10, 10, 8, 9, 8, 9, 9, 9, 10, 9, 8, 10, 10, 7, 9, 10, 8, 10, 10, 9, 10, 10, 8, 10, 7, 7, 9, 8, 9, 9, 9, 9, 8, 8, 9, 8, 7, 8, 7, 9, 9, 6, 7, 6, 8, 9, 6, 6, 7, 5, 8, 7, 7, 6, 7, 6, 7, 6, 6, 0, 0]) # noqa: E501
        self.assertGreaterEqual(safe, 16)
        self.assertLessEqual(dead, 11)

    def test_wudc_2016_esl_round_8(self):
        safe, dead = liveness_bp(False, 8, 16, 382, 9, [13, 15, 14, 13, 13, 13, 15, 14, 12, 13, 13, 10, 10, 14, 14, 11, 13, 11, 13, 11, 12, 11, 11, 10, 12, 12, 12, 11, 11, 11, 11, 10, 10, 9, 11, 9, 8, 8, 10, 10, 12, 8, 11, 8, 10, 11, 10, 10, 12, 13, 12, 10, 12, 9, 7, 9, 10, 10, 9, 10, 9, 8, 9, 10, 11, 10, 11, 12, 8, 10, 9, 10, 9, 10, 10, 9, 9, 8, 9, 9, 11, 9, 9, 8, 11, 9, 10, 8, 8, 9, 7, 8, 10, 10, 9, 10, 10, 10, 7, 9, 7, 8, 7, 10, 7, 9, 9, 8, 6, 8, 8, 6, 7, 10, 7, 8, 9, 7, 7, 9, 10, 6, 9, 7, 7, 8, 7, 8, 8, 6, 5, 8, 8, 7, 9, 9, 8, 8, 7, 9, 6, 6, 7, 7, 6, 8, 3, 7, 6, 5, 6, 6, 6, 7, 5, 7, 6, 6, 4, 4, 6, 5, 5, 5, 0, 0]) # noqa: E501
        self.assertGreaterEqual(safe, 16)
        self.assertLessEqual(dead, 8)

    def test_wudc_2016_esl_round_7(self):
        safe, dead = liveness_bp(False, 7, 16, 382, 9, [11, 12, 13, 11, 10, 10, 14, 12, 9, 13, 12, 8, 7, 12, 11, 9, 11, 10, 11, 9, 9, 9, 8, 7, 11, 11, 10, 9, 9, 10, 9, 8, 8, 9, 9, 9, 7, 6, 8, 9, 9, 7, 10, 7, 9, 10, 9, 7, 12, 10, 9, 8, 10, 7, 6, 6, 8, 10, 8, 7, 8, 5, 8, 7, 10, 9, 8, 10, 7, 10, 8, 10, 9, 9, 10, 6, 9, 8, 7, 6, 9, 8, 8, 8, 8, 7, 8, 8, 8, 6, 7, 8, 8, 9, 9, 10, 9, 8, 7, 9, 7, 8, 7, 7, 6, 7, 7, 8, 6, 7, 6, 5, 4, 7, 6, 7, 9, 7, 4, 8, 10, 6, 8, 4, 5, 5, 6, 5, 6, 4, 5, 7, 8, 7, 7, 6, 8, 5, 7, 9, 6, 6, 6, 7, 3, 6, 3, 6, 5, 5, 5, 5, 6, 5, 5, 5, 6, 5, 4, 3, 5, 4, 5, 2, 0, 0]) # noqa: E501
        self.assertGreaterEqual(safe, 16)
        self.assertLessEqual(dead, 5)

    def test_wudc_2016_esl_round_6(self):
        safe, dead = liveness_bp(False, 6, 16, 382, 9, [9, 9, 10, 9, 8, 8, 11, 11, 6, 10, 12, 8, 5, 10, 9, 9, 8, 8, 9, 7, 7, 8, 7, 7, 9, 11, 7, 6, 8, 7, 8, 7, 6, 7, 7, 9, 6, 6, 5, 9, 9, 7, 9, 6, 8, 8, 7, 7, 9, 7, 8, 8, 8, 7, 6, 5, 5, 8, 7, 7, 6, 5, 6, 4, 9, 9, 6, 8, 7, 10, 7, 8, 9, 8, 7, 5, 8, 7, 6, 6, 7, 8, 5, 8, 6, 5, 7, 5, 6, 3, 4, 5, 7, 8, 7, 7, 6, 6, 7, 8, 5, 8, 7, 6, 5, 5, 5, 8, 6, 5, 3, 5, 2, 4, 5, 7, 6, 6, 4, 8, 7, 5, 6, 3, 4, 4, 4, 5, 6, 4, 2, 7, 7, 7, 7, 6, 6, 4, 5, 7, 5, 6, 6, 4, 3, 4, 3, 3, 4, 3, 3, 5, 3, 5, 4, 4, 4, 2, 4, 2, 3, 4, 5, 1, 0, 0]) # noqa: E501
        self.assertGreaterEqual(safe, 16)
        self.assertLessEqual(dead, 2)

    def test_wudc_2016_esl_round_5(self):
        safe, dead = liveness_bp(False, 5, 16, 382, 9, [6, 8, 7, 7, 8, 5, 9, 8, 5, 7, 9, 6, 5, 8, 6, 6, 6, 5, 6, 5, 6, 7, 4, 7, 7, 8, 6, 5, 8, 6, 6, 5, 3, 7, 4, 6, 4, 5, 4, 8, 6, 5, 8, 5, 6, 6, 4, 5, 7, 7, 7, 5, 6, 6, 4, 5, 5, 6, 4, 6, 3, 5, 6, 2, 6, 8, 5, 5, 6, 7, 5, 8, 6, 8, 7, 4, 6, 4, 5, 5, 4, 5, 3, 5, 4, 5, 5, 3, 5, 3, 2, 4, 7, 6, 6, 7, 6, 6, 4, 5, 3, 5, 5, 4, 4, 2, 3, 7, 4, 4, 2, 3, 0, 4, 3, 4, 5, 6, 4, 6, 6, 2, 3, 3, 3, 3, 4, 4, 5, 3, 2, 5, 5, 5, 4, 3, 6, 4, 4, 5, 5, 4, 6, 3, 2, 3, 1, 3, 2, 2, 2, 2, 3, 3, 4, 1, 1, 2, 3, 1, 3, 2, 4, 1, 0, 0]) # noqa: E501
        self.assertGreaterEqual(safe, 16)
        self.assertLessEqual(dead, -1)

    def test_wudc_2016_esl_round_4(self):
        safe, dead = liveness_bp(False, 4, 16, 382, 9, [6, 5, 6, 5, 6, 5, 8, 7, 5, 6, 7, 3, 3, 5, 4, 6, 5, 2, 4, 5, 6, 5, 2, 4, 7, 6, 6, 3, 5, 4, 6, 3, 3, 4, 3, 5, 3, 5, 3, 5, 5, 4, 5, 4, 5, 5, 4, 5, 5, 5, 4, 3, 5, 6, 4, 5, 4, 3, 3, 5, 3, 5, 4, 2, 6, 5, 5, 3, 5, 5, 5, 6, 4, 5, 4, 4, 4, 2, 2, 5, 4, 3, 3, 4, 3, 3, 4, 3, 5, 1, 2, 3, 6, 3, 6, 5, 3, 4, 2, 4, 3, 4, 3, 2, 3, 1, 3, 4, 2, 2, 2, 3, 0, 4, 3, 3, 4, 4, 3, 5, 5, 2, 2, 2, 3, 3, 3, 1, 2, 2, 1, 3, 2, 3, 3, 3, 3, 4, 4, 2, 4, 1, 6, 1, 1, 0, 1, 2, 2, 0, 2, 2, 3, 3, 2, 1, 1, 2, 3, 1, 1, 1, 1, 0, 0, 0]) # noqa: E501
        self.assertGreaterEqual(safe, 16)
        self.assertLessEqual(dead, -4)

    def test_wudc_2016_efl_round_9(self):
        safe, dead = liveness_bp(False, 9, 8, 382, 9, [15, 13, 12, 13, 12, 12, 12, 12, 12, 11, 11, 10, 10, 10, 10, 11, 11, 12, 11, 10, 12, 9, 9, 10, 11, 11, 11, 10, 9, 11, 8, 8, 9, 8, 9, 10, 10, 9, 10, 8, 10, 7, 9, 8, 9, 8, 8, 9, 8, 7, 8, 9, 9, 7, 8, 6, 6, 7, 7, 7, 6, 7, 6, 6, 6]) # noqa: E501
        self.assertGreaterEqual(safe, 15)
        self.assertLessEqual(dead, 10)

    def test_wudc_2016_efl_round_8(self):
        safe, dead = liveness_bp(False, 8, 8, 382, 9, [13, 10, 11, 12, 11, 11, 12, 10, 11, 8, 10, 7, 10, 9, 9, 10, 11, 12, 9, 10, 9, 9, 9, 8, 11, 8, 9, 7, 7, 10, 7, 8, 6, 8, 7, 9, 10, 7, 8, 8, 8, 5, 8, 8, 7, 8, 7, 9, 6, 6, 7, 6, 8, 7, 5, 6, 6, 7, 6, 6, 4, 4, 6, 5, 5]) # noqa: E501
        self.assertGreaterEqual(safe, 15)
        self.assertLessEqual(dead, 7)

    def test_wudc_2016_efl_round_7(self):
        safe, dead = liveness_bp(False, 7, 8, 382, 9, [12, 7, 9, 9, 9, 8, 11, 8, 9, 6, 8, 6, 8, 8, 8, 7, 8, 10, 8, 10, 6, 9, 8, 8, 8, 8, 9, 7, 7, 7, 6, 8, 6, 7, 4, 9, 10, 5, 5, 5, 6, 5, 7, 8, 7, 5, 7, 9, 6, 6, 6, 3, 6, 6, 5, 5, 6, 5, 6, 5, 4, 3, 5, 5, 2]) # noqa: E501
        self.assertGreaterEqual(safe, 15)
        self.assertLessEqual(dead, 4)

    def test_wudc_2016_efl_round_6(self):
        safe, dead = liveness_bp(False, 6, 8, 382, 9, [12, 5, 7, 7, 8, 7, 9, 7, 7, 6, 5, 6, 5, 6, 6, 4, 6, 8, 7, 8, 5, 8, 5, 8, 6, 5, 7, 7, 7, 6, 5, 8, 6, 5, 2, 6, 7, 4, 4, 5, 6, 2, 7, 7, 7, 4, 5, 7, 5, 6, 6, 3, 4, 3, 3, 5, 3, 5, 4, 2, 4, 2, 3, 5, 1]) # noqa: E501
        self.assertGreaterEqual(safe, 15)
        self.assertLessEqual(dead, 1)

    def test_wudc_2016_efl_round_5(self):
        safe, dead = liveness_bp(False, 5, 8, 382, 9, [9, 5, 5, 6, 7, 4, 7, 5, 4, 5, 4, 4, 5, 3, 6, 2, 5, 5, 5, 8, 4, 6, 3, 5, 4, 4, 6, 4, 5, 4, 4, 7, 4, 4, 0, 5, 6, 3, 3, 4, 5, 2, 5, 5, 5, 4, 4, 5, 5, 4, 6, 2, 3, 3, 2, 2, 3, 3, 1, 2, 3, 1, 3, 4, 1]) # noqa: E501
        self.assertGreaterEqual(safe, 15)
        self.assertLessEqual(dead, -2)

    def test_wudc_2016_efl_round_4(self):
        safe, dead = liveness_bp(False, 4, 8, 382, 9, [7, 3, 5, 6, 5, 2, 7, 3, 3, 5, 3, 4, 4, 3, 4, 2, 5, 3, 5, 6, 4, 4, 3, 4, 3, 3, 6, 2, 3, 2, 3, 4, 2, 2, 0, 4, 5, 3, 3, 1, 2, 1, 3, 2, 3, 4, 4, 2, 4, 1, 6, 1, 0, 2, 0, 2, 3, 3, 1, 2, 3, 1, 1, 1, 0]) # noqa: E501
        self.assertGreaterEqual(safe, 15)
        self.assertLessEqual(dead, -5)

    def test_wudc_2017_open_round_9(self):
        safe, dead = liveness_bp(True, 9, 48, 371, 9, None)
        self.assertGreaterEqual(safe, 18)
        self.assertLessEqual(dead, 13)

    def test_wudc_2017_open_round_8(self):
        safe, dead = liveness_bp(True, 8, 48, 371, 9, None)
        self.assertGreaterEqual(safe, 18)
        self.assertLessEqual(dead, 10)

    def test_wudc_2017_open_round_7(self):
        safe, dead = liveness_bp(True, 7, 48, 371, 9, None)
        self.assertGreaterEqual(safe, 18)
        self.assertLessEqual(dead, 7)

    def test_wudc_2017_open_round_6(self):
        safe, dead = liveness_bp(True, 6, 48, 371, 9, None)
        self.assertGreaterEqual(safe, 18)
        self.assertLessEqual(dead, 4)

    def test_wudc_2017_open_round_5(self):
        safe, dead = liveness_bp(True, 5, 48, 371, 9, None)
        self.assertGreaterEqual(safe, 18)
        self.assertLessEqual(dead, 1)

    def test_wudc_2017_open_round_4(self):
        safe, dead = liveness_bp(True, 4, 48, 371, 9, None)
        self.assertGreaterEqual(safe, 18)
        self.assertLessEqual(dead, -2)

    def test_wudc_2017_esl_round_9(self):
        safe, dead = liveness_bp(False, 9, 16, 371, 9, [17, 16, 18, 15, 15, 14, 15, 17, 15, 15, 14, 14, 13, 16, 15, 14, 12, 15, 13, 13, 15, 13, 14, 14, 14, 12, 13, 13, 11, 14, 14, 12, 11, 11, 12, 11, 11, 12, 11, 13, 10, 13, 10, 11, 12, 11, 11, 10, 10, 10, 13, 10, 11, 11, 10, 9, 12, 11, 10, 12, 12, 12, 11, 9, 11, 11, 11, 11, 9, 11, 10, 10, 10, 11, 12, 11, 11, 10, 11, 10, 8, 10, 11, 11, 11, 9, 10, 9, 11, 9, 10, 9, 10, 10, 8, 10, 10, 9, 9, 7, 9, 8, 9, 7, 6, 9, 8, 9, 9, 9, 8, 8, 7, 9, 7, 7, 8, 7, 5, 8, 6, 6, 8, 7, 7, 7, 3, 4, 4, 5, 3]) # noqa: E501
        self.assertGreaterEqual(safe, 16)
        self.assertLessEqual(dead, 12)

    def test_wudc_2017_esl_round_8(self):
        safe, dead = liveness_bp(False, 8, 16, 371, 9, [17, 16, 16, 13, 12, 13, 12, 14, 12, 12, 12, 11, 13, 13, 12, 11, 11, 12, 11, 12, 13, 10, 12, 12, 12, 10, 11, 13, 8, 12, 12, 12, 9, 9, 10, 11, 8, 10, 10, 12, 9, 11, 9, 10, 10, 9, 11, 9, 10, 8, 11, 9, 10, 10, 9, 9, 11, 11, 7, 10, 10, 12, 10, 9, 8, 10, 11, 10, 8, 9, 7, 8, 10, 8, 9, 11, 10, 10, 10, 7, 8, 9, 11, 11, 8, 9, 8, 6, 9, 8, 8, 9, 7, 10, 6, 9, 8, 8, 9, 7, 7, 8, 9, 6, 6, 8, 6, 6, 6, 8, 8, 6, 6, 8, 4, 6, 7, 5, 5, 7, 6, 4, 5, 7, 7, 7, 3, 3, 2, 5, 3]) # noqa: E501
        self.assertGreaterEqual(safe, 16)
        self.assertLessEqual(dead, 9)

    def test_wudc_2017_esl_round_7(self):
        safe, dead = liveness_bp(False, 7, 16, 371, 9, [14, 13, 15, 10, 9, 13, 12, 11, 10, 10, 9, 8, 12, 11, 11, 10, 8, 11, 9, 9, 11, 9, 12, 11, 9, 8, 10, 10, 8, 9, 11, 9, 8, 8, 8, 11, 7, 7, 10, 11, 9, 10, 9, 8, 10, 6, 9, 6, 9, 7, 9, 7, 7, 9, 6, 8, 10, 10, 6, 7, 9, 10, 9, 7, 7, 7, 8, 8, 8, 8, 5, 8, 7, 6, 7, 8, 10, 8, 10, 7, 7, 7, 9, 8, 8, 8, 6, 4, 7, 7, 6, 7, 6, 7, 5, 8, 7, 6, 7, 6, 6, 5, 7, 6, 6, 6, 5, 6, 5, 5, 7, 6, 5, 5, 2, 6, 7, 5, 4, 5, 3, 4, 5, 5, 6, 4, 3, 3, 1, 3, 3]) # noqa: E501
        self.assertGreaterEqual(safe, 16)
        self.assertLessEqual(dead, 6)

    def test_wudc_2017_esl_round_6(self):
        safe, dead = liveness_bp(False, 6, 16, 371, 9, [11, 10, 12, 8, 7, 10, 11, 8, 10, 9, 9, 5, 11, 11, 9, 9, 6, 10, 8, 7, 8, 6, 9, 9, 7, 7, 8, 10, 6, 6, 11, 7, 5, 8, 6, 8, 5, 6, 8, 8, 9, 8, 8, 7, 7, 6, 6, 5, 7, 6, 6, 7, 7, 6, 5, 5, 10, 7, 5, 7, 7, 8, 8, 4, 7, 5, 6, 6, 5, 7, 5, 5, 4, 4, 4, 6, 9, 6, 7, 6, 7, 7, 6, 7, 6, 7, 6, 4, 6, 7, 3, 7, 6, 6, 5, 8, 7, 6, 4, 4, 5, 5, 6, 5, 6, 6, 5, 5, 5, 4, 4, 5, 4, 3, 2, 6, 5, 4, 2, 3, 3, 4, 3, 4, 4, 3, 2, 2, 1, 2, 3]) # noqa: E501
        self.assertGreaterEqual(safe, 16)
        self.assertLessEqual(dead, 3)

    def test_wudc_2017_esl_round_5(self):
        safe, dead = liveness_bp(False, 5, 16, 371, 9, [8, 8, 9, 7, 5, 8, 9, 7, 7, 7, 6, 5, 9, 8, 8, 7, 5, 7, 7, 6, 6, 6, 6, 7, 6, 5, 8, 7, 6, 6, 8, 7, 5, 5, 3, 5, 4, 5, 6, 5, 6, 5, 5, 5, 6, 6, 4, 5, 5, 6, 5, 4, 7, 5, 4, 5, 7, 4, 5, 6, 7, 5, 7, 4, 4, 4, 3, 5, 4, 4, 3, 5, 4, 4, 4, 5, 6, 5, 7, 3, 6, 6, 4, 4, 5, 4, 4, 4, 6, 4, 1, 6, 4, 5, 4, 5, 6, 4, 2, 3, 3, 3, 5, 3, 3, 4, 3, 5, 5, 4, 4, 4, 3, 3, 2, 6, 3, 2, 2, 2, 3, 2, 2, 2, 1, 3, 2, 0, 1, 1, 0]) # noqa: E501
        self.assertGreaterEqual(safe, 16)
        self.assertLessEqual(dead, 0)

    def test_wudc_2017_esl_round_4(self):
        safe, dead = liveness_bp(False, 4, 16, 371, 9, [5, 8, 6, 5, 4, 8, 7, 5, 7, 6, 5, 4, 8, 5, 6, 4, 4, 5, 5, 3, 5, 3, 5, 5, 4, 5, 8, 5, 6, 3, 5, 4, 3, 5, 3, 4, 3, 4, 5, 5, 4, 4, 3, 4, 6, 4, 3, 5, 3, 3, 4, 3, 4, 4, 1, 5, 5, 3, 3, 5, 5, 3, 5, 4, 3, 1, 2, 4, 2, 4, 3, 5, 3, 1, 3, 3, 4, 4, 5, 3, 4, 4, 3, 2, 4, 4, 1, 4, 4, 4, 1, 3, 4, 3, 4, 3, 4, 2, 2, 1, 2, 3, 3, 3, 3, 4, 3, 5, 3, 3, 2, 4, 3, 3, 2, 3, 2, 1, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 1, 1, 0]) # noqa: E501
        self.assertGreaterEqual(safe, 16)
        self.assertLessEqual(dead, -3)

    def test_wudc_2017_efl_round_9(self):
        safe, dead = liveness_bp(False, 9, 8, 371, 9, [15, 14, 15, 14, 14, 14, 13, 11, 12, 11, 11, 10, 11, 10, 12, 12, 12, 11, 11, 11, 10, 10, 10, 11, 10, 10, 11, 10, 9, 11, 9, 10, 10, 8, 10, 9, 9, 7, 9, 8, 8, 9, 8, 7, 7, 7, 8, 5, 6, 6, 8, 7, 7, 7, 3, 4, 4, 3]) # noqa: E501
        self.assertGreaterEqual(safe, 14)
        self.assertLessEqual(dead, 10)

    def test_wudc_2017_efl_round_8(self):
        safe, dead = liveness_bp(False, 8, 8, 371, 9, [12, 11, 12, 12, 12, 12, 11, 8, 10, 10, 11, 8, 10, 9, 11, 10, 10, 8, 10, 11, 7, 8, 10, 10, 7, 9, 11, 8, 6, 9, 8, 8, 7, 6, 8, 8, 9, 7, 7, 8, 6, 8, 6, 6, 4, 6, 7, 5, 6, 4, 5, 7, 7, 7, 3, 3, 2, 3]) # noqa: E501
        self.assertGreaterEqual(safe, 14)
        self.assertLessEqual(dead, 7)

    def test_wudc_2017_efl_round_7(self):
        safe, dead = liveness_bp(False, 7, 8, 371, 9, [11, 10, 11, 12, 11, 9, 10, 7, 7, 8, 9, 7, 9, 6, 10, 7, 9, 7, 7, 8, 5, 8, 7, 10, 7, 7, 8, 6, 4, 7, 7, 6, 6, 5, 7, 6, 7, 6, 6, 5, 5, 5, 6, 5, 2, 6, 7, 4, 3, 4, 5, 5, 6, 4, 3, 3, 1, 3]) # noqa: E501
        self.assertGreaterEqual(safe, 14)
        self.assertLessEqual(dead, 4)

    def test_wudc_2017_efl_round_6(self):
        safe, dead = liveness_bp(False, 6, 8, 371, 9, [9, 9, 10, 9, 9, 7, 8, 5, 6, 7, 6, 6, 6, 5, 10, 7, 7, 7, 5, 6, 5, 5, 4, 9, 6, 7, 7, 6, 4, 6, 7, 3, 6, 5, 7, 6, 4, 4, 5, 5, 5, 4, 5, 4, 2, 6, 5, 2, 3, 4, 3, 4, 4, 3, 2, 2, 1, 3]) # noqa: E501
        self.assertGreaterEqual(safe, 14)
        self.assertLessEqual(dead, 1)

    def test_wudc_2017_efl_round_5(self):
        safe, dead = liveness_bp(False, 5, 8, 371, 9, [8, 7, 7, 6, 7, 6, 8, 4, 5, 5, 4, 6, 5, 4, 7, 6, 7, 4, 4, 3, 3, 5, 4, 6, 3, 6, 4, 4, 4, 6, 4, 1, 4, 4, 6, 4, 2, 3, 3, 3, 3, 4, 4, 3, 2, 6, 3, 2, 3, 2, 2, 2, 1, 3, 2, 0, 1, 0]) # noqa: E501
        self.assertGreaterEqual(safe, 14)
        self.assertLessEqual(dead, -2)

    def test_wudc_2017_efl_round_4(self):
        safe, dead = liveness_bp(False, 4, 8, 371, 9, [6, 4, 5, 5, 5, 4, 8, 3, 4, 4, 3, 3, 4, 1, 5, 5, 5, 3, 1, 2, 3, 5, 3, 4, 3, 4, 2, 1, 4, 4, 4, 1, 4, 4, 4, 2, 2, 1, 2, 3, 3, 3, 4, 3, 2, 3, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 1, 0]) # noqa: E501
        self.assertGreaterEqual(safe, 14)
        self.assertLessEqual(dead, -5)

    def test_wudc_2018_open_round_9(self):
        safe, dead = liveness_bp(True, 9, 48, 314, 9, None)
        self.assertGreaterEqual(safe, 18)
        self.assertLessEqual(dead, 13)

    def test_wudc_2018_open_round_8(self):
        safe, dead = liveness_bp(True, 8, 48, 314, 9, None)
        self.assertGreaterEqual(safe, 18)
        self.assertLessEqual(dead, 10)

    def test_wudc_2018_open_round_7(self):
        safe, dead = liveness_bp(True, 7, 48, 314, 9, None)
        self.assertGreaterEqual(safe, 18)
        self.assertLessEqual(dead, 7)

    def test_wudc_2018_open_round_6(self):
        safe, dead = liveness_bp(True, 6, 48, 314, 9, None)
        self.assertGreaterEqual(safe, 18)
        self.assertLessEqual(dead, 4)

    def test_wudc_2018_open_round_5(self):
        safe, dead = liveness_bp(True, 5, 48, 314, 9, None)
        self.assertGreaterEqual(safe, 18)
        self.assertLessEqual(dead, 1)

    def test_wudc_2018_open_round_4(self):
        safe, dead = liveness_bp(True, 4, 48, 314, 9, None)
        self.assertGreaterEqual(safe, 18)
        self.assertLessEqual(dead, -2)

    def test_wudc_2018_esl_round_9(self):
        safe, dead = liveness_bp(False, 9, 16, 314, 9, [22, 19, 16, 17, 16, 14, 15, 15, 15, 15, 16, 14, 13, 15, 14, 13, 15, 15, 15, 12, 13, 14, 12, 13, 12, 14, 13, 12, 11, 13, 13, 13, 10, 12, 10, 11, 13, 11, 12, 10, 13, 10, 10, 11, 12, 12, 12, 9, 11, 11, 9, 10, 9, 10, 9, 9, 10, 11, 10, 11, 10, 10, 11, 8, 9, 9, 9, 8, 9, 10, 10, 9, 10, 10, 8, 10, 10, 9, 8, 8, 8, 9, 9, 7, 8, 9, 8, 7, 8, 8, 8, 7, 8, 8, 8, 5, 8, 7, 6, 6, 6, 5, 2]) # noqa: E501
        self.assertGreaterEqual(safe, 16)
        self.assertLessEqual(dead, 12)

    def test_wudc_2018_esl_round_8(self):
        safe, dead = liveness_bp(False, 8, 16, 314, 9, [19, 17, 15, 16, 13, 13, 13, 12, 15, 14, 14, 13, 11, 12, 11, 13, 12, 12, 14, 10, 12, 14, 9, 10, 9, 13, 10, 12, 10, 13, 12, 12, 8, 12, 10, 8, 10, 10, 10, 9, 11, 9, 9, 11, 10, 12, 11, 8, 10, 9, 7, 10, 8, 10, 6, 9, 9, 8, 10, 9, 8, 8, 9, 8, 8, 7, 8, 6, 9, 10, 9, 9, 10, 9, 6, 8, 7, 9, 8, 6, 8, 6, 7, 6, 5, 6, 7, 7, 7, 5, 8, 6, 6, 7, 7, 5, 7, 6, 6, 6, 6, 4, 2]) # noqa: E501
        self.assertGreaterEqual(safe, 16)
        self.assertLessEqual(dead, 9)

    def test_wudc_2018_esl_round_7(self):
        safe, dead = liveness_bp(False, 7, 16, 314, 9, [16, 14, 12, 13, 11, 12, 10, 9, 13, 14, 12, 13, 10, 11, 8, 10, 9, 10, 11, 9, 9, 11, 7, 10, 9, 10, 7, 9, 9, 11, 10, 10, 8, 11, 7, 7, 8, 7, 8, 7, 10, 6, 6, 8, 10, 9, 8, 8, 8, 8, 6, 10, 8, 9, 6, 7, 6, 8, 8, 6, 6, 7, 8, 6, 5, 5, 5, 6, 7, 7, 8, 8, 7, 6, 5, 6, 6, 7, 7, 4, 7, 5, 7, 4, 5, 6, 5, 5, 4, 5, 6, 6, 6, 7, 5, 4, 7, 5, 6, 5, 4, 4, 0]) # noqa: E501
        self.assertGreaterEqual(safe, 16)
        self.assertLessEqual(dead, 6)

    def test_wudc_2018_esl_round_6(self):
        safe, dead = liveness_bp(False, 6, 16, 314, 9, [14, 14, 11, 10, 10, 9, 10, 9, 11, 11, 9, 10, 9, 8, 8, 7, 9, 9, 8, 9, 8, 8, 7, 7, 9, 7, 6, 6, 8, 9, 10, 7, 8, 8, 7, 7, 7, 6, 7, 6, 7, 5, 6, 7, 7, 7, 7, 8, 7, 7, 6, 7, 5, 6, 6, 7, 3, 5, 6, 4, 5, 5, 6, 6, 5, 3, 4, 5, 4, 7, 7, 6, 6, 5, 5, 6, 3, 4, 7, 4, 5, 3, 5, 3, 5, 4, 4, 3, 2, 2, 5, 6, 3, 5, 4, 4, 5, 4, 6, 5, 4, 1, 0]) # noqa: E501
        self.assertGreaterEqual(safe, 16)
        self.assertLessEqual(dead, 3)

    def test_wudc_2018_esl_round_5(self):
        safe, dead = liveness_bp(False, 5, 16, 314, 9, [12, 11, 9, 7, 7, 7, 7, 8, 8, 8, 8, 7, 8, 8, 8, 7, 6, 8, 8, 6, 5, 6, 4, 6, 7, 5, 6, 6, 5, 7, 8, 6, 7, 7, 4, 6, 4, 4, 5, 4, 5, 5, 5, 7, 5, 6, 7, 7, 6, 7, 4, 4, 5, 5, 3, 6, 2, 4, 4, 4, 4, 5, 4, 3, 4, 3, 3, 5, 4, 5, 5, 6, 5, 3, 4, 4, 3, 2, 4, 3, 4, 3, 2, 1, 2, 1, 3, 3, 2, 1, 5, 3, 2, 3, 3, 3, 2, 4, 4, 3, 1, 1, 0]) # noqa: E501
        self.assertGreaterEqual(safe, 16)
        self.assertLessEqual(dead, 0)

    def test_wudc_2018_esl_round_4(self):
        safe, dead = liveness_bp(False, 4, 16, 314, 9, [9, 9, 6, 4, 4, 5, 5, 8, 8, 5, 6, 5, 5, 6, 5, 6, 4, 6, 6, 5, 3, 4, 3, 5, 5, 5, 3, 6, 4, 5, 6, 6, 4, 4, 4, 4, 3, 3, 2, 4, 4, 4, 2, 5, 3, 4, 4, 5, 5, 5, 1, 4, 2, 3, 3, 4, 2, 2, 3, 3, 3, 4, 2, 2, 2, 3, 1, 3, 4, 3, 3, 4, 3, 2, 3, 2, 1, 0, 2, 3, 1, 2, 2, 1, 2, 1, 1, 3, 2, 1, 2, 3, 1, 2, 3, 0, 1, 3, 3, 3, 0, 0, 0]) # noqa: E501
        self.assertGreaterEqual(safe, 16)
        self.assertLessEqual(dead, -3)

    def test_wudc_2018_efl_round_9(self):
        safe, dead = liveness_bp(False, 9, 8, 314, 9, [15, 13, 15, 13, 13, 13, 12, 11, 12, 11, 11, 12, 10, 13, 10, 10, 11, 12, 12, 10, 9, 9, 10, 11, 10, 10, 8, 9, 8, 9, 10, 8, 9, 8, 8, 8, 9, 9, 7, 8, 9, 8, 7, 8, 7, 8, 8, 5, 8, 6, 6, 5]) # noqa: E501
        self.assertGreaterEqual(safe, 14)
        self.assertLessEqual(dead, 10)

    def test_wudc_2018_efl_round_8(self):
        safe, dead = liveness_bp(False, 8, 8, 314, 9, [12, 13, 14, 12, 10, 10, 12, 10, 12, 8, 10, 10, 9, 11, 9, 9, 11, 12, 11, 10, 8, 6, 9, 9, 8, 8, 8, 8, 6, 9, 9, 6, 9, 8, 6, 8, 6, 7, 6, 5, 6, 7, 7, 7, 6, 7, 7, 5, 7, 6, 6, 4]) # noqa: E501
        self.assertGreaterEqual(safe, 14)
        self.assertLessEqual(dead, 7)

    def test_wudc_2018_efl_round_7(self):
        safe, dead = liveness_bp(False, 7, 8, 314, 9, [11, 10, 11, 9, 10, 7, 9, 9, 11, 7, 7, 8, 7, 10, 6, 6, 8, 9, 8, 10, 8, 6, 6, 6, 6, 7, 6, 5, 6, 8, 6, 5, 7, 7, 4, 7, 5, 7, 4, 5, 6, 5, 5, 4, 6, 7, 5, 4, 7, 5, 4, 4]) # noqa: E501
        self.assertGreaterEqual(safe, 14)
        self.assertLessEqual(dead, 4)

    def test_wudc_2018_efl_round_6(self):
        safe, dead = liveness_bp(False, 6, 8, 314, 9, [8, 7, 8, 8, 7, 6, 6, 8, 8, 7, 6, 7, 6, 7, 5, 6, 7, 7, 7, 7, 5, 6, 3, 4, 5, 5, 6, 5, 5, 6, 5, 5, 4, 7, 4, 5, 3, 5, 3, 5, 4, 4, 3, 2, 6, 5, 4, 4, 5, 5, 4, 1]) # noqa: E501
        self.assertGreaterEqual(safe, 14)
        self.assertLessEqual(dead, 1)

    def test_wudc_2018_efl_round_5(self):
        safe, dead = liveness_bp(False, 5, 8, 314, 9, [8, 7, 8, 5, 6, 6, 6, 5, 7, 6, 4, 5, 4, 5, 5, 5, 7, 6, 7, 4, 5, 3, 2, 4, 4, 5, 3, 4, 5, 6, 3, 4, 2, 4, 3, 4, 3, 2, 1, 2, 1, 3, 3, 2, 3, 3, 3, 3, 2, 3, 1, 1]) # noqa: E501
        self.assertGreaterEqual(safe, 14)
        self.assertLessEqual(dead, -2)

    def test_wudc_2018_efl_round_4(self):
        safe, dead = liveness_bp(False, 4, 8, 314, 9, [6, 6, 6, 3, 5, 3, 6, 4, 4, 4, 3, 2, 4, 4, 4, 2, 5, 4, 4, 4, 2, 3, 2, 3, 3, 4, 2, 2, 3, 4, 2, 3, 0, 2, 3, 1, 2, 2, 1, 2, 1, 1, 3, 2, 3, 2, 3, 0, 1, 3, 0, 0]) # noqa: E501
        self.assertGreaterEqual(safe, 14)
        self.assertLessEqual(dead, -5)
