from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from actionlog.models import ActionLogEntry
from adjallocation.consumers import AdjudicatorAllocationWorkerConsumer
from adjallocation.models import DebateAdjudicator
from adjallocation.preformed import update_or_create_preformed_panels
from adjallocation.preformed.anticipated import calculate_anticipated_draw
from utils.tests import CompletedTournamentTestMixin


class CreatePreformedPanelsTests(CompletedTournamentTestMixin, TestCase):
    round_seq = 4

    def setUp(self):
        super().setUp()
        self.consumer = AdjudicatorAllocationWorkerConsumer()
        self.user = get_user_model().objects.get()
        self.anticipated = list(calculate_anticipated_draw(self.round))

    def create_preformed_panels(self):
        """Runs the worker action and returns the message and its level."""
        with patch.object(self.consumer, 'return_response') as return_response:
            self.consumer.create_preformed_panels({'extra': {
                'round_id': self.round.id,
                'user_id': self.user.id,
                'group_name': 'panels_test',
            }})
        return_response.assert_called_once()
        _, _, msg, level = return_response.call_args.args
        return msg, level

    def assertPanelsMatchAnticipatedDraw(self):  # noqa: N802
        panels = self.round.preformedpanel_set.order_by('room_rank')
        self.assertEqual([(p.bracket_min, p.bracket_max, p.liveness) for p in panels], self.anticipated)

    def test_anticipated_draw_has_brackets(self):
        # Guards the other tests: refreshing would be indistinguishable from
        # resetting if the anticipated draw were all zeroes.
        self.assertTrue(any(bracket_max > 0 for _, bracket_max, _ in self.anticipated))

    def test_create_panels(self):
        msg, level = self.create_preformed_panels()

        self.assertEqual(level, 'success')
        self.assertIn("created new preformed panels", msg)
        self.assertEqual(self.round.preformedpanel_set.count(), len(self.anticipated))
        self.assertPanelsMatchAnticipatedDraw()
        self.assertTrue(ActionLogEntry.objects.filter(round=self.round, user=self.user,
            type=ActionLogEntry.ActionType.PREFORMED_PANELS_CREATE).exists())

    def test_refresh_keeps_adjudicators_and_importance(self):
        update_or_create_preformed_panels(self.round)
        self.round.preformedpanel_set.update(bracket_min=0, bracket_max=0, liveness=0)
        panel = self.round.preformedpanel_set.get(room_rank=1)
        panel.importance = 2
        panel.save()
        adjudicator = self.tournament.adjudicator_set.first()
        panel.preformedpaneladjudicator_set.create(adjudicator=adjudicator, type=DebateAdjudicator.TYPE_CHAIR)
        panel_ids = set(self.round.preformedpanel_set.values_list('id', flat=True))

        msg, level = self.create_preformed_panels()

        self.assertEqual(level, 'success')
        self.assertIn("refreshed the brackets and liveness", msg)
        self.assertNotIn("new preformed panel", msg)
        self.assertEqual(set(self.round.preformedpanel_set.values_list('id', flat=True)), panel_ids)
        self.assertPanelsMatchAnticipatedDraw()

        panel.refresh_from_db()
        self.assertEqual(panel.importance, 2)
        self.assertEqual(list(panel.preformedpaneladjudicator_set.values_list('adjudicator', 'type')),
            [(adjudicator.id, DebateAdjudicator.TYPE_CHAIR)])

    def test_refresh_creates_missing_panels(self):
        update_or_create_preformed_panels(self.round)
        self.round.preformedpanel_set.get(room_rank=len(self.anticipated)).delete()

        msg, level = self.create_preformed_panels()

        self.assertEqual(level, 'success')
        self.assertIn("refreshed the brackets and liveness", msg)
        self.assertIn("1 new preformed panel was also created.", msg)
        self.assertEqual(self.round.preformedpanel_set.count(), len(self.anticipated))
        self.assertPanelsMatchAnticipatedDraw()

    def test_update_or_create_returns_number_created(self):
        self.assertEqual(update_or_create_preformed_panels(self.round), len(self.anticipated))
        self.round.preformedpanel_set.filter(room_rank__lte=2).delete()
        self.assertEqual(update_or_create_preformed_panels(self.round), 2)
        self.assertEqual(update_or_create_preformed_panels(self.round), 0)
