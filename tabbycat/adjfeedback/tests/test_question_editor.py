from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from adjfeedback.models import AdjudicatorFeedback, AdjudicatorFeedbackQuestion
from draw.models import DebateTeam
from participants.models import Adjudicator, Team
from registration.models import Answer, Question
from tournaments.models import Tournament
from utils.misc import reverse_tournament


class FeedbackQuestionEditorTests(TestCase):
    fixtures = ['after_round_4.json']

    def setUp(self):
        self.tournament = Tournament.objects.first()
        self.content_type = ContentType.objects.get_for_model(AdjudicatorFeedback)
        AdjudicatorFeedbackQuestion.objects.filter(tournament=self.tournament).delete()
        self.user = get_user_model().objects.create_user('feedback-question-admin', is_superuser=True)
        self.client.force_login(self.user)
        self.url = reverse_tournament('adjfeedback-edit-questions', self.tournament)

    def question(self, seq=0):
        return AdjudicatorFeedbackQuestion.objects.create(
            tournament=self.tournament, for_content_type=self.content_type,
            seq=seq, name='Clarity', text='Was the explanation clear?', reference=f'clarity_{seq}',
            answer_type='t', required=True, from_adj=True, from_team=False,
        )

    def payload(self, rows):
        prefix = 'adjudicatorfeedback'
        data = {
            f'{prefix}-TOTAL_FORMS': str(len(rows)),
            f'{prefix}-INITIAL_FORMS': str(sum(bool(row.get('question_ptr')) for row in rows)),
            f'{prefix}-MIN_NUM_FORMS': '0', f'{prefix}-MAX_NUM_FORMS': '1000',
        }
        for i, row in enumerate(rows):
            values = {'text': 'Was the explanation clear?', 'name': 'Clarity', 'answer_type': 't', 'reference': f'clarity_{i}', 'ORDER': str(i), **row}
            data.update({f'{prefix}-{i}-{name}': value for name, value in values.items()})
        return data

    def test_serializes_feedback_fields_and_fixed_score(self):
        question = self.question()
        response = self.client.get(self.url)
        self.assertContains(response, '<question-editor-container')
        section = response.context['question_editor_data']['sections'][0]
        self.assertEqual(section['primaryKey'], 'question_ptr')
        self.assertEqual(section['questions'][0]['values']['question_ptr'], question.pk)
        self.assertIs(section['questions'][0]['values']['from_adj'], True)
        self.assertIs(section['questions'][0]['values']['from_team'], False)
        self.assertEqual(section['fields']['from_adj']['kind'], 'checkbox')
        self.assertIn('reference', section['fields'])
        self.assertEqual(section['systemQuestions'][0]['label'], 'Overall score')
        self.assertTrue(section['systemQuestions'][0]['disabled'])

    def test_creates_feedback_subclass_with_audience_and_choices(self):
        response = self.client.post(self.url, self.payload([{
            'from_adj': 'on', 'from_team': 'on', 'answer_type': 'ss', 'choices': 'Yes\nNo',
        }]))
        self.assertRedirects(response, self.url)
        question = AdjudicatorFeedbackQuestion.objects.get(tournament=self.tournament)
        self.assertEqual(question.for_content_type, self.content_type)
        self.assertEqual(question.reference, 'clarity_0')
        self.assertTrue(question.from_adj and question.from_team)
        self.assertEqual(question.choices, ['Yes', 'No'])
        self.assertEqual(question.seq, 0)

    def test_reorders_and_updates_audience_without_losing_answers(self):
        first, second = self.question(), self.question(1)
        feedback = AdjudicatorFeedback.objects.create(
            adjudicator=Adjudicator.objects.filter(tournament=self.tournament).first(),
            source_team=DebateTeam.objects.filter(debate__round__tournament=self.tournament).first(),
            score=3, submitter_type=AdjudicatorFeedback.Submitter.TABROOM,
        )
        answer = Answer.objects.create(question=first, content_object=feedback, answer='Keep this answer')
        response = self.client.post(self.url, self.payload([
            {'question_ptr': first.pk, 'ORDER': '1', 'from_team': 'on'},
            {'question_ptr': second.pk, 'ORDER': '0', 'from_adj': 'on'},
        ]))
        self.assertRedirects(response, self.url)
        first.refresh_from_db()
        second.refresh_from_db()
        answer.refresh_from_db()
        self.assertEqual((first.seq, second.seq), (1, 0))
        self.assertFalse(first.from_adj)
        self.assertTrue(first.from_team)
        self.assertEqual(answer.answer, 'Keep this answer')

    def test_deletes_parent_and_feedback_subclass(self):
        question = self.question()
        response = self.client.post(self.url, self.payload([{'question_ptr': question.pk, 'DELETE': 'on'}]))
        self.assertRedirects(response, self.url)
        self.assertFalse(Question.objects.filter(pk=question.pk).exists())
        self.assertFalse(AdjudicatorFeedbackQuestion.objects.filter(pk=question.pk).exists())

    def test_invalid_reference_and_scale_remain_bound(self):
        response = self.client.post(self.url, self.payload([{
            'reference': 'invalid reference!', 'from_team': 'on', 'answer_type': 'is',
        }]))
        self.assertEqual(response.status_code, 200)
        question = response.context['question_editor_data']['sections'][0]['questions'][0]
        self.assertIn('reference', question['errors'])
        self.assertIn('min_value', question['errors'])
        self.assertEqual(question['values']['reference'], 'invalid reference!')
        self.assertTrue(question['values']['from_team'])
        self.assertFalse(AdjudicatorFeedbackQuestion.objects.filter(tournament=self.tournament).exists())

    def test_rejects_registration_question_id(self):
        question = Question.objects.create(
            tournament=self.tournament, for_content_type=ContentType.objects.get_for_model(Team),
            seq=0, name='Registration', text='Original', answer_type='t',
        )
        response = self.client.post(self.url, self.payload([{'question_ptr': question.pk}]))
        self.assertEqual(response.status_code, 200)
        question.refresh_from_db()
        self.assertEqual(question.text, 'Original')

    def test_rejects_another_tournaments_question(self):
        question = self.question()
        other = Tournament.objects.create(name='Other', short_name='Other', slug='other-feedback-editor')
        question.tournament = other
        question.save()
        response = self.client.post(self.url, self.payload([{'question_ptr': question.pk}]))
        self.assertEqual(response.status_code, 200)
        question.refresh_from_db()
        self.assertEqual(question.tournament, other)

    def test_requires_question_edit_permission(self):
        self.user.is_superuser = False
        self.user.save()
        response = self.client.post(self.url, self.payload([{}]))
        self.assertEqual(response.status_code, 403)
