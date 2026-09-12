from django.test import TestCase

from participants.models import Adjudicator
from utils.tests import CompletedTournamentTestMixin

from ..testers import get_tested_rounds, tester_ids


class TesterTests(CompletedTournamentTestMixin, TestCase):

    def setUp(self):
        super().setUp()
        Adjudicator.objects.filter(tournament=self.tournament).update(
            adj_core=False, is_tester=False)

    def a_panel_of_at_least(self, size):
        for debate in self.tournament.round_set.first().debate_set.all():
            allocations = list(debate.debateadjudicator_set.all())
            if len(allocations) >= size:
                return debate, allocations
        self.skipTest("no panel of %d in the fixture" % size)

    def test_adj_core_members_are_testers_without_being_marked(self):
        adj = self.tournament.adjudicator_set.first()
        adj.adj_core = True
        adj.save()
        self.assertIn(adj.pk, tester_ids(self.tournament))

    def test_marked_adjudicators_are_testers(self):
        adj = self.tournament.adjudicator_set.first()
        adj.is_tester = True
        adj.save()
        self.assertIn(adj.pk, tester_ids(self.tournament))

    def test_nobody_is_tested_when_there_are_no_testers(self):
        self.assertEqual(get_tested_rounds(self.tournament), {})

    def test_sitting_with_a_tester_counts_as_tested(self):
        debate, allocations = self.a_panel_of_at_least(2)
        tester, other = allocations[0], allocations[1]
        tester.adjudicator.is_tester = True
        tester.adjudicator.save()

        tested = get_tested_rounds(self.tournament)
        self.assertIn(debate.round_id, tested.get(other.adjudicator_id, set()))

    def test_a_tester_is_not_tested_by_their_own_presence(self):
        debate, allocations = self.a_panel_of_at_least(1)
        solo = allocations[0]
        solo.adjudicator.is_tester = True
        solo.adjudicator.save()

        tested = get_tested_rounds(self.tournament)
        self.assertNotIn(debate.round_id, tested.get(solo.adjudicator_id, set()))
