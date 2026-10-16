from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from tournaments.models import Round, Tournament


class TestRoundLookup(TestCase):

    def setUp(self):
        self.tournament = Tournament.objects.create()
        self.rd = Round.objects.create(tournament=self.tournament, name="A Test Round", abbreviation="ATR", seq=1, schedule_group=1)

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

    def test_schedule_group_defaults_to_seq(self):
        rd = Round.objects.create(tournament=self.tournament, name="Round 2", abbreviation="R2", seq=2)
        self.assertEqual(rd.schedule_group, 2)


class TestCurrentRoundSeqLimit(TestCase):

    def setUp(self):
        self.tournament = Tournament.objects.create()

    def test_no_rounds(self):
        self.assertEqual(self.tournament.current_round_seq_limit, 0)

    def test_all_rounds_completed(self):
        for seq in (1, 2):
            Round.objects.create(tournament=self.tournament, seq=seq, completed=True)

        self.tournament = Tournament.objects.get(pk=self.tournament.pk)
        self.assertEqual(self.tournament.current_rounds, [])
        self.assertEqual(self.tournament.current_round_seq_limit, 2)

    def test_elimination_round_without_draw(self):
        Round.objects.create(tournament=self.tournament, seq=1, completed=True)
        Round.objects.create(tournament=self.tournament, seq=2, stage=Round.Stage.ELIMINATION)

        self.tournament = Tournament.objects.get(pk=self.tournament.pk)
        self.assertEqual(self.tournament.current_rounds, [])
        self.assertEqual(self.tournament.current_round_seq_limit, 2)

    def test_parallel_current_rounds(self):
        for seq in (1, 2):
            Round.objects.create(tournament=self.tournament, seq=seq, schedule_group=1)
        Round.objects.create(tournament=self.tournament, seq=3, schedule_group=2)

        self.assertEqual(self.tournament.current_round_seq_limit, 2)
