import json
import logging

from django.contrib.auth import get_user_model
from django.test import TestCase

from breakqual.models import BreakCategory
from participants.models import SpeakerCategory
from tournaments.models import Tournament
from utils.misc import reverse_tournament
from utils.tests import ConditionalTournamentViewSimpleLoadTestMixin, suppress_logs


class PublicStandingsTestMixin(ConditionalTournamentViewSimpleLoadTestMixin):
    """Suppresses standings logging output."""

    def test_view_enabled(self):
        with suppress_logs('standings.metrics', logging.INFO):
            super().test_view_enabled()


class PublicTeamStandingsViewTest(ConditionalTournamentViewSimpleLoadTestMixin, TestCase):
    view_name = 'standings-public-teams-current'
    view_toggle_preference = 'public_features__public_team_standings'


class PublicTeamTabViewTest(PublicStandingsTestMixin, TestCase):
    view_name = 'standings-public-tab-team'
    view_toggle_preference = 'tab_release__team_tab_released'


class PublicSpeakerTabViewTest(PublicStandingsTestMixin, TestCase):
    view_name = 'standings-public-tab-speaker'
    view_toggle_preference = 'tab_release__speaker_tab_released'


class PublicRepliesTabViewTest(PublicStandingsTestMixin, TestCase):
    view_name = 'standings-public-tab-replies'
    view_toggle_preference = 'tab_release__replies_tab_released'


class PublicAdjudicatorTabViewTest(ConditionalTournamentViewSimpleLoadTestMixin, TestCase):
    view_name = 'standings-public-adjudicators-tab'
    view_toggle_preference = 'tab_release__adjudicators_tab_released'


class PublicDiversityViewTest(ConditionalTournamentViewSimpleLoadTestMixin, TestCase):
    view_name = 'standings-public-diversity'
    view_toggle_preference = 'public_features__public_diversity'


class CategoryRankStandingsViewTest(TestCase):
    fixtures = ['after_round_4.json']

    def setUp(self):
        self.tournament = Tournament.objects.first()
        self.round = self.tournament.round_set.get(seq=4)
        user = get_user_model().objects.create(username='category-rank-admin', is_superuser=True)
        self.client.force_login(user)

    def get_table(self, view_name):
        url = reverse_tournament(view_name, self.tournament, kwargs={'round_seq': self.round.seq})
        with suppress_logs('standings.metrics', logging.INFO):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        return json.loads(response.context['tables_data'])[0]

    def assert_single_category_member(self, table, column_key):
        column_index = next(i for i, header in enumerate(table['head']) if header['key'] == column_key)
        cells = [row[column_index]['text'] for row in table['data']]
        self.assertEqual(sum(bool(cell) for cell in cells), 1)
        self.assertEqual(sum(not cell for cell in cells), len(cells) - 1)

    def test_team_category_rank_columns(self):
        category = BreakCategory.objects.create(
            tournament=self.tournament,
            name="No-break category",
            slug="no-break",
            seq=100,
            break_size=0,
            is_general=False,
            priority=1,
        )
        category.team_set.add(self.tournament.team_set.first())

        table = self.get_table('standings-team-categories')

        self.assert_single_category_member(table, 'category-no-break')

    def test_speaker_category_rank_columns(self):
        category = SpeakerCategory.objects.create(
            tournament=self.tournament,
            name="Test category",
            slug="test-category",
            seq=100,
        )
        category.speaker_set.add(self.tournament.team_set.first().speaker_set.first())

        table = self.get_table('standings-speaker-categories')

        self.assert_single_category_member(table, 'category-test-category')
