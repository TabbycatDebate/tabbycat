"""Round-robin draw generators (two-team Berger; BP preset tables)."""

from django.utils.translation import gettext as _

from .common import BaseBPDrawGenerator, BasePairDrawGenerator, DrawUserError
from .data.bp_round_robin import BP_ROUND_ROBIN_TABLES
from .pairing import Pairing, PolyPairing


def berger_pairings_for_round(teams, rrseq):
    """Return list of (team_a, team_b) for one Berger / circle round.

    `teams` is ordered list of n even teams. `rrseq` is 1-based index into the
    n-1 round robin schedule.
    """
    n = len(teams)
    if n < 2 or n % 2:
        raise DrawUserError(_("Berger round-robin requires an even number of teams with no byes in the draw."))
    max_rr = n - 1
    if rrseq < 1 or rrseq > max_rr:
        raise DrawUserError(_("This round's position in the round-robin schedule (%(rr)d) is not valid for "
            "%(n)d teams (expected between 1 and %(max)d).") % {'rr': rrseq, 'n': n, 'max': max_rr})

    fixed = teams[0]
    rotating = list(teams[1:])
    k = rrseq - 1
    state = rotating[k:] + rotating[:k]
    out = [(fixed, state[0])]
    m = len(state)
    for i in range(1, m // 2 + 1):
        out.append((state[i], state[m - i]))
    return out


class TwoTeamRoundRobinDrawGenerator(BasePairDrawGenerator):
    """Berger (circle) schedule for two-team formats."""

    requires_rrseq = True
    pairing_class = Pairing
    DEFAULT_OPTIONS = {"avoid_history": False}

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("avoid_history", False)
        super().__init__(*args, **kwargs)

    def generate(self):
        pairs = berger_pairings_for_round(self.teams, self.rrseq)
        pairings = [
            Pairing(teams=list(p), bracket=0, room_rank=i + 1)
            for i, p in enumerate(pairs)
        ]
        self.allocate_sides(pairings)
        return pairings


class BPRoundRobinDrawGenerator(BaseBPDrawGenerator):
    """BP round-robin from preset tables (supported sizes only)."""

    requires_rrseq = True
    DEFAULT_OPTIONS = {}

    def generate(self):
        n = len(self.teams)
        if n not in BP_ROUND_ROBIN_TABLES:
            supported = ", ".join(str(x) for x in sorted(BP_ROUND_ROBIN_TABLES))
            raise DrawUserError(_("British Parliamentary round-robin draws are only implemented for "
                "%(supported)s teams at the moment (this tournament has %(n)d).") % {
                'supported': supported,
                'n': n,
            })

        tables = BP_ROUND_ROBIN_TABLES[n]
        if self.rrseq < 1 or self.rrseq > len(tables):
            raise DrawUserError(_("This round's position in the round-robin schedule (%(rr)d) is not valid — "
                "expected between 1 and %(max)d for %(n)d teams.") % {
                'rr': self.rrseq, 'max': len(tables), 'n': n,
            })

        teams_by_seed = sorted(self.teams, key=lambda t: t.seed)

        for i, t in enumerate(teams_by_seed, start=1):
            if t.seed != i:
                raise DrawUserError(_("Team seeds must be the integers 1 through %(n)d for BP round-robin.") % {'n': n})

        return [
            PolyPairing(teams=[teams_by_seed[s-1] for s in debate], bracket=0, room_rank=i)
            for i, debate in enumerate(tables[self.rrseq - 1], start=1)
        ]
