from draw.manager import RoundRobinDrawManager
from tournaments.models import Round
from utils.tests import BaseMinimalTournamentTestCase


class RoundRobinRrseqScheduleGroupTests(BaseMinimalTournamentTestCase):
    """``get_rrseq`` must follow schedule slots, not database ``seq`` within a slot."""

    def _rr_round(self, seq, schedule_group, name, abbr):
        return Round.objects.create(
            tournament=self.tournament,
            seq=seq,
            schedule_group=schedule_group,
            name=name,
            abbreviation=abbr,
            stage=Round.Stage.PRELIMINARY,
            draw_type=Round.DrawType.ROUNDROBIN,
        )

    def test_parallel_panels_share_rrseq(self):
        r1a = self._rr_round(1, 1, 'Round 1 (A)', 'R1A')
        r1b = self._rr_round(2, 1, 'Round 1 (B)', 'R1B')
        r2a = self._rr_round(3, 2, 'Round 2 (A)', 'R2A')

        self.assertEqual(RoundRobinDrawManager(r1a).get_rrseq(), 1)
        self.assertEqual(RoundRobinDrawManager(r1b).get_rrseq(), 1)
        self.assertEqual(RoundRobinDrawManager(r2a).get_rrseq(), 2)

    def test_non_contiguous_schedule_group_order(self):
        """Distinct groups are ordered by ``schedule_group`` value, not insertion order."""
        r_slot3 = self._rr_round(1, 3, 'R1', 'R1')
        r_slot1a = self._rr_round(2, 1, 'R2A', 'R2A')
        r_slot1b = self._rr_round(3, 1, 'R2B', 'R2B')

        self.assertEqual(RoundRobinDrawManager(r_slot1a).get_rrseq(), 1)
        self.assertEqual(RoundRobinDrawManager(r_slot1b).get_rrseq(), 1)
        self.assertEqual(RoundRobinDrawManager(r_slot3).get_rrseq(), 2)
