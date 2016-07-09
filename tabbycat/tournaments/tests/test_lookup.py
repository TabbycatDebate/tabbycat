from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from tournaments.models import Round, Tournament


class TestRoundLookup(TestCase):

    def setUp(self):
        self.tournament = Tournament.objects.create()
        self.rd = Round.objects.create(tournament=self.tournament, name="A Test Round", abbreviation="ATR", seq=1)

    def tearDown(self):
        self.rd.delete()
        self.tournament.delete()

    def test_lookup(self):
        self.assertEqual(Round.objects.lookup("A Test Round"), self.rd)
        self.assertEqual(Round.objects.lookup("ATR"), self.rd)
        self.assertRaises(ObjectDoesNotExist, Round.objects.lookup, "randomstring")

    def test_lookup_with_tournament(self):
        other_tournament = Tournament.objects.create(slug="other")
        self.assertEqual(Round.objects.lookup("A Test Round", tournament=self.tournament), self.rd)
        self.assertEqual(Round.objects.lookup("ATR", tournament=self.tournament), self.rd)
        self.assertRaises(ObjectDoesNotExist, Round.objects.lookup, "A Test Round", tournament=other_tournament)
        self.assertRaises(ObjectDoesNotExist, Round.objects.lookup, "ATR", tournament=other_tournament)
        other_tournament.delete()
