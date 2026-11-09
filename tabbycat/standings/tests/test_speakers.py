from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from draw.models import Debate, DebateTeam
from draw.types import DebateSide
from participants.models import Speaker, Team
from results.models import BallotSubmission, SpeakerScore
from tournaments.models import Round, Tournament

from ..speakers import SpeakerStandingsGenerator
from ..views import BaseReplyStandingsView


class TestSpeakerScoreRounding(TestCase):

    def setUp(self):
        self.tournament = Tournament.objects.create(slug='speaker-rounding', name='Speaker rounding')
        self.speakers = []
        for i in range(2):
            team = Team.objects.create(tournament=self.tournament, reference=str(i))
            self.speakers.append(Speaker.objects.create(team=team, name=str(i)))

    def add_scores(self, scores, position=1):
        for seq, pair in enumerate(zip(*scores), start=1):
            rd = Round.objects.create(tournament=self.tournament, seq=seq, schedule_group=seq)
            debate = Debate.objects.create(round=rd)
            ballot = BallotSubmission.objects.create(debate=debate, confirmed=True)
            for speaker, score, side in zip(self.speakers, pair, (DebateSide.AFF, DebateSide.NEG)):
                dt = DebateTeam.objects.create(debate=debate, team=speaker.team, side=side)
                SpeakerScore.objects.create(
                    debate_team=dt, ballot_submission=ballot, speaker=speaker, position=position, score=score,
                )

    def standings(self, metric):
        generator = SpeakerStandingsGenerator((metric,), ('rank',))
        round = Round.objects.filter(tournament=self.tournament).select_related('tournament').order_by('-seq').first()
        standings = generator.generate(Speaker.objects.filter(team__tournament=self.tournament), tournament=self.tournament, round=round)
        return [standings.get_standing(speaker) for speaker in self.speakers]

    def test_equal_averages_rank_together(self):
        # The same three judge scores can produce different floats depending on
        # their addition order, despite having exactly the same rational average.
        first = (75.0 + 75.2 + 75.1) / 3
        second = (75.2 + 75.1 + 75.0) / 3
        self.assertNotEqual(first, second)
        self.add_scores([[first] * 4, [second] * 4])
        for metric in ('total', 'average', 'trimmed_mean', 'stdev'):
            with self.subTest(metric=metric):
                standings = self.standings(metric)
                self.assertEqual(standings[0].metrics[metric], standings[1].metrics[metric])
                for standing in standings:
                    self.assertEqual(standing.rankings['rank'], (1, True))

    def test_reply_averages_rank_together(self):
        self.add_scores([[40.1, 40.1], [40.1 + 1e-12, 40.1 + 1e-12]],
            position=self.tournament.reply_position)
        for metric in ('replies_sum', 'replies_avg', 'replies_stddev'):
            with self.subTest(metric=metric):
                for standing in self.standings(metric):
                    self.assertEqual(standing.rankings['rank'], (1, True))

    def test_differences_smaller_than_display_precision_are_preserved(self):
        self.add_scores([[75] * 10, [75] * 9 + [sum([75, 75, 75.1]) / 3]])
        standings = self.standings('average')
        self.assertEqual(format(standings[0].metrics['average'], '.2f'),
            format(standings[1].metrics['average'], '.2f'))
        self.assertEqual(standings[0].rankings['rank'], (2, False))
        self.assertEqual(standings[1].rankings['rank'], (1, False))

    def test_trimmed_mean_rounds_only_after_arithmetic(self):
        self.add_scores([[70, 75 + 1/3, 76 + 1/3, 80], [70, 75, 76, 80]])
        standings = self.standings('trimmed_mean')
        self.assertEqual(standings[0].metrics['trimmed_mean'], 75.833333)


class TestReplyStandingsQueries(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.tournament = Tournament.objects.create(slug='reply-queries', name='Reply queries')
        cls.speakers = []
        for name in ('Replies', 'Ghost', 'Substantive', 'Future'):
            team = Team.objects.create(tournament=cls.tournament, reference=name)
            cls.speakers.append(Speaker.objects.create(team=team, name=name))
        cls.rounds = [Round.objects.create(tournament=cls.tournament, seq=seq, schedule_group=seq)
                      for seq in range(1, 5)]
        cls.rounds[3].stage = Round.Stage.ELIMINATION
        cls.rounds[3].save()
        for rd in cls.rounds:
            debate = Debate.objects.create(round=rd)
            ballot = BallotSubmission.objects.create(debate=debate, confirmed=True)
            for speaker in cls.speakers:
                DebateTeam.objects.create(debate=debate, team=speaker.team, side=DebateSide.AFF)
            cls.add_score(cls.speakers[0], ballot, 99, position=1)
            cls.add_score(cls.speakers[0], ballot, 40 + 2 * (rd.seq - 1))
        cls.add_score(cls.speakers[1], BallotSubmission.objects.get(debate__round=cls.rounds[0]), 49, ghost=True)
        cls.add_score(cls.speakers[2], BallotSubmission.objects.get(debate__round=cls.rounds[0]), 75, position=1)
        cls.add_score(cls.speakers[3], BallotSubmission.objects.get(debate__round=cls.rounds[2]), 48)
        unconfirmed = BallotSubmission.objects.create(
            debate=Debate.objects.get(round=cls.rounds[0]), confirmed=False, version=2)
        cls.add_score(cls.speakers[0], unconfirmed, 50)

    @classmethod
    def add_score(cls, speaker, ballot, score, position=None, **kwargs):
        return SpeakerScore.objects.create(
            speaker=speaker, ballot_submission=ballot,
            debate_team=DebateTeam.objects.get(debate=ballot.debate, team=speaker.team),
            score=score, position=cls.tournament.reply_position if position is None else position,
            **kwargs,
        )

    def reply_speakers(self):
        view = BaseReplyStandingsView()
        view._tournament_from_url = self.tournament
        return view.get_speakers()

    def test_reply_metrics_execute_once_and_keep_speakers_without_qualifying_scores(self):
        generator = SpeakerStandingsGenerator(
            ('replies_avg',), ('rank',), ('replies_stddev', 'replies_count'),
            rank_filter=('replies_count', 2),
        )
        with CaptureQueriesContext(connection) as queries:
            standings = generator.generate(self.reply_speakers(), tournament=self.tournament, round=self.rounds[1])
        ranking_queries = [q['sql'] for q in queries if 'RANK() OVER' in q['sql']]
        self.assertEqual(len(ranking_queries), 1)
        self.assertNotIn('SELECT DISTINCT', ranking_queries[0])
        self.assertEqual(set(standings.infos), {self.speakers[i] for i in (0, 1, 3)})
        first = standings.get_standing(self.speakers[0])
        self.assertEqual(first.metrics, {'replies_avg': 41, 'replies_stddev': 1, 'replies_count': 2})
        self.assertEqual(first.rankings['rank'], (1, False))
        for speaker in (self.speakers[1], self.speakers[3]):
            self.assertEqual(standings.get_standing(speaker).metrics,
                             {'replies_avg': None, 'replies_stddev': None, 'replies_count': 0})

    def test_mixed_metrics_share_scores_without_multiplying_rows(self):
        generator = SpeakerStandingsGenerator(
            ('average',), ('rank',), ('count', 'replies_avg', 'replies_count', 'trimmed_mean', 'srank'),
        )
        standings = generator.generate(self.reply_speakers(), tournament=self.tournament, round=self.rounds[3])
        metrics = standings.get_standing(self.speakers[0]).metrics
        self.assertEqual(metrics['average'], 99)
        self.assertEqual(metrics['trimmed_mean'], 99)
        self.assertEqual(metrics['count'], 3)
        self.assertEqual(metrics['replies_avg'], 42)
        self.assertEqual(metrics['replies_count'], 3)

    def test_selection_by_round_does_not_restrict_metric_rounds(self):
        speakers = self.reply_speakers().filter(speakerscore__debate_team__debate__round=self.rounds[1])
        generator = SpeakerStandingsGenerator(('replies_avg',), ('rank',), ('replies_count',))
        standings = generator.generate(speakers, tournament=self.tournament, round=self.rounds[1])
        self.assertEqual(standings.get_standing(self.speakers[0]).metrics,
                         {'replies_avg': 41, 'replies_count': 2})
