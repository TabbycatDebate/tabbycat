from unittest.mock import Mock

from django.test import TestCase

from draw.consumers import DebateEditConsumer
from draw.models import Debate, DebateTeam
from participants.models import Adjudicator, Team
from tournaments.models import Round, Tournament
from venues.models import Venue


class DebateEditConsumerTournamentScopeTests(TestCase):

    def setUp(self):
        self.tournament = Tournament.objects.create(name="First Tournament", slug="first")
        self.other_tournament = Tournament.objects.create(name="Second Tournament", slug="second")
        self.round = Round.objects.create(
            tournament=self.tournament, seq=1, schedule_group=1, name="Round 1",
            abbreviation="R1", draw_type=Round.DrawType.RANDOM,
        )
        self.other_round = Round.objects.create(
            tournament=self.other_tournament, seq=1, schedule_group=1, name="Round 1",
            abbreviation="R1", draw_type=Round.DrawType.RANDOM,
        )
        self.debate = Debate.objects.create(round=self.round)
        self.other_debate = Debate.objects.create(round=self.other_round)
        self.consumer = DebateEditConsumer()
        self.consumer._tournament_from_url = self.tournament
        self.consumer.round = self.round
        self.consumer.return_attributes = Mock()

    def test_debate_ids_are_limited_to_consumer_tournament(self):
        changes = {self.debate.id: {}, self.other_debate.id: {}}

        debates = self.consumer.get_debates_or_panels(changes)

        self.assertEqual(debates, [self.debate])

    def test_foreign_adjudicator_does_not_change_allocation(self):
        foreign_adjudicator = Adjudicator.objects.create(
            tournament=self.other_tournament, name="Foreign Adjudicator",
        )
        self.consumer.delete_adjudicators = Mock()
        self.consumer.create_adjudicators = Mock()
        self.consumer.adjudicators_serializer = Mock()

        self.consumer.receive_adjudicators({
            'adjudicators': [{
                'id': self.debate.id,
                'adjudicators': {'C': [foreign_adjudicator.id]},
            }],
        })

        self.consumer.delete_adjudicators.assert_not_called()
        self.consumer.create_adjudicators.assert_not_called()

    def test_foreign_team_does_not_change_debate(self):
        foreign_team = Team.objects.create(
            tournament=self.other_tournament, reference="Foreign Team",
            short_reference="Foreign Team",
        )

        self.consumer.modify_debate_teams(self.debate, [foreign_team.id, None])

        self.assertFalse(DebateTeam.objects.filter(debate=self.debate).exists())

    def test_foreign_venue_does_not_change_debate(self):
        original_venue = Venue.objects.create(
            tournament=self.tournament, name="Original", priority=1,
        )
        foreign_venue = Venue.objects.create(
            tournament=self.other_tournament, name="Foreign", priority=1,
        )
        self.debate.venue = original_venue
        self.debate.save()
        serializer = Mock()
        serializer.return_value.data = []

        self.consumer.receive_debate_change(
            {'venues': [{'id': self.debate.id, 'venue': foreign_venue.id}]},
            'venues', 'venue', 'venue_id', serializer,
        )

        self.debate.refresh_from_db()
        self.assertEqual(self.debate.venue, original_venue)


class DebateEditConsumerFlagTests(TestCase):

    def setUp(self):
        self.tournament = Tournament.objects.create(name="Flag Tests", slug="flags")
        self.round = Round.objects.create(
            tournament=self.tournament, seq=1, schedule_group=1, name="Round 1",
            abbreviation="R1", draw_type=Round.DrawType.RANDOM,
        )
        self.teams = [Team.objects.create(
            tournament=self.tournament, reference=f"Team {i}", short_reference=f"Team {i}",
        ) for i in range(3)]
        self.debate = Debate.objects.create(round=self.round, flags=['1u1d_hist'])
        DebateTeam.objects.create(debate=self.debate, side=0, team=self.teams[0], flags=['pullup'])
        DebateTeam.objects.create(debate=self.debate, side=1, team=self.teams[1], flags=['pulldown'])
        self.consumer = DebateEditConsumer()
        self.consumer._tournament_from_url = self.tournament
        self.consumer.round = self.round

    def assert_flags_cleared(self):
        self.debate.refresh_from_db()
        self.assertEqual(self.debate.flags, [])
        for debate_team in self.debate.debateteam_set.all():
            self.assertEqual(debate_team.flags, [])

    def assert_flags_preserved(self):
        self.debate.refresh_from_db()
        self.assertEqual(self.debate.flags, ['1u1d_hist'])
        self.assertEqual(self.debate.debateteam_set.get(side=0).flags, ['pullup'])
        self.assertEqual(self.debate.debateteam_set.get(side=1).flags, ['pulldown'])

    def test_replacement_does_not_inherit_pullup(self):
        self.consumer.modify_debate_teams(self.debate, [self.teams[2].id, self.teams[1].id])

        self.assertEqual(self.debate.get_team(0), self.teams[2])
        self.assert_flags_cleared()

    def test_side_swap_clears_flags(self):
        self.consumer.modify_debate_teams(self.debate, [self.teams[1].id, self.teams[0].id])

        self.assert_flags_cleared()

    def test_removal_clears_flags(self):
        self.consumer.modify_debate_teams(self.debate, [None, self.teams[1].id])

        self.assertFalse(self.debate.debateteam_set.filter(side=0).exists())
        self.assert_flags_cleared()

    def test_filling_vacant_side_clears_flags(self):
        self.debate.debateteam_set.filter(side=0).delete()
        self.consumer.modify_debate_teams(self.debate, [self.teams[2].id, self.teams[1].id])

        self.assert_flags_cleared()

    def test_unchanged_matchup_preserves_flags(self):
        self.consumer.modify_debate_teams(self.debate, [self.teams[0].id, self.teams[1].id])

        self.assert_flags_preserved()

    def test_invalid_team_preserves_flags(self):
        self.consumer.modify_debate_teams(self.debate, [-1, self.teams[1].id])

        self.assert_flags_preserved()

    def test_only_changed_debate_loses_flags(self):
        unchanged = Debate.objects.create(round=self.round, flags=['max_swapped'])
        unchanged_dt = DebateTeam.objects.create(debate=unchanged, side=0, team=self.teams[2], flags=['pullup'])
        self.consumer.return_attributes = Mock()

        self.consumer.receive_teams({'teams': [
            {'id': self.debate.id, 'teams': [self.teams[2].id, self.teams[1].id]},
            {'id': unchanged.id, 'teams': [self.teams[2].id, None]},
        ]})

        self.assert_flags_cleared()
        unchanged.refresh_from_db()
        unchanged_dt.refresh_from_db()
        self.assertEqual(unchanged.flags, ['max_swapped'])
        self.assertEqual(unchanged_dt.flags, ['pullup'])
