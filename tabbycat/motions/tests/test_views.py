from django.test import TestCase

from breakqual.models import BreakCategory
from draw.models import Debate
from tournaments.models import Round, Tournament
from utils.misc import reverse_tournament
from utils.tests import ConditionalTournamentViewSimpleLoadTestMixin


class PublicMotionStatisticsViewTest(ConditionalTournamentViewSimpleLoadTestMixin, TestCase):
    view_name = 'motions-public-statistics'
    view_toggle_preference = 'tab_release__motion_tab_released'


class PublicMotionsViewTest(TestCase):

    def setUp(self):
        self.tournament = Tournament.objects.create(slug='motions')
        self.tournament.preferences['public_features__public_motions'] = True
        self.prelim = Round.objects.create(tournament=self.tournament, seq=1, completed=True)
        self.open = BreakCategory.objects.create(
            tournament=self.tournament, name='Open', slug='open', seq=1,
            break_size=8, is_general=True, priority=0)
        self.novice = BreakCategory.objects.create(
            tournament=self.tournament, name='Novice', slug='novice', seq=2,
            break_size=4, is_general=False, priority=0)
        self.open_quarter = self.create_break_round(self.open, 8)
        self.open_semi = self.create_break_round(self.open, 9)
        self.open_final = self.create_break_round(self.open, 10)
        self.novice_semi = self.create_break_round(self.novice, 13)
        self.novice_final = self.create_break_round(self.novice, 14)
        Debate.objects.create(round=self.open_quarter)
        Debate.objects.create(round=self.novice_semi)

    def create_break_round(self, category, seq):
        return Round.objects.create(
            tournament=self.tournament, seq=seq, name=f'{category.name} {seq}',
            stage=Round.Stage.ELIMINATION, break_category=category)

    def assert_visible_rounds(self, rounds):
        response = self.client.get(reverse_tournament('motions-public', self.tournament))
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(response.context['rounds'], rounds)

    def test_independent_break_progression(self):
        self.assert_visible_rounds([self.prelim, self.open_quarter, self.novice_semi])

        self.novice_semi.completed = True
        self.novice_semi.save()
        Debate.objects.create(round=self.novice_final)
        self.assert_visible_rounds([self.prelim, self.open_quarter, self.novice_semi, self.novice_final])

        self.open_quarter.completed = True
        self.open_quarter.save()
        Debate.objects.create(round=self.open_semi)
        self.assert_visible_rounds([
            self.prelim, self.open_quarter, self.open_semi, self.novice_semi, self.novice_final])

    def test_released_future_motion_is_visible(self):
        self.novice_final.motions_status = Round.MotionsStatus.MOTIONS_RELEASED
        self.novice_final.save()
        self.assert_visible_rounds([self.prelim, self.open_quarter, self.novice_semi, self.novice_final])

    def test_completed_category_stays_visible_without_exposing_other_future_rounds(self):
        self.novice.round_set.update(completed=True)
        self.assert_visible_rounds([self.prelim, self.open_quarter, self.novice_semi, self.novice_final])

    def test_parallel_preliminary_rounds(self):
        self.prelim.completed = False
        self.prelim.save()
        parallel = Round.objects.create(tournament=self.tournament, seq=2, schedule_group=1)
        Round.objects.create(tournament=self.tournament, seq=3, schedule_group=3)
        self.assert_visible_rounds([self.prelim, parallel])
