from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from draw.generator import DrawUserError
from draw.manager import BaseDrawManager, RoundRobinDrawManager


class RoundRobinSeedValidationTests(SimpleTestCase):
    def test_missing_seed_rejected_before_draw_creation(self):
        for teams_in_debate in (2, 4):
            for unseeded_count in (1, 2):
                with self.subTest(teams_in_debate=teams_in_debate, unseeded_count=unseeded_count):
                    round = Mock()
                    round.tournament.pref.return_value = teams_in_debate
                    manager = RoundRobinDrawManager(round)
                    seeded = SimpleNamespace(seed=1)
                    unseeded = SimpleNamespace(seed=None)
                    teams = ([seeded] + [unseeded] * unseeded_count, [])
                    with patch.object(BaseDrawManager, 'get_teams', return_value=teams), \
                            patch.object(BaseDrawManager, 'create') as create:
                        with self.assertRaisesMessage(DrawUserError, 'Every team must have a seed set'):
                            manager.create()
                        create.assert_not_called()

    def test_seeded_competitors_allow_unseeded_bye(self):
        for teams_in_debate in (2, 4):
            with self.subTest(teams_in_debate=teams_in_debate):
                round = Mock()
                round.tournament.pref.return_value = teams_in_debate
                manager = RoundRobinDrawManager(round)
                teams = ([SimpleNamespace(seed=1)], [SimpleNamespace(seed=None)])
                options = {}
                with patch.object(BaseDrawManager, 'get_teams', return_value=teams), \
                        patch.object(BaseDrawManager, 'create', return_value=[]) as create:
                    self.assertEqual(manager.create(options), [])
                    create.assert_called_once_with(options)

    def test_unseeded_bye_debate_creation(self):
        round = Mock()
        round.tournament.pref.return_value = 'off'
        manager = RoundRobinDrawManager(round)
        bye = SimpleNamespace(seed=None)
        with patch('draw.manager.Debate') as debate, patch('draw.manager.DebateTeam') as debate_team:
            self.assertEqual(manager._make_bye_debates([bye], 1), [debate.return_value])
            self.assertIs(debate_team.call_args.kwargs['team'], bye)
            debate.return_value.save.assert_called_once()
            debate_team.return_value.save.assert_called_once()
