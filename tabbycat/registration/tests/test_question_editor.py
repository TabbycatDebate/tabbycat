from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet
from django.test import TestCase

from participants.models import Speaker, Team
from registration.form_utils import CustomQuestionsFormMixin
from registration.forms import SpeakerForm
from registration.models import Answer, Question
from tournaments.models import Tournament
from users.models import UserPermission
from users.permissions import Permission
from utils.misc import reverse_tournament


class QuestionEditorTests(TestCase):
    fixtures = ['after_round_4.json']

    def setUp(self):
        self.tournament = Tournament.objects.first()
        self.user = get_user_model().objects.create_user('questions-admin', is_superuser=True)
        self.client.force_login(self.user)
        self.url = reverse_tournament('reg-team-questions', self.tournament)

    def question(self, model=Team, seq=0, **kwargs):
        return Question.objects.create(
            tournament=self.tournament, for_content_type=ContentType.objects.get_for_model(model),
            seq=seq, name='Question', text='Your question?', answer_type='t', **kwargs,
        )

    def payload(self, rows=(), speakers=()):
        data = {}
        for prefix, questions in [('team', rows), ('speaker', speakers)]:
            data.update({
                f'{prefix}-TOTAL_FORMS': str(len(questions)),
                f'{prefix}-INITIAL_FORMS': str(sum(bool(q.get('id')) for q in questions)),
                f'{prefix}-MIN_NUM_FORMS': '0', f'{prefix}-MAX_NUM_FORMS': '1000',
            })
            for i, question in enumerate(questions):
                values = {'name': 'Question', 'text': 'Your question?', 'answer_type': 't', 'ORDER': str(i), **question}
                data.update({f'{prefix}-{i}-{key}': value for key, value in values.items()})
        return data

    def test_creates_questions_in_both_sections_and_updates_system_fields(self):
        data = self.payload([{'answer_type': 'ss', 'choices': 'Vegan\nVegetarian, with dairy'}], [{}])
        data['speaker-system-phone'] = 'on'
        response = self.client.post(self.url, data)
        self.assertRedirects(response, self.url)
        question = Question.objects.get(tournament=self.tournament, for_content_type=ContentType.objects.get_for_model(Team))
        self.assertEqual(question.choices, ['Vegan', 'Vegetarian, with dairy'])
        self.assertEqual(question.seq, 0)
        self.assertTrue(Question.objects.filter(tournament=self.tournament, for_content_type=ContentType.objects.get_for_model(Speaker)).exists())
        self.assertEqual(self.tournament.preferences['registration__reg_speaker_fields'], ['phone'])

    def test_save_redirect_ignores_untrusted_request_path(self):
        response = self.client.post(self.url, self.payload(), SCRIPT_NAME='//evil.example')
        self.assertRedirects(response, self.url, fetch_redirect_response=False)

    def test_reordering_preserves_answers(self):
        first, second = self.question(), self.question(seq=1)
        team = Team.objects.filter(tournament=self.tournament).first()
        answer = Answer.objects.create(question=first, content_object=team, answer='Existing answer')
        response = self.client.post(self.url, self.payload([
            {'id': first.pk, 'ORDER': '1'}, {'id': second.pk, 'ORDER': '0'},
        ]))
        self.assertRedirects(response, self.url)
        first.refresh_from_db()
        second.refresh_from_db()
        answer.refresh_from_db()
        self.assertEqual((first.seq, second.seq), (1, 0))
        self.assertEqual(answer.answer, 'Existing answer')

    def test_invalid_second_section_saves_nothing(self):
        response = self.client.post(self.url, self.payload([{}], [{'text': '', 'name': 'Invalid'}]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Question.objects.filter(tournament=self.tournament, for_content_type=ContentType.objects.get_for_model(Team)).exists())

    def test_cannot_edit_question_from_another_section(self):
        question = self.question(Speaker)
        response = self.client.post(self.url, self.payload([{'id': question.pk, 'text': 'Tampered'}]))
        self.assertEqual(response.status_code, 200)
        question.refresh_from_db()
        self.assertEqual(question.text, 'Your question?')

    def test_cannot_edit_question_from_another_tournament(self):
        other = Tournament.objects.create(name='Other', short_name='Other', slug='other-questions')
        question = self.question()
        question.tournament = other
        question.save()
        response = self.client.post(self.url, self.payload([{'id': question.pk, 'text': 'Tampered'}]))
        self.assertEqual(response.status_code, 200)
        question.refresh_from_db()
        self.assertEqual(question.text, 'Your question?')

    def test_delete_does_not_require_question_fields(self):
        question = self.question()
        data = self.payload([{'id': question.pk, 'DELETE': 'on', 'name': '', 'text': '', 'answer_type': ''}])
        response = self.client.post(self.url, data)
        self.assertRedirects(response, self.url)
        self.assertFalse(Question.objects.filter(pk=question.pk).exists())

    def test_requires_options_for_choice_question(self):
        response = self.client.post(self.url, self.payload([{'answer_type': 'ss'}]))
        self.assertIn('choices', response.context['question_editor_data']['sections'][0]['questions'][0]['errors'])
        self.assertFalse(Question.objects.filter(tournament=self.tournament, for_content_type=ContentType.objects.get_for_model(Team)).exists())

    def test_question_editor_cannot_change_settings_without_permission(self):
        self.user.is_superuser = False
        self.user.save()
        UserPermission.objects.create(user=self.user, tournament=self.tournament, permission=Permission.EDIT_QUESTIONS)
        original = self.tournament.pref('reg_speaker_fields')
        data = self.payload([{}])
        data['speaker-system-phone'] = 'on'
        self.assertRedirects(self.client.post(self.url, data), self.url)
        self.assertEqual(self.tournament.preferences['registration__reg_speaker_fields'], original)

    def test_read_only_user_cannot_post(self):
        self.user.is_superuser = False
        self.user.save()
        self.assertEqual(self.client.post(self.url, self.payload([{}])).status_code, 403)

    def test_editor_routes_render_the_expected_sections(self):
        for route, prefixes in (
            ('reg-team-questions', ['team', 'speaker']),
            ('reg-speaker-questions', ['team', 'speaker']),
            ('reg-institution-questions', ['tournamentinstitution', 'coach']),
            ('reg-coach-questions', ['tournamentinstitution', 'coach']),
            ('reg-adjudicator-questions', ['adjudicator']),
        ):
            with self.subTest(route=route):
                response = self.client.get(reverse_tournament(route, self.tournament))
                self.assertContains(response, '<question-editor-container')
                self.assertEqual([s['prefix'] for s in response.context['sections']], prefixes)

    def test_scale_requires_both_bounds(self):
        response = self.client.post(self.url, self.payload([{'answer_type': 'is'}]))
        self.assertIn('min_value', response.context['question_editor_data']['sections'][0]['questions'][0]['errors'])

    def test_short_name_defaults_to_question_text(self):
        text = 'A registration question longer than thirty characters?'
        response = self.client.post(self.url, self.payload([{'name': '', 'text': text}]))
        self.assertRedirects(response, self.url)
        self.assertEqual(Question.objects.get(text=text).name, text[:30])

    def test_bound_editor_data_preserves_values_order_deletion_and_errors(self):
        first, second = self.question(), self.question(seq=1)
        data = self.payload([
            {'id': first.pk, 'ORDER': '1', 'DELETE': 'on', 'choices': 'One\nTwo'},
            {'id': second.pk, 'ORDER': '0', 'answer_type': 'ss', 'choices': ''},
        ])
        data['speaker-system-phone'] = 'on'
        response = self.client.post(self.url, data)
        editor = response.context['question_editor_data']
        team, speaker = editor['sections']
        self.assertEqual(team['management']['initialForms'], 2)
        self.assertEqual(team['questions'][0]['formIndex'], 0)
        self.assertEqual(team['questions'][0]['values']['ORDER'], '1')
        self.assertEqual(team['questions'][0]['values']['choices'], 'One\nTwo')
        self.assertTrue(team['questions'][0]['deleted'])
        self.assertIn('choices', team['questions'][1]['errors'])
        phone = next(q for q in speaker['systemQuestions'] if q['name'] == 'speaker-system-phone')
        self.assertTrue(phone['enabled'])
        self.assertEqual(team['emptyQuestion']['values']['answer_type'], 't')

    def test_open_participant_form_keeps_answers_on_their_questions_after_reorder(self):
        first, second = self.question(Speaker), self.question(Speaker, seq=1)
        data = {
            'name': 'New speaker',
            CustomQuestionsFormMixin.question_field_name(first): 'First answer',
            CustomQuestionsFormMixin.question_field_name(second): 'Second answer',
        }
        response = self.client.post(self.url, self.payload(speakers=[
            {'id': first.pk, 'ORDER': '1'}, {'id': second.pk, 'ORDER': '0'},
        ]))
        self.assertRedirects(response, self.url)
        form = SpeakerForm(Team.objects.filter(tournament=self.tournament).first(), None, data=data)
        self.assertTrue(form.is_valid(), form.errors)
        speaker = form.save()
        self.assertEqual(dict(speaker.answers.values_list('question_id', 'answer')), {
            first.pk: 'First answer', second.pk: 'Second answer',
        })

    def test_question_deleted_before_lock_is_not_recreated(self):
        question = self.question()
        question_id = question.pk
        get = QuerySet.get

        def acquire_lock(queryset, *args, **kwargs):
            if queryset.model is Tournament and queryset.query.select_for_update:
                Question.objects.filter(pk=question_id).delete()
            return get(queryset, *args, **kwargs)

        with patch.object(QuerySet, 'get', acquire_lock):
            response = self.client.post(self.url, self.payload([{'id': question_id}]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Question.objects.filter(pk=question_id).exists())
