from django.test import TestCase

from draw.models import Debate, DebateTeam
from draw.types import DebateSide
from participants.models import Speaker, Team
from results.models import BallotSubmission, SpeakerScore
from tournaments.models import Round, Tournament

from ..speakers import SpeakerStandingsGenerator


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
