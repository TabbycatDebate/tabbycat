from django.test import TestCase

from draw.models import DebateTeam
from tournaments.models import Round
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
        self.round.draw_status = Round.STATUS_RELEASED
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
        self.round.draw_status = Round.STATUS_CONFIRMED
        self.round.save()

        response = self.get_response('draw-public-for-round')
        self.assertResponseOK(response)
        self.assertNoTables(response)

    def test_released(self):
        self.round.draw_status = Round.STATUS_RELEASED
        self.round.save()

        response = self.get_response('draw-public-for-round')
        count = self.round.debate_set.count()
        self.assertResponseTableRowCountsEqual(response, [count])


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
        self.round.draw_status = Round.STATUS_RELEASED
        self.round.save()

    def test_unreleased(self):
        self.round.draw_status = Round.STATUS_CONFIRMED
        self.round.save()

        response = self.get_response('draw-public-current-rounds')
        self.assertResponseOK(response)
        self.assertNoTables(response)

    def test_released(self):
        self.round.draw_status = Round.STATUS_RELEASED
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
        aff_column_index = keys.index('aff')
        neg_column_index = keys.index('neg')

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
        self.oqf.draw_status = Round.STATUS_CONFIRMED
        self.oqf.save()
        self.ssf.draw_status = Round.STATUS_CONFIRMED
        self.ssf.save()

        response = self.get_response('draw-public-current-rounds')
        self.assertResponseOK(response)
        self.assertNoTables(response)

    def test_one_released(self):
        self.oqf.draw_status = Round.STATUS_RELEASED
        self.oqf.save()
        self.ssf.draw_status = Round.STATUS_CONFIRMED
        self.ssf.save()

        response = self.get_response('draw-public-current-rounds')
        self.assertResponseTableRowCountsEqual(response, [4, 0], allow_vacuous=True)

    def test_both_released(self):
        self.oqf.draw_status = Round.STATUS_RELEASED
        self.oqf.save()
        self.ssf.draw_status = Round.STATUS_RELEASED
        self.ssf.save()

        response = self.get_response('draw-public-current-rounds')
        self.assertResponseTableRowCountsEqual(response, [4, 2])

    def test_all_three_released(self):
        self.oqf.draw_status = Round.STATUS_RELEASED
        self.oqf.save()
        self.ssf.draw_status = Round.STATUS_RELEASED
        self.ssf.save()
        self.ngf.draw_status = Round.STATUS_RELEASED
        self.ngf.save()

        # Create a Novice Grand Final to check that the table will appear
        ngf_debate = self.ngf.debate_set.create()
        aff = self.tournament.team_set.get(id=4)
        neg = self.tournament.team_set.get(id=6)
        ngf_debate.debateteam_set.create(team=aff, side=DebateTeam.SIDE_AFF)
        ngf_debate.debateteam_set.create(team=neg, side=DebateTeam.SIDE_NEG)

        response = self.get_response('draw-public-current-rounds')
        self.assertResponseTableRowCountsEqual(response, [4, 2, 1])


class EditDebateTeamsViewTest(AdminTournamentViewSimpleLoadTestMixin, TestCase):
    view_name = 'edit-debate-teams'
    round_seq = 1
