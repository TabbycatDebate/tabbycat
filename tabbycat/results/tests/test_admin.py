from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db import connection
from django.test import RequestFactory, TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from adjallocation.models import DebateAdjudicator
from draw.models import Debate, DebateTeam
from participants.models import Adjudicator, Speaker, Team
from results.admin import BallotSubmissionAdmin
from results.models import (
    BallotSubmission, ScoreCriterion, SpeakerCriterionScore, SpeakerCriterionScoreByAdj, SpeakerScore,
    SpeakerScoreByAdj, TeamScore, TeamScoreByAdj,
)
from tournaments.models import Round, Tournament


class ScoreCriterionAdminTests(TestCase):
    def test_search_by_criterion_and_tournament_names(self):
        user = get_user_model().objects.create_superuser(username='criterion-admin')
        tournament = Tournament.objects.create(name='Regional Championship', short_name='Reg Champs', slug='regional')
        other_tournament = Tournament.objects.create(name='National Championship', slug='national')
        criterion_fields = dict(seq=1, weight=1, min_score=0, max_score=10, step=1)
        criterion = ScoreCriterion.objects.create(tournament=tournament, name='Delivery', **criterion_fields)
        ScoreCriterion.objects.create(tournament=other_tournament, name='Content', **criterion_fields)

        self.client.force_login(user)
        url = reverse('admin:results_scorecriterion_changelist')
        for search_term in ('deliv', 'regional', 'reg champs'):
            with self.subTest(search_term=search_term):
                response = self.client.get(url, {'q': search_term})
                self.assertEqual(response.status_code, 200)
                self.assertQuerySetEqual(response.context['cl'].result_list, [criterion])


class BallotSubmissionAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(username='ballot-admin', password='test')
        tournament = Tournament.objects.create(name='Ballot test', slug='ballot-test')
        round = Round.objects.create(tournament=tournament, seq=1, name='Round 1', abbreviation='R1')
        cls.debate = Debate.objects.create(round=round)
        cls.ballot = BallotSubmission.objects.create(debate=cls.debate)
        for side in range(2):
            team = Team.objects.create(tournament=tournament, reference=f'Team {side}')
            dt = DebateTeam.objects.create(debate=cls.debate, team=team, side=side)
            TeamScore.objects.create(ballot_submission=cls.ballot, debate_team=dt, score=225)
            for position in range(1, 4):
                speaker = Speaker.objects.create(team=team, name=f'Speaker {side}-{position}')
                SpeakerScore.objects.create(ballot_submission=cls.ballot, debate_team=dt,
                                            speaker=speaker, position=position, score=75)

    def add_adjudicators(self, count):
        for index in range(count):
            adjudicator = Adjudicator.objects.create(name=f'Adjudicator {index}')
            da = DebateAdjudicator.objects.create(debate=self.debate, adjudicator=adjudicator, type='P')
            for dt in self.debate.debateteam_set.all():
                TeamScoreByAdj.objects.create(ballot_submission=self.ballot, debate_team=dt,
                                             debate_adjudicator=da, score=225)
                for position in range(1, 4):
                    SpeakerScoreByAdj.objects.create(ballot_submission=self.ballot, debate_team=dt,
                                                    debate_adjudicator=da, position=position, score=75)

    def admin_request(self):
        request = RequestFactory().get(f'/database/results/ballotsubmission/{self.ballot.pk}/change/')
        request.user = self.user
        return request

    def render_ballot(self):
        request = self.admin_request()
        model_admin = BallotSubmissionAdmin(BallotSubmission, admin.site)
        with CaptureQueriesContext(connection) as queries:
            response = model_admin.change_view(request, str(self.ballot.pk))
            response.render()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            {inline.formset.model for inline in response.context_data['inline_admin_formsets']},
            {TeamScore, TeamScoreByAdj, SpeakerScore, SpeakerScoreByAdj},
        )
        self.assertContains(response, 'Team 0')
        if self.user.is_superuser:
            self.assertContains(response, 'Team 0 in R1')
        self.assertContains(response, 'Speaker 0-1')
        return queries

    def test_render_queries_do_not_grow_with_panel_size(self):
        self.add_adjudicators(1)
        self.render_ballot()  # Warm template, preference and content-type caches.
        small = self.render_ballot()
        self.add_adjudicators(4)
        large = self.render_ballot()
        self.assertLessEqual(len(large), len(small))

    def test_all_four_score_inlines_save_edits(self):
        self.add_adjudicators(1)
        model_admin = BallotSubmissionAdmin(BallotSubmission, admin.site)
        for formset_class, inline in model_admin.get_formsets_with_inlines(self.admin_request(), self.ballot):
            with self.subTest(model=inline.model):
                formset = formset_class(instance=self.ballot)
                prefix = formset.prefix
                data = {f'{prefix}-{name}': value for name, value in formset.management_form.initial.items()}
                for form in formset:
                    data.update({f'{form.prefix}-{name}': form[name].value() for name in form.fields})
                data[f'{prefix}-0-score'] = '76'
                bound = formset_class(data=data, instance=self.ballot)
                self.assertTrue(bound.is_valid(), bound.errors)
                bound.save()
                self.assertEqual(inline.model.objects.get(pk=formset.forms[0].instance.pk).score, 76)

    def test_search_criterion_scores(self):
        self.add_adjudicators(1)
        criterion = ScoreCriterion.objects.create(
            tournament=self.debate.round.tournament, name='Delivery', seq=1,
            weight=1, min_score=0, max_score=100, step=1,
        )
        speaker_score = SpeakerScore.objects.filter(ballot_submission=self.ballot).first()
        adj_score = SpeakerScoreByAdj.objects.filter(ballot_submission=self.ballot).first()
        criterion_score = SpeakerCriterionScore.objects.create(
            criterion=criterion, speaker_score=speaker_score, score=76,
        )
        adj_criterion_score = SpeakerCriterionScoreByAdj.objects.create(
            criterion=criterion, speaker_score_by_adj=adj_score, score=76,
        )

        self.client.force_login(self.user)
        for result, score_id in ((criterion_score, speaker_score.pk), (adj_criterion_score, adj_score.pk)):
            url = reverse(f'admin:results_{result._meta.model_name}_changelist')
            for search_term in ('deliv', '76', str(score_id)):
                with self.subTest(url=url, search_term=search_term):
                    response = self.client.get(url, {'q': search_term})
                    self.assertEqual(response.status_code, 200)
                    self.assertQuerySetEqual(response.context['cl'].result_list, [result])

    def test_view_only_user_can_render_score_inlines(self):
        self.add_adjudicators(1)
        self.user = get_user_model().objects.create_user(username='ballot-viewer', is_staff=True)
        self.user.user_permissions.add(*Permission.objects.filter(
            content_type__app_label='results',
            codename__in=[f'view_{model._meta.model_name}' for model in (
                BallotSubmission, TeamScore, TeamScoreByAdj, SpeakerScore, SpeakerScoreByAdj,
            )],
        ))
        self.render_ballot()
        small = self.render_ballot()
        self.add_adjudicators(4)
        large = self.render_ballot()
        self.assertLessEqual(len(large), len(small))
