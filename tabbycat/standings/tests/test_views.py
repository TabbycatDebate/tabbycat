import json
import logging

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import resolve

from breakqual.models import BreakCategory
from draw.models import Debate, DebateTeam
from participants.models import SpeakerCategory, Team
from results.models import BallotSubmission, TeamScore
from tournaments.models import Round, Tournament
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

    def get_table(self, view_name, **kwargs):
        url = reverse_tournament(view_name, self.tournament, kwargs={'round_seq': self.round.seq, **kwargs})
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

    def test_category_ranks_apply_who_beat_whom_independently(self):
        self.tournament = Tournament.objects.create(name="Category WBW", slug="category-wbw")
        self.tournament.preferences['standings__team_standings_precedence'] = ['wins', 'wbw', 'speaks_sum']
        teams = [
            Team.objects.create(tournament=self.tournament, reference=name, use_institution_prefix=False)
            for name in ('A', 'B', 'C')
        ]
        category = BreakCategory.objects.create(
            tournament=self.tournament, name="Category", slug="category", seq=1,
            break_size=0, is_general=False, priority=1,
        )
        category.team_set.add(*teams[:2])

        # Each team wins once, but only A and B are category members. WBW is
        # skipped for the global three-way tie and resolves the category tie.
        for seq, (winner, loser) in enumerate(((0, 1), (1, 2), (2, 0)), start=1):
            self.round = Round.objects.create(tournament=self.tournament, seq=seq)
            debate = Debate.objects.create(round=self.round)
            ballot = BallotSubmission.objects.create(debate=debate, confirmed=True)
            for side, index in enumerate((winner, loser)):
                debate_team = DebateTeam.objects.create(debate=debate, team=teams[index], side=side)
                TeamScore.objects.create(
                    debate_team=debate_team, ballot_submission=ballot,
                    win=index == winner, points=int(index == winner), score=(200, 210, 190)[index],
                )
        self.tournament.current_round = self.round
        self.tournament.save()

        combined = self.get_table('standings-team-categories')
        individual = self.get_table('standings-break-category', category=category.slug)

        def rankings_by_team(table, key):
            columns = {header['key']: i for i, header in enumerate(table['head'])}
            return {row[columns['team']]['text']: row[columns[key]]['text'] for row in table['data']}

        self.assertEqual(rankings_by_team(combined, 'Rk'), {'B': '1', 'A': '2', 'C': '3'})
        category_rankings = rankings_by_team(combined, 'category-category')
        self.assertEqual(category_rankings, {'B': '2', 'A': '1', 'C': ''})
        self.assertEqual(
            {team: rank for team, rank in category_rankings.items() if rank},
            rankings_by_team(individual, 'Rk'),
        )


class CategoryStandingsURLTest(TestCase):

    def test_category_slug_does_not_collide_with_overview(self):
        tournament = Tournament.objects.create(name="Category URLs", slug="category-urls")
        for category_view, overview_view in (
            ('standings-break-category', 'standings-team-categories'),
            ('standings-speaker-category', 'standings-speaker-categories'),
        ):
            with self.subTest(view=category_view):
                category_url = reverse_tournament(category_view, tournament, kwargs={'round_seq': 1, 'category': 'categories'})
                overview_url = reverse_tournament(overview_view, tournament, kwargs={'round_seq': 1})
                self.assertEqual(resolve(category_url).url_name, category_view)
                self.assertEqual(resolve(overview_url).url_name, overview_view)
