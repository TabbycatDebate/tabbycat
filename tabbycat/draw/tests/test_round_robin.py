import unittest

from draw.generator import DrawGenerator, DrawUserError
from draw.generator.data.bp_round_robin import BP_ROUND_ROBIN_TABLES
from draw.generator.roundrobin import berger_pairings_for_round

from .utils import TestTeam


class TestBergerRoundRobin(unittest.TestCase):

    def test_four_teams_three_rounds(self):
        teams = [
            TestTeam(1, 'A', seed=1, side_history=[0, 0], hist=[]),
            TestTeam(2, 'B', seed=2, side_history=[0, 0], hist=[]),
            TestTeam(3, 'C', seed=3, side_history=[0, 0], hist=[]),
            TestTeam(4, 'D', seed=4, side_history=[0, 0], hist=[]),
        ]
        r1 = berger_pairings_for_round(teams, 1)
        self.assertEqual({frozenset(p) for p in r1}, {frozenset((teams[0], teams[1])), frozenset((teams[2], teams[3]))})

        r2 = berger_pairings_for_round(teams, 2)
        self.assertEqual({frozenset(p) for p in r2}, {frozenset((teams[0], teams[2])), frozenset((teams[3], teams[1]))})

        r3 = berger_pairings_for_round(teams, 3)
        self.assertEqual({frozenset(p) for p in r3}, {frozenset((teams[0], teams[3])), frozenset((teams[1], teams[2]))})

    def test_draw_generator_two_team_rr(self):
        teams = [
            TestTeam(10, 'X', seed=1, side_history=[0, 0], hist=[]),
            TestTeam(20, 'Y', seed=2, side_history=[0, 0], hist=[]),
        ]
        d = DrawGenerator(2, "round_robin", teams, rrseq=1, avoid_conflicts="off", side_allocations="random")
        pairings = d.generate()
        self.assertEqual(len(pairings), 1)
        self.assertEqual(set(pairings[0].teams), {teams[0], teams[1]})


class TestBPRoundRobinTables(unittest.TestCase):

    def test_sixteen_team_round_five_matches_plan(self):
        teams = [TestTeam(i, 'I', seed=i, side_history=[0, 0, 0, 0], hist=[]) for i in range(1, 17)]
        d = DrawGenerator(4, "round_robin", teams, rrseq=5)
        pairings = d.generate()
        seeds_per_room = [tuple(sorted(t.seed for t in p.teams)) for p in pairings]
        self.assertCountEqual(seeds_per_room, [(1, 2, 3, 4), (5, 6, 7, 8), (9, 10, 11, 12), (13, 14, 15, 16)])

    def test_sixteen_team_round_one_first_debate_order(self):
        teams = [TestTeam(i, 'I', seed=i, side_history=[0, 0, 0, 0], hist=[]) for i in range(1, 17)]
        d = DrawGenerator(4, "round_robin", teams, rrseq=1)
        pairings = d.generate()
        first = pairings[0].teams
        self.assertEqual([t.seed for t in first], [12, 14, 1, 7])

    def test_unsupported_team_count_raises(self):
        teams = [TestTeam(i, 'I', seed=i, side_history=[0, 0, 0, 0], hist=[]) for i in range(1, 13)]
        d = DrawGenerator(4, "round_robin", teams, rrseq=1)
        with self.assertRaises(DrawUserError):
            d.generate()


class TestBPRoundRobinTableSanity(unittest.TestCase):

    def test_all_sizes_cover_distinct_teams_per_round(self):
        for n, rounds in BP_ROUND_ROBIN_TABLES.items():
            for rnd in rounds:
                seen = set()
                for debate in rnd:
                    for s in debate:
                        self.assertNotIn(s, seen, msg=(n, debate))
                        seen.add(s)
                self.assertEqual(len(seen), n)
