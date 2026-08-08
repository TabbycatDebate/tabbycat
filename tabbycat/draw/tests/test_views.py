import json

from django.contrib.auth import get_user_model
from django.test import TestCase

from tournaments.models import Round
from utils.misc import reverse_tournament
from utils.tests import AdminTournamentViewSimpleLoadTestMixin, CompletedTournamentTestMixin, ConditionalTableViewTestsMixin, TableViewTestsMixin

from draw.dbutils import delete_round_draw
from draw.models import DebateTeam, TeamSideAllocation
from draw.utils import opposite_side


class PublicDrawForSpecificRoundViewPermissionTest(ConditionalTableViewTestsMixin, TestCase):
    """Checks the preference enabling/disabling showing round by specific"""
    view_name = 'draw-public-for-round'
    view_toggle_preference = 'public_features__public_draw'
    view_toggle_on_value = 'all-released'
    view_toggle_off_values = ['current', 'off']
    round_seq = 2

    def expected_row_counts(self):
        return [self.round.debate_set.count()]


class PublicDrawForCurrentRoundViewPermissionTest(ConditionalTableViewTestsMixin, TestCase):
    """ Check that the current round can have its draw seen if enabled"""
    view_name = 'draw-public-current-rounds'
    view_toggle_preference = 'public_features__public_draw'
    view_toggle_on_value = 'current'
    view_toggle_off_values = ['all-released', 'off']

    def setUp(self):
        super().setUp()
        seq = 3
        self.tournament.round_set.filter(seq__lt=seq).update(completed=True)
        self.tournament.round_set.filter(seq__gte=seq).update(completed=False)
        self.round = self.tournament.round_set.get(seq=seq)
        self.round.draw_status = Round.Status.RELEASED
        self.round.save()

    def expected_row_counts(self):
        return [self.round.debate_set.count()]


class PublicDrawSpecificRoundTest(CompletedTournamentTestMixin, TableViewTestsMixin, TestCase):
    """Tests that the specific-round draw page responds to draw release."""

    round_seq = 2

    def setUp(self):
        super().setUp()
        self.tournament.preferences['public_features__public_draw'] = 'all-released'

    def test_unreleased(self):
        self.round.draw_status = Round.Status.CONFIRMED
        self.round.save()

        response = self.get_response('draw-public-for-round')
        self.assertResponseOK(response)
        self.assertNoTables(response)

    def test_released(self):
        self.round.draw_status = Round.Status.RELEASED
        self.round.save()

        response = self.get_response('draw-public-for-round')
        count = self.round.debate_set.count()
        self.assertResponseTableRowCountsEqual(response, [count])

    def test_teams_released(self):
        self.round.draw_status = Round.Status.TEAMS_RELEASED
        self.round.save()

        response = self.get_response('draw-public-for-round')
        count = self.round.debate_set.count()
        self.assertResponseTableRowCountsEqual(response, [count])

    def test_teams_released_lists(self):
        self.tournament.round_set.update(draw_status=Round.Status.CONFIRMED)
        self.round.draw_status = Round.Status.TEAMS_RELEASED
        self.round.save()

        response = self.client.get(reverse_tournament('tournament-public-index', self.tournament))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Draw for {}".format(self.round.name))
        self.assertContains(response, self.reverse_url('draw-public-for-round'), count=2)


class PublicDrawPreliminaryCurrentRoundTest(CompletedTournamentTestMixin, TableViewTestsMixin, TestCase):
    """Tests the single-round current round page, which appears during the
    preliminary rounds, and how it responds to draw release."""

    def setUp(self):
        super().setUp()
        self.tournament.preferences['public_features__public_draw'] = 'current'
        seq = 3
        self.tournament.round_set.filter(seq__lt=seq).update(completed=True)
        self.tournament.round_set.filter(seq__gte=seq).update(completed=False)
        self.round = self.tournament.round_set.get(seq=seq)
        self.round.draw_status = Round.Status.RELEASED
        self.round.save()

    def test_unreleased(self):
        self.round.draw_status = Round.Status.CONFIRMED
        self.round.save()

        response = self.get_response('draw-public-current-rounds')
        self.assertResponseOK(response)
        self.assertNoTables(response)

    def test_released(self):
        self.round.draw_status = Round.Status.RELEASED
        self.round.save()

        response = self.get_response('draw-public-current-rounds')
        count = self.round.debate_set.count()
        self.assertResponseTableRowCountsEqual(response, [count])

        # Check that it is actually the Round 3 draw with a quick spot check
        data = self.get_table_data(response)
        self.assertEqual(len(data), 1)
        table = data[0]

        keys = [c['key'] for c in table['head']]
        venue_column_index = keys.index('venue')
        aff_column_index = keys.index('0')
        neg_column_index = keys.index('1')

        venues = [c[venue_column_index]['text'] for c in table['data']]
        pairings = [
            ('K06', 'Stanford 3', 'Harvard 1'),
            ('Z10', 'MIT 1', 'Harvard 2'),
            ('4 K05', 'Johns Hopkins 1', 'Chicago 1'),
        ]
        for venue, aff, neg in pairings:
            row_index = venues.index(venue)
            row = table['data'][row_index]
            self.assertEqual(row[aff_column_index]['text'], aff)
            self.assertEqual(row[neg_column_index]['text'], neg)


class PublicDrawEliminationCurrentRoundTest(CompletedTournamentTestMixin, TableViewTestsMixin, TestCase):
    """Tests the multi-round current round page, which appears when there are
    simultaneous elimination rounds, and how it responds to draw release."""

    fixtures = ['before_oqf_ssf.json']

    def setUp(self):
        super().setUp()
        self.tournament.preferences['public_features__public_draw'] = 'current'
        self.tournament.prelim_rounds().update(completed=True)
        self.tournament.break_rounds().update(completed=False)

        self.oqf = self.tournament.round_set.get(abbreviation='OQF')
        self.ssf = self.tournament.round_set.get(abbreviation='SSF')
        self.ngf = self.tournament.round_set.get(abbreviation='NGF')

    def test_unreleased(self):
        self.oqf.draw_status = Round.Status.CONFIRMED
        self.oqf.save()
        self.ssf.draw_status = Round.Status.CONFIRMED
        self.ssf.save()

        response = self.get_response('draw-public-current-rounds')
        self.assertResponseOK(response)
        self.assertNoTables(response)

    def test_one_released(self):
        self.oqf.draw_status = Round.Status.RELEASED
        self.oqf.save()
        self.ssf.draw_status = Round.Status.CONFIRMED
        self.ssf.save()

        response = self.get_response('draw-public-current-rounds')
        self.assertResponseTableRowCountsEqual(response, [4, 0], allow_vacuous=True)

    def test_both_released(self):
        self.oqf.draw_status = Round.Status.RELEASED
        self.oqf.save()
        self.ssf.draw_status = Round.Status.RELEASED
        self.ssf.save()

        response = self.get_response('draw-public-current-rounds')
        self.assertResponseTableRowCountsEqual(response, [4, 2])

    def test_all_three_released(self):
        self.oqf.draw_status = Round.Status.RELEASED
        self.oqf.save()
        self.ssf.draw_status = Round.Status.RELEASED
        self.ssf.save()
        self.ngf.draw_status = Round.Status.RELEASED
        self.ngf.save()

        # Create a Novice Grand Final to check that the table will appear
        ngf_debate = self.ngf.debate_set.create()
        aff = self.tournament.team_set.get(id=4)
        neg = self.tournament.team_set.get(id=6)
        ngf_debate.debateteam_set.create(team=aff, side=0)
        ngf_debate.debateteam_set.create(team=neg, side=1)

        response = self.get_response('draw-public-current-rounds')
        self.assertResponseTableRowCountsEqual(response, [4, 2, 1])


class EditDebateTeamsViewTest(AdminTournamentViewSimpleLoadTestMixin, TestCase):
    view_name = 'edit-debate-teams'
    round_seq = 1


class SideAllocationsEditingTest(CompletedTournamentTestMixin, TestCase):
    """Tests the editable side pre-allocation matrix and its two update
    endpoints ("Side Locks"). In the after_round_4 fixture, rounds 1-4 all
    already have a generated draw, so round 4 is reset here (its draw
    deleted) to simulate the "next round, not yet drawn" state that the
    editable column and the bulk-apply tool both target."""

    def setUp(self):
        super().setUp()
        self.target_round = self.tournament.round_set.get(seq=4)
        delete_round_draw(self.target_round)
        self.source_round = self.tournament.round_set.get(seq=3)

        self.admin = get_user_model().objects.create(username='side_locks_admin', is_superuser=True)
        self.client.force_login(self.admin)

    def reverse_url(self, name):
        return reverse_tournament(name, self.tournament)

    def test_table_shows_editable_cell_for_undrawn_round(self):
        response = self.client.get(self.reverse_url('draw-side-allocations'))
        self.assertEqual(response.status_code, 200)
        tables = json.loads(response.context['tables_data'])
        table = tables[0]

        headers = [h['key'] for h in table['head']]
        target_index = headers.index(self.target_round.abbreviation)
        source_index = headers.index(self.source_round.abbreviation)

        target_cell = table['data'][0][target_index]
        source_cell = table['data'][0][source_index]

        self.assertEqual(target_cell.get('component'), 'side-cell')
        self.assertNotEqual(source_cell.get('component'), 'side-cell')

    def test_update_single_preallocation_set_and_clear(self):
        team = self.tournament.team_set.first()
        url = self.reverse_url('draw-side-allocations-update')

        response = self.client.post(url, data=json.dumps({
            'team_id': team.id, 'round_id': self.target_round.id, 'side': 0,
        }), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            TeamSideAllocation.objects.get(round=self.target_round, team=team).side, 0)

        response = self.client.post(url, data=json.dumps({
            'team_id': team.id, 'round_id': self.target_round.id, 'side': None,
        }), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            TeamSideAllocation.objects.filter(round=self.target_round, team=team).exists())

    def test_update_rejected_for_already_drawn_round(self):
        team = self.tournament.team_set.first()
        drawn_round = self.tournament.round_set.get(seq=1)
        url = self.reverse_url('draw-side-allocations-update')

        response = self.client.post(url, data=json.dumps({
            'team_id': team.id, 'round_id': drawn_round.id, 'side': 0,
        }), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertFalse(
            TeamSideAllocation.objects.filter(round=drawn_round, team=team).exists())

    def _source_sides(self):
        return dict(DebateTeam.objects.filter(
            debate__round=self.source_round).values_list('team_id', 'side'))

    def test_bulk_apply_same_side(self):
        source_sides = self._source_sides()
        self.assertTrue(source_sides)  # sanity check the fixture actually has data here

        response = self.client.post(self.reverse_url('draw-side-allocations-bulk'), data={
            'target_round_id': self.target_round.id,
            'source_round_id': self.source_round.id,
            'direction': 'same',
        })
        self.assertEqual(response.status_code, 302)

        for team_id, side in source_sides.items():
            self.assertEqual(
                TeamSideAllocation.objects.get(round=self.target_round, team_id=team_id).side, side)

    def test_bulk_apply_opposite_side(self):
        source_sides = self._source_sides()
        teams_in_debate = self.tournament.pref('teams_in_debate')

        response = self.client.post(self.reverse_url('draw-side-allocations-bulk'), data={
            'target_round_id': self.target_round.id,
            'source_round_id': self.source_round.id,
            'direction': 'opposite',
        })
        self.assertEqual(response.status_code, 302)

        for team_id, side in source_sides.items():
            expected = opposite_side(side, teams_in_debate)
            self.assertEqual(
                TeamSideAllocation.objects.get(round=self.target_round, team_id=team_id).side, expected)

    def test_bulk_apply_skips_team_with_no_result_in_source_round(self):
        bye_team = self.tournament.team_set.first()
        DebateTeam.objects.filter(debate__round=self.source_round, team=bye_team).delete()

        response = self.client.post(self.reverse_url('draw-side-allocations-bulk'), data={
            'target_round_id': self.target_round.id,
            'source_round_id': self.source_round.id,
            'direction': 'same',
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            TeamSideAllocation.objects.filter(round=self.target_round, team=bye_team).exists())

    def test_bulk_apply_rejected_when_target_already_drawn(self):
        drawn_round = self.tournament.round_set.get(seq=1)

        response = self.client.post(self.reverse_url('draw-side-allocations-bulk'), data={
            'target_round_id': drawn_round.id,
            'source_round_id': self.source_round.id,
            'direction': 'same',
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(TeamSideAllocation.objects.filter(round=drawn_round).exists())

    def test_bulk_apply_rejected_when_source_round_not_finished(self):
        response = self.client.post(self.reverse_url('draw-side-allocations-bulk'), data={
            'target_round_id': self.target_round.id,
            'source_round_id': self.target_round.id,  # not finished, its own draw was just deleted
            'direction': 'same',
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(TeamSideAllocation.objects.filter(round=self.target_round).exists())
