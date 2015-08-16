from allocator import Allocator

class PanelMaker(object):
    RANK_A = 0
    RANK_B = 1
    RANK_C = 2
    RANK_D = 3
    RANK_E = 4

    RANK_RANGES = (
        (RANK_A, 4.5, 5),
        (RANK_B, 3.5, 4.5),
        (RANK_C, 2.5, 3.5),
        (RANK_D, 1.5, 2.5),
        (RANK_E, 1, 1.5),
    )

    def _rate(self, adj):
        score = adj.test_score

        for rank, lo, hi in self.RANK_RANGES:
            if lo <= score <= hi:
                return rank
        raise

    def rate_adjudicators(self, adjudicators):
        all = [(adj, self._rate(adj)) for adj in adjudicators]
        return [(adj, rank) for adj, rank in all if rank != self.RANK_E]

    def _get_single_chairs(self):

        clone = list(self.available)

        singles = []
        for adj, rank in clone:
            if rank in (self.RANK_A, self.RANK_B):
                self.available.remove((adj, rank))
                singles.append(adj)

        return singles

    def form_panels(self, adjudicators, num_panels):
        self.panels = []
        self.available = self.rate_adjudicators(adjudicators)

        singles = self._get_single_chairs()
        for adj in singles:
            self.add_panel(adj)

        n_left = max(0, num_panels - len(singles))
        self.build_panels(n_left)

        return self.panels

    def build_panels(self, panels_left):
        assert panels_left <= len(self.available) // 3
        num_b = self._count(self.RANK_B)
        num_c = self._count(self.RANK_C)
        num_d = self._count(self.RANK_D)

        if num_b / 2 < panels_left:
            self.build(self.RANK_B, self.RANK_B, self.RANK_B, num_b % 2)
            num_bbc = (num_b // 2) - (num_b % 2)
            if num_c >= num_bbc:
                self.build(self.RANK_B, self.RANK_B, self.RANK_C, num_bbc)
                num_c -= num_bbc
            else:
                raise # not enough C's
        else:
            self.build(self.RANK_B, self.RANK_B, self.RANK_B, num_b -
                       panels_left * 2)
            num_bbc = panels_left * 3 - num_b
            if num_c >= num_bbc:
                self.build(self.RANK_B, self.RANK_B, self.RANK_C, num_bbc)
                num_c -= num_bbc

        if num_c // 3 >= panels_left:
            self.build(self.RANK_C, self.RANK_C, self.RANK_C, panels_left)
        elif num_c / 2 < panels_left:
            num_ccc = num_c % 2
            num_ccd = (num_c // 2) - num_ccc
            num_ddd = panels_left - (num_c // 2)

            self.build(self.RANK_C, self.RANK_C, self.RANK_C, num_ccc)
            self.build(self.RANK_C, self.RANK_C, self.RANK_D, num_ccd)
            self.build(self.RANK_D, self.RANK_D, self.RANK_D, num_ddd)
        else:
            self.build(self.RANK_C, self.RANK_C, self.RANK_C, num_c -
                       panels_left * 2)
            self.build(self.RANK_C, self.RANK_C, self.RANK_D, panels_left * 3 -
                       num_c)


    def build(self, r1, r2, r3, n):
        for i in range(n):
            self.add_panel(self.pop(r1), self.pop(r2), self.pop(r3))

    def pop(self, r):
        for adj, rank in self.available:
            if rank == r:
                self.available.remove((adj, rank))
                return adj
        raise

    def add_panel(self, *adjs):
        self.panels.append(StabPanel(adjs))

    def _count(self, r):
        return len([(adj, rank) for adj, rank in self.available if rank == r])

class StabAllocator(Allocator):
    def allocate(self, avoid_conflicts=True):
        p = PanelMaker()
        panels = p.form_panels(self.adjudicators, len(self.debates))

        assert len(self.debates) <= len(panels)

        self.debates.sort(key=lambda d: self.get_debate_energy(d), reverse=True)
        panels.sort(key=lambda p:p.get_energy(), reverse=True)

        self.pairings = zip(self.debates, panels)

        if avoid_conflicts:
            for i, (debate, panel) in enumerate(self.pairings):
                if panel.conflicts(debate):
                    j = self.search_swap(i, range(i, 0, -1))
                    if j is None:
                        j = self.search_swap(i, range(i+1, len(panels)))

        from adjallocation.models import AdjudicatorAllocation

        allocation = []
        for debate, panel in self.pairings:
            a = AdjudicatorAllocation(debate)
            a.chair = panel[0]
            a.panel = panel[1:]
            allocation.append(a)

        return allocation

    def get_debate_energy(self, debate, bubble=False):
        # TODO: does TeamAtRound exist?
        from tournaments.models import TeamAtRound
        from draw.models import DebateTeam
        aff_team = TeamAtRound(debate.aff_team, debate.round)
        neg_team = TeamAtRound(debate.neg_team, debate.round)

        energy = aff_team.points * 300
        energy += neg_team.points * 300
        energy += aff_team.speaker_score
        energy += neg_team.speaker_score

        return energy


    def search_swap(self, idx, search_range):
        base_debate, base_panel = self.pairings[idx]

        for j in search_range:
            debate, panel = self.pairings[j]
            if not (base_panel.conflicts(debate) or
                    panel.conflicts(base_debate)):
                # do swap
                self.pairings[idx] = (base_debate, panel)
                self.pairings[j] = (debate, base_panel)
                return j
        return None


class StabPanel(object):
    def __init__(self, panel):
        self.panel = list(panel)
        self.panel.sort(key=lambda a: a.score, reverse=True)

    def __getattr__(self, name):
        return getattr(self.panel, name)

    def __getitem__(self, o):
        return self.panel.__getitem__(o)

    def get_energy(self):
        return sum(a.score for a in self.panel) / len(self.panel)

    def conflicts(self, debate):
        for adj in self.panel:
            for team in (debate.aff_team, debate.neg_team):
                if adj.conflict_with(team):
                    return True
        return False

def test():
    p = PanelMaker()
    from tournaments.models import Round
    r = Round.objects.get(pk=1)

    a = StabAllocator(r.debates(), r.active_adjudicators.all())
    return a.allocate()

if __name__ == '__main__':
    test()
