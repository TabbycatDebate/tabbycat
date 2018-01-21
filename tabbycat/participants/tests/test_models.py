from django.core.exceptions import ValidationError

from utils.tests import BaseDebateTestCase

from participants.models import Adjudicator, Institution


class TestInstitution(BaseDebateTestCase):
    def test_objects(self):
        self.failUnlessEqual(4, Institution.objects.count())


class TestAdjudicator(BaseDebateTestCase):
    def test_objects(self):
        self.failUnlessEqual(8, Adjudicator.objects.count())

    def test_invalid_score(self):
        adj = Adjudicator(
            tournament=self.t,
            name="Adjudicator X",
            test_score=self.t.pref('adj_min_score')-1)
        self.assertRaises(ValidationError, adj.clean)
        adj = Adjudicator(
            tournament=self.t,
            name="Adjudicator X",
            test_score=self.t.pref('adj_max_score')+1)
        self.assertRaises(ValidationError, adj.clean)
