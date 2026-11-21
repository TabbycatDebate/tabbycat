import json

from django.contrib.auth import get_user_model
from django.test import TestCase

from adjallocation.models import AdjudicatorTeamConflict
from draw.dbutils import delete_round_draw
from draw.models import DebateTeam, TeamSideAllocation
from draw.utils import opposite_side
from tournaments.models import Round
from utils.misc import reverse_tournament
from utils.tests import AdminTournamentViewSimpleLoadTestMixin, CompletedTournamentTestMixin, ConditionalTableViewTestsMixin, TableViewTestsMixin


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


class PublicDrawDetailsViewPermissionTest(ConditionalTableViewTestsMixin, TestCase):
    """Checks the preference enabling/disabling the public draw details pages"""
    view_name = 'draw-public-details'
    view_toggle_preference = 'tab_release__draw_details_released'
    round_seq = 2

    def expected_row_counts(self):
        return [self.round.debate_set.count()]


class BasePublicDrawDetailsTest(CompletedTournamentTestMixin, TableViewTestsMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.tournament.preferences['tab_release__draw_details_released'] = True

    def get_header_keys(self, response):
        return [str(header['key']) for header in self.get_table_data(response)[0]['head']]

    def get_column_texts(self, response, key):
        table = self.get_table_data(response)[0]
        index = self.get_header_keys(response).index(key)
        return [str(row[index]['text']) for row in table['data']]


class PublicDrawDetailsTest(BasePublicDrawDetailsTest):
    """Tests the public draw details page in preliminary rounds."""

    round_seq = 2

    def test_unreleased(self):
        self.round.draw_status = Round.Status.CONFIRMED
        self.round.save()

        response = self.get_response('draw-public-details')
        self.assertResponseOK(response)
        self.assertTemplateUsed(response, 'draw_not_released.html')
        self.assertNoTables(response)

    def test_teams_released(self):
        self.round.draw_status = Round.Status.TEAMS_RELEASED
        self.round.save()

        response = self.get_response('draw-public-details')
        self.assertResponseTableRowCountsEqual(response, [self.round.debate_set.count()])

    def test_details_columns(self):
        response = self.get_response('draw-public-details')
        keys = self.get_header_keys(response)

        self.assertEqual(keys[0], 'bracket')
        self.assertTrue(any(key.endswith('<br>SH') for key in keys))  # side history
        self.assertIn('conflags', keys)
        self.assertNotIn('adjudicators', keys)

    def test_first_round(self):
        response = self.get_response('draw-public-details', round_seq=1)
        round1 = self.tournament.round_set.get(seq=1)
        self.assertResponseTableRowCountsEqual(response, [round1.debate_set.count()])

    def test_adjudicator_conflicts_not_shown(self):
        debate = self.round.debate_set.filter(debateadjudicator__isnull=False).first()
        adjudicator = debate.debateadjudicator_set.first().adjudicator
        team = debate.debateteam_set.first().team
        AdjudicatorTeamConflict.objects.create(adjudicator=adjudicator, team=team)

        user, _ = get_user_model().objects.get_or_create(username='test_admin', is_superuser=True)
        self.client.force_login(user)
        admin_response = self.client.get(self.reverse_url('draw-details'))
        self.assertTrue(any("Conflict:" in text for text in self.get_column_texts(admin_response, 'conflags')))

        self.client.logout()
        response = self.get_response('draw-public-details')
        self.assertFalse(any("Conflict:" in text for text in self.get_column_texts(response, 'conflags')))

    def test_institution_clash_hidden_by_code_names(self):
        self.tournament.preferences['draw_rules__avoid_same_institution'] = True
        debate = self.round.debate_set.first()
        team1, team2 = [dt.team for dt in debate.debateteam_set.all()]
        team2.institution = team1.institution
        team2.save()

        response = self.get_response('draw-public-details')
        self.assertTrue(any("same institution" in text for text in self.get_column_texts(response, 'conflags')))

        self.tournament.preferences['ui_options__team_code_names'] = 'everywhere'
        response = self.get_response('draw-public-details')
        self.assertFalse(any("same institution" in text for text in self.get_column_texts(response, 'conflags')))

    def test_listed_on_public_index(self):
        self.tournament.round_set.update(draw_status=Round.Status.CONFIRMED)
        self.round.draw_status = Round.Status.RELEASED
        self.round.save()

        response = self.client.get(reverse_tournament('tournament-public-index', self.tournament))
        self.assertContains(response, "Draw Details for {}".format(self.round.name))
        # Once in the navigation bar and once in the index
        self.assertContains(response, self.reverse_url('draw-public-details'), count=2)
        self.assertNotContains(response, self.reverse_url('draw-public-details', round_seq=1))


class PublicDrawDetailsEliminationTest(BasePublicDrawDetailsTest):
    """Tests the public draw details page in elimination rounds."""

    fixtures = ['before_oqf_ssf.json']

    def test_break_rank_columns(self):
        oqf = self.tournament.round_set.get(abbreviation='OQF')
        oqf.draw_status = Round.Status.RELEASED
        oqf.save()

        response = self.get_response('draw-public-details', round_seq=oqf.seq)
        self.assertResponseTableRowCountsEqual(response, [oqf.debate_set.count()])
        keys = self.get_header_keys(response)
        self.assertEqual(keys[0], 'room-rank')
        self.assertTrue(any(key.endswith('<br>BR') for key in keys))  # break rank


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
        target_index = headers.index(f'round_{self.target_round.id}')
        source_index = headers.index(f'round_{self.source_round.id}')

        target_cell = table['data'][0][target_index]
        source_cell = table['data'][0][source_index]

        self.assertEqual(target_cell.get('component'), 'ajax-select-cell')
        self.assertNotEqual(source_cell.get('component'), 'ajax-select-cell')

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

    def test_bulk_apply_side(self):
        source_sides = self._source_sides()
        self.assertTrue(source_sides)  # sanity check the fixture actually has data here
        teams_in_debate = self.tournament.pref('teams_in_debate')

        for direction in ('same', 'opposite'):
            with self.subTest(direction=direction):
                response = self.client.post(self.reverse_url('draw-side-allocations-bulk'), data={
                    'target_round_id': self.target_round.id,
                    'source_round_id': self.source_round.id,
                    'direction': direction,
                })
                self.assertEqual(response.status_code, 302)

                for team_id, side in source_sides.items():
                    expected = opposite_side(side, teams_in_debate) if direction == 'opposite' else side
                    self.assertEqual(
                        TeamSideAllocation.objects.get(round=self.target_round, team_id=team_id).side,
                        expected,
                    )

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

    def _add_further_undrawn_round(self):
        """Adds another preliminary round (no draw yet) after round 4, so the
        destination-round picker has more than one choice to select between.
        Uses seq=11 since the after_round_4 fixture already has elimination
        rounds occupying seq 5-10."""
        return Round.objects.create(
            tournament=self.tournament, seq=11, name="Round 5", abbreviation="R5",
            stage=Round.Stage.PRELIMINARY, draw_type=Round.DrawType.POWERPAIRED,
        )

    def test_bulk_apply_can_target_a_further_undrawn_round(self):
        round5 = self._add_further_undrawn_round()
        source_sides = self._source_sides()

        response = self.client.get(self.reverse_url('draw-side-allocations'))
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(
            [r.id for r in response.context['target_round_choices']],
            [self.target_round.id, round5.id])

        response = self.client.post(self.reverse_url('draw-side-allocations-bulk'), data={
            'target_round_id': round5.id,
            'source_round_id': self.source_round.id,
            'direction': 'same',
        })
        self.assertEqual(response.status_code, 302)

        for team_id, side in source_sides.items():
            self.assertEqual(
                TeamSideAllocation.objects.get(round=round5, team_id=team_id).side, side)
        # The immediately-next round (round 4) must be untouched.
        self.assertFalse(TeamSideAllocation.objects.filter(round=self.target_round).exists())
