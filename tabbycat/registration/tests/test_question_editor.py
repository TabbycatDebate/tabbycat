from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from participants.models import Speaker, Team
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

    def test_pairs_sections_and_keeps_legacy_speaker_url(self):
        for route in ('reg-team-questions', 'reg-speaker-questions'):
            response = self.client.get(reverse_tournament(route, self.tournament))
            self.assertEqual(response.status_code, 200)
            self.assertEqual([s['prefix'] for s in response.context['sections']], ['team', 'speaker'])
            self.assertContains(response, '<question-editor-container')
            self.assertEqual(len(response.context['question_editor_data']['sections']), 2)

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
        self.assertContains(response, 'Add at least one option.')
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

    def test_all_editor_routes_render(self):
        for route, prefixes in (
            ('reg-institution-questions', ['tournamentinstitution', 'coach']),
            ('reg-coach-questions', ['tournamentinstitution', 'coach']),
            ('reg-adjudicator-questions', ['adjudicator']),
        ):
            response = self.client.get(reverse_tournament(route, self.tournament))
            self.assertEqual(response.status_code, 200)
            self.assertEqual([s['prefix'] for s in response.context['sections']], prefixes)

    def test_scale_requires_both_bounds(self):
        response = self.client.post(self.url, self.payload([{'answer_type': 'is'}]))
        self.assertContains(response, 'Set both bounds for an integer scale.')

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
        self.assertEqual(team['questions'][1]['errors']['choices'], ['Add at least one option.'])
        phone = next(q for q in speaker['systemQuestions'] if q['name'] == 'speaker-system-phone')
        self.assertTrue(phone['enabled'])
        self.assertEqual(team['emptyQuestion']['values']['answer_type'], 't')
