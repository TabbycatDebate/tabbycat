import logging

from django.core.exceptions import ValidationError
from django.test import RequestFactory, TestCase
from django.urls import reverse

from adjallocation.models import DebateAdjudicator
from draw.models import Debate, DebateTeam
from draw.types import DebateSide
from options.fields import EMPTY_CHOICE
from options.forms import tournament_preference_form_builder
from participants.models import Adjudicator, Speaker, Team
from results.models import (BallotSubmission, ScoreCriterion, SpeakerCriterionScore,
    SpeakerScore, TeamScore)
from tournaments.models import Round, Tournament
from utils.misc import reverse_tournament
from utils.tests import suppress_logs

from ..speakers import (AverageCriterionScoreMetricAnnotator, SpeakerStandingsGenerator,
    TotalCriterionScoreMetricAnnotator)
from ..views import CriterionStandingsView


class TestCriterionStandings(TestCase):
    """Tests speaker standings ranked by a single score criterion, as used for
    e.g. a 'top speakers by Style' tab in World Schools format."""

    def setUp(self):
        self.tournament = Tournament.objects.create(slug="criterionstandingstest",
            name="Criterion standings test")
        self.team1 = Team.objects.create(tournament=self.tournament, reference="1",
            use_institution_prefix=False)
        self.team2 = Team.objects.create(tournament=self.tournament, reference="2",
            use_institution_prefix=False)
        self.speaker1 = Speaker.objects.create(team=self.team1, name="Speaker 1")
        self.speaker2 = Speaker.objects.create(team=self.team2, name="Speaker 2")

        self.style = ScoreCriterion.objects.create(tournament=self.tournament, name="Style",
            seq=1, weight=1, min_score=0, max_score=40, step=1)
        self.content = ScoreCriterion.objects.create(tournament=self.tournament, name="Content",
            seq=2, weight=1, min_score=0, max_score=40, step=1)

        adj = Adjudicator.objects.create(tournament=self.tournament, name="Adjudicator")

        # Speaker 1 is the better overall speaker, but speaker 2 is better on
        # style, so the two tabs should rank them in opposite orders.
        style_scores = {self.speaker1: [30, 32], self.speaker2: [35, 37]}
        content_scores = {self.speaker1: [40, 38], self.speaker2: [20, 22]}

        for i in [1, 2]:
            rd = Round.objects.create(tournament=self.tournament, seq=i, schedule_group=i,
                completed=True)
            debate = Debate.objects.create(round=rd)
            dt1 = DebateTeam.objects.create(debate=debate, team=self.team1, side=DebateSide.AFF)
            dt2 = DebateTeam.objects.create(debate=debate, team=self.team2, side=DebateSide.NEG)
            DebateAdjudicator.objects.create(debate=debate, adjudicator=adj,
                type=DebateAdjudicator.TYPE_CHAIR)
            ballotsub = BallotSubmission.objects.create(debate=debate, confirmed=True)
            TeamScore.objects.create(debate_team=dt1, ballot_submission=ballotsub,
                margin=+2, points=1, score=100, win=True, votes_given=1, votes_possible=1)
            TeamScore.objects.create(debate_team=dt2, ballot_submission=ballotsub,
                margin=-2, points=0, score=100, win=False, votes_given=0, votes_possible=1)

            for speaker, dt in [(self.speaker1, dt1), (self.speaker2, dt2)]:
                style = style_scores[speaker][i - 1]
                content = content_scores[speaker][i - 1]
                ss = SpeakerScore.objects.create(debate_team=dt, ballot_submission=ballotsub,
                    speaker=speaker, position=1, score=style + content)
                SpeakerCriterionScore.objects.create(speaker_score=ss,
                    criterion=self.style, score=style)
                SpeakerCriterionScore.objects.create(speaker_score=ss,
                    criterion=self.content, score=content)

    def tearDown(self):
        DebateTeam.objects.filter(team__tournament=self.tournament).delete()
        self.tournament.delete()

    def get_standings(self, metrics, extra_metrics=(), replies=False):
        generator = SpeakerStandingsGenerator(metrics, ('rank',), extra_metrics,
            tournament=self.tournament, replies=replies)
        with suppress_logs('standings.metrics', logging.INFO):
            return generator.generate(
                Speaker.objects.filter(team__tournament=self.tournament),
                round=self.tournament.round_set.get(seq=2))

    def test_criterion_average(self):
        key = AverageCriterionScoreMetricAnnotator.build_key(self.style.seq)
        standings = self.get_standings((key,))
        self.assertEqual(standings.get_standing(self.speaker1).metrics[key], 31)
        self.assertEqual(standings.get_standing(self.speaker2).metrics[key], 36)

    def test_criterion_total(self):
        key = TotalCriterionScoreMetricAnnotator.build_key(self.style.seq)
        standings = self.get_standings((key,))
        self.assertEqual(standings.get_standing(self.speaker1).metrics[key], 62)
        self.assertEqual(standings.get_standing(self.speaker2).metrics[key], 72)

    def test_criteria_are_aggregated_separately(self):
        """The whole point: a criterion metric must not pick up other criteria's
        scores, nor the speech's overall score."""
        style = AverageCriterionScoreMetricAnnotator.build_key(self.style.seq)
        content = AverageCriterionScoreMetricAnnotator.build_key(self.content.seq)
        standings = self.get_standings((style,), (content, 'average'))

        info1 = standings.get_standing(self.speaker1)
        self.assertEqual(info1.metrics[style], 31)
        self.assertEqual(info1.metrics[content], 39)
        self.assertEqual(info1.metrics['average'], 70)

    def test_ranking_differs_from_overall(self):
        """Speaker 2 is worse overall but better on style, so should top the
        style tab and place second on the overall tab."""
        style = AverageCriterionScoreMetricAnnotator.build_key(self.style.seq)

        style_standings = self.get_standings((style,))
        self.assertEqual(style_standings.get_standing(self.speaker2).rankings['rank'], (1, False))
        self.assertEqual(style_standings.get_standing(self.speaker1).rankings['rank'], (2, False))

        overall_standings = self.get_standings(('average',))
        self.assertEqual(overall_standings.get_standing(self.speaker1).rankings['rank'], (1, False))
        self.assertEqual(overall_standings.get_standing(self.speaker2).rankings['rank'], (2, False))

    def test_metric_choices_include_criteria(self):
        choices = dict(SpeakerStandingsGenerator.get_metric_choices(tournament=self.tournament))
        self.assertIn(AverageCriterionScoreMetricAnnotator.build_key(self.style.seq), choices)
        self.assertIn(TotalCriterionScoreMetricAnnotator.build_key(self.content.seq), choices)
        self.assertEqual(
            choices[AverageCriterionScoreMetricAnnotator.build_key(self.style.seq)],
            "Average for style")

    def test_metric_choices_without_tournament_omit_criteria(self):
        choices = dict(SpeakerStandingsGenerator.get_metric_choices())
        self.assertNotIn(AverageCriterionScoreMetricAnnotator.build_key(self.style.seq), choices)

    def test_criterion_metric_does_not_inflate_other_metrics(self):
        """The speakercriterionscore join produces one row per criterion per
        speech. If a criterion metric shared the combined query, that fan-out
        would multiply other aggregations in it."""
        style = AverageCriterionScoreMetricAnnotator.build_key(self.style.seq)
        style_total = TotalCriterionScoreMetricAnnotator.build_key(self.style.seq)

        alone = self.get_standings(('count',))
        self.assertEqual(alone.get_standing(self.speaker1).metrics['count'], 2)

        # Each speech has 2 criteria attached, so a naive join would give 4.
        combined = self.get_standings((style,), ('count', 'total', style_total))
        info = combined.get_standing(self.speaker1)
        self.assertEqual(info.metrics['count'], 2)
        self.assertEqual(info.metrics['total'], 140)  # (30+40) + (32+38), not doubled
        self.assertEqual(info.metrics[style_total], 62)

    def test_metric_abbreviations(self):
        """A criterion's own metrics drop its name on its dedicated page, where
        the title already gives it, but keep it everywhere else."""
        style = AverageCriterionScoreMetricAnnotator.build_key(self.style.seq)
        content = AverageCriterionScoreMetricAnnotator.build_key(self.content.seq)

        standings = self.get_standings((style,), (content,))
        self.assertEqual([m['abbr'] for m in standings.metrics_info()],
            ["Style Avg", "Content Avg"])

        generator = SpeakerStandingsGenerator((style,), ('rank',), (content,),
            tournament=self.tournament, standalone_criterion=self.style)
        with suppress_logs('standings.metrics', logging.INFO):
            standings = generator.generate(
                Speaker.objects.filter(team__tournament=self.tournament),
                round=self.tournament.round_set.get(seq=2))
        self.assertEqual([m['abbr'] for m in standings.metrics_info()],
            ["Avg", "Content Avg"])

    def test_criteria_scoped_to_the_speeches_of_the_standings(self):
        """Criterion metrics count the speeches the standings are over, as the
        other speaker metrics do: substantives for speaker standings, the reply
        for reply standings. A criterion's own speech_type doesn't enter into
        it, since a criterion is only ever scored on speeches it applies to."""
        self.tournament.preferences['debate_rules__reply_scores_enabled'] = True
        self.tournament.preferences['debate_rules__substantive_speakers'] = 3

        rd = self.tournament.round_set.get(seq=1)
        dt = DebateTeam.objects.get(debate__round=rd, team=self.team1)
        ballotsub = BallotSubmission.objects.get(debate__round=rd)

        # speaker1 already has a position-1 speech from setUp, scored 30 on
        # style; give them a reply speech scored on style too.
        reply_score = SpeakerScore.objects.create(debate_team=dt, ballot_submission=ballotsub,
            speaker=self.speaker1, position=self.tournament.reply_position, score=38)
        SpeakerCriterionScore.objects.create(speaker_score=reply_score,
            criterion=self.style, score=18)

        style_key = AverageCriterionScoreMetricAnnotator.build_key(self.style.seq)

        # Speaker standings: the substantive speeches only (30 and 32), not 18.
        standings = self.get_standings((style_key,))
        self.assertEqual(standings.get_standing(self.speaker1).metrics[style_key], 31)

        # Reply standings: the reply speech only.
        reply_standings = self.get_standings((style_key,), replies=True)
        self.assertEqual(reply_standings.get_standing(self.speaker1).metrics[style_key], 18)

    def test_public_tab_respects_release_preference(self):
        url = reverse_tournament('standings-public-tab-criterion', self.tournament,
            kwargs={'criterion': self.style.seq})

        self.tournament.preferences['tab_release__criterion_tabs_released'] = False
        with suppress_logs('django.request', logging.WARNING):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        self.tournament.preferences['tab_release__criterion_tabs_released'] = True
        with suppress_logs('standings.metrics', logging.INFO):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Style")

    def test_api_standings_accepts_criterion_metric(self):
        self.tournament.preferences['tab_release__speaker_tab_released'] = True
        key = AverageCriterionScoreMetricAnnotator.build_key(self.style.seq)

        url = reverse('api-substantive-speaker-standings', kwargs={'tournament_slug': self.tournament.slug})
        with suppress_logs('standings.metrics', logging.INFO):
            response = self.client.get(url, {'metrics': key})
        self.assertEqual(response.status_code, 200, response.data)

        by_speaker = {row['speaker'].split('/')[-1]: row for row in response.data}
        self.assertEqual(len(by_speaker), 2)
        for row in response.data:
            metrics = {m['metric']: m['value'] for m in row['metrics']}
            self.assertIn(key, metrics)

    def test_api_standings_rejects_unknown_criterion_metric(self):
        self.tournament.preferences['tab_release__speaker_tab_released'] = True

        url = reverse('api-substantive-speaker-standings', kwargs={'tournament_slug': self.tournament.slug})
        with suppress_logs('django.request', logging.WARNING):
            response = self.client.get(url, {'metrics': 'criterion_avg_99'})
        self.assertEqual(response.status_code, 400)

    def test_criterion_metric_can_be_saved_as_a_preference(self):
        """The criteria are per-tournament, so they can't be in the static
        choices the preference declares; validation must let them through."""
        key = AverageCriterionScoreMetricAnnotator.build_key(self.style.seq)
        self.tournament.preferences['standings__speaker_standings_precedence'] = [key]
        self.assertEqual(self.tournament.pref('speaker_standings_precedence'), [key])

        total = TotalCriterionScoreMetricAnnotator.build_key(self.content.seq)
        self.tournament.preferences['standings__speaker_standings_extra_metrics'] = [total]
        self.assertEqual(self.tournament.pref('speaker_standings_extra_metrics'), [total])

    def test_preferences_form_accepts_criterion_metric(self):
        key = AverageCriterionScoreMetricAnnotator.build_key(self.style.seq)
        FormClass = tournament_preference_form_builder(  # noqa: N806
            instance=self.tournament, section='standings')
        form = FormClass(data={
            'standings__speaker_standings_precedence_0': key,
            'standings__speaker_standings_precedence_1': EMPTY_CHOICE,
            'standings__speaker_standings_precedence_2': EMPTY_CHOICE,
            'standings__speaker_standings_precedence_3': EMPTY_CHOICE,
        })
        form.is_valid()
        self.assertNotIn('standings__speaker_standings_precedence', form.errors)

    def test_preferences_reject_invalid_metric(self):
        with self.assertRaises(ValidationError):
            self.tournament.preferences['standings__speaker_standings_precedence'] = ['not_a_metric']

    def test_public_tab_unknown_criterion_404s(self):
        self.tournament.preferences['tab_release__criterion_tabs_released'] = True
        url = reverse_tournament('standings-public-tab-criterion', self.tournament,
            kwargs={'criterion': 99})
        with suppress_logs('django.request', logging.WARNING):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class TestReplyCriterionStandings(TestCase):
    """Tests the tab for a criterion scored only on reply speeches.

    In formats like WSDC the reply is given by one of the substantive speakers,
    so the substantive speech count usually clears the eligibility threshold
    anyway. These tests cover the case it doesn't: a speaker who gives replies
    without giving substantives, whose substantive count says nothing about how
    many replies they gave."""

    def setUp(self):
        self.tournament = Tournament.objects.create(slug="replycriteriontest",
            name="Reply criterion test")
        self.tournament.preferences['debate_rules__reply_scores_enabled'] = True
        self.tournament.preferences['debate_rules__substantive_speakers'] = 3
        self.tournament.preferences['standings__standings_missed_replies'] = 1
        # Set explicitly: this is the threshold that would exclude a speaker who
        # gives replies but no substantives, if the tab counted substantives.
        self.tournament.preferences['standings__standings_missed_debates'] = 1
        self.tournament.preferences['tab_release__criterion_tabs_released'] = True

        self.team1 = Team.objects.create(tournament=self.tournament, reference="1",
            use_institution_prefix=False)
        self.team2 = Team.objects.create(tournament=self.tournament, reference="2",
            use_institution_prefix=False)
        self.speaker1 = Speaker.objects.create(team=self.team1, name="Speaker 1")
        self.speaker2 = Speaker.objects.create(team=self.team2, name="Speaker 2")

        self.reply_criterion = ScoreCriterion.objects.create(tournament=self.tournament,
            name="Rebuttal", seq=1, weight=1, min_score=0, max_score=20, step=1,
            speech_type=ScoreCriterion.SpeechType.REPLY)

        adj = Adjudicator.objects.create(tournament=self.tournament, name="Adjudicator")
        reply_scores = {self.speaker1: [16, 17], self.speaker2: [18, 19]}

        for i in [1, 2]:
            rd = Round.objects.create(tournament=self.tournament, seq=i, schedule_group=i,
                completed=True)
            debate = Debate.objects.create(round=rd)
            dt1 = DebateTeam.objects.create(debate=debate, team=self.team1, side=DebateSide.AFF)
            dt2 = DebateTeam.objects.create(debate=debate, team=self.team2, side=DebateSide.NEG)
            DebateAdjudicator.objects.create(debate=debate, adjudicator=adj,
                type=DebateAdjudicator.TYPE_CHAIR)
            ballotsub = BallotSubmission.objects.create(debate=debate, confirmed=True)
            TeamScore.objects.create(debate_team=dt1, ballot_submission=ballotsub,
                margin=+2, points=1, score=100, win=True, votes_given=1, votes_possible=1)
            TeamScore.objects.create(debate_team=dt2, ballot_submission=ballotsub,
                margin=-2, points=0, score=100, win=False, votes_given=0, votes_possible=1)

            # Each speaker only gives the reply, as a reply speaker typically would.
            for speaker, dt in [(self.speaker1, dt1), (self.speaker2, dt2)]:
                ss = SpeakerScore.objects.create(debate_team=dt, ballot_submission=ballotsub,
                    speaker=speaker, position=self.tournament.reply_position, score=38)
                SpeakerCriterionScore.objects.create(speaker_score=ss,
                    criterion=self.reply_criterion, score=reply_scores[speaker][i - 1])

    def tearDown(self):
        DebateTeam.objects.filter(team__tournament=self.tournament).delete()
        self.tournament.delete()

    def get_ranks(self):
        """Returns each speaker's rank on the criterion tab, as None if unranked.

        This drives the view directly rather than fetching the page, because the
        public tab pages are wrapped in `cache_page` and a cached response has no
        template context to read the table out of."""
        view = CriterionStandingsView()
        view.request = RequestFactory().get('/')
        view.kwargs = {
            'tournament_slug': self.tournament.slug,
            'round_seq': self.tournament.round_set.order_by('seq').last().seq,
            'criterion': self.reply_criterion.seq,
        }
        view.object = self.reply_criterion
        with suppress_logs('standings.metrics', logging.INFO):
            standings, rounds = view.get_standings()
        return {info.speaker: info.rankings.get('rank') for info in standings}

    def test_reply_speakers_are_ranked(self):
        """A speaker who only ever gives the reply has no substantive speeches,
        so ranking against the missed-debates count would leave them unranked."""
        ranks = self.get_ranks()
        self.assertIsNotNone(ranks[self.speaker1])
        self.assertIsNotNone(ranks[self.speaker2])

    def test_ranked_by_reply_criterion_scores(self):
        ranks = self.get_ranks()
        self.assertEqual(ranks[self.speaker2], (1, False))  # 18, 19
        self.assertEqual(ranks[self.speaker1], (2, False))  # 16, 17

    def test_missing_replies_excludes_speaker_from_ranking(self):
        """A speaker below the reply threshold is listed but not ranked."""
        self.tournament.preferences['standings__standings_missed_replies'] = 0
        SpeakerScore.objects.filter(speaker=self.speaker1,
            debate_team__debate__round__seq=2).delete()

        ranks = self.get_ranks()
        self.assertEqual(ranks[self.speaker2], (1, False))
        self.assertIsNone(ranks[self.speaker1])
