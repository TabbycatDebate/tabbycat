from utils.tests import BaseDebateTestCase

from ..models import Adjudicator, Institution


class TestInstitution(BaseDebateTestCase):
    def test_objects(self):
        self.failUnlessEqual(4, Institution.objects.count())


class TestAdjudicator(BaseDebateTestCase):
    def test_objects(self):
        self.failUnlessEqual(8, Adjudicator.objects.count())
