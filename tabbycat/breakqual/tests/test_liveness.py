from django.test import TestCase

from ..utils import calculate_bp, calculate_2vs2


class TestFeedbackProgress(TestCase):
    """ Params are:
    is_general, current round, break size, elgibile teams, total_rounds, scores
    """

    # 2vs2
    def test_case_australs_2017_open(self):
        safe, dead = calculate_2vs2(True, 8, 16, 79, 8, None)
        self.assertIs(safe, 6) # All on 6 broke
        self.assertIs(dead, 3) # Some on 5 broke

    def test_case_australs_2017_esl(self):
        # Note 2 teams bypassed ESL break; 8 eligible
        safe, dead = calculate_2vs2(False, 8, 4, 8, 8, [5,4,3,3,1,1])
        self.assertIs(safe, 3) # All on 4 broke
        self.assertIs(dead, 1) # Some (all?) on 3 broke

    def test_case_easters_2017_open(self):
        safe, dead = calculate_2vs2(True, 6, 16, 100, 6, None)
        self.assertIs(safe, 5) # All on 5 broke
        self.assertIs(dead, 2) # Some on 4 broke

    def test_case_australs_2016_open(self):
        safe, dead = calculate_2vs2(True, 8, 16, 74, 8, None)
        self.assertIs(safe, 6)
        self.assertIs(dead, 3)

    def test_case_australs_2016_esl(self):
        # Note 2 teams bypassed ESL break
        break_cat_scores = [6,5,3,3,3,1] # Worst case (-1 on finishing scores)
        safe, dead = calculate_2vs2(False, 8, 4, 8, 8, break_cat_scores)
        self.assertIs(safe, 5)
        self.assertIs(dead, 1)

    def test_case_australs_2015_open(self):
        safe, dead = calculate_2vs2(True, 8, 16, 78, 8, None)
        self.assertIs(safe, 6)
        self.assertIs(dead, 3)
