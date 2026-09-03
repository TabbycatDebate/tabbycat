import json
from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import formats, timezone

from tournaments.models import ScheduleEvent, Tournament
from users.models import UserPermission
from users.permissions import Permission
from utils.misc import reverse_tournament


class SetTournamentScheduleViewTest(TestCase):

    fixtures = ['after_round_4.json']

    def setUp(self):
        self.tournament = Tournament.objects.first()
        self.user = get_user_model().objects.create_user('schedule-admin', is_superuser=True)
        self.client.force_login(self.user)
        self.url = reverse_tournament('tournament-set-schedule', self.tournament)

    def create_event(self, title, day, hour):
        return ScheduleEvent.objects.create(
            tournament=self.tournament,
            type=ScheduleEvent.Types.OTHER,
            title=title,
            start_time=timezone.make_aware(datetime(2026, 8, day, hour)),
        )

    def test_serializes_events_for_vue_editor(self):
        first = self.create_event('Registration', 15, 9)
        second = self.create_event('Round 1', 16, 10)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        editor_data = response.context['schedule_editor_data']
        self.assertEqual(editor_data['management']['initialForms'], 2)
        self.assertEqual(editor_data['management']['totalForms'], 2)
        self.assertEqual(editor_data['events'][0]['id'], str(first.pk))
        self.assertEqual(editor_data['events'][0]['startDate'], '2026-08-15')
        self.assertEqual(editor_data['events'][0]['startTime'], '09:00')
        self.assertEqual(editor_data['events'][1]['id'], str(second.pk))
        self.assertTrue(editor_data['canEdit'])
        self.assertContains(response, '<schedule-editor-container')

    def test_dynamic_formset_event_can_be_created(self):
        response = self.client.post(self.url, {
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-tournament': str(self.tournament.pk),
            'form-0-type': ScheduleEvent.Types.BRIEFING,
            'form-0-title': 'Opening briefing',
            'form-0-start_time': '2026-08-15T09:00',
            'form-0-end_time': '2026-08-15T09:30',
            'form-0-round': '',
        })

        self.assertRedirects(response, self.url)
        event = ScheduleEvent.objects.get(tournament=self.tournament)
        self.assertEqual(event.title, 'Opening briefing')
        self.assertEqual(event.type, ScheduleEvent.Types.BRIEFING)

    def test_persisted_events_can_be_updated_and_deleted(self):
        deleted = self.create_event('Registration', 15, 9)
        updated = self.create_event('Briefing', 15, 10)

        response = self.client.post(self.url, {
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '2',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-id': str(deleted.pk),
            'form-0-tournament': str(self.tournament.pk),
            'form-0-type': deleted.type,
            'form-0-title': deleted.title,
            'form-0-start_time': '2026-08-15T09:00',
            'form-0-end_time': '',
            'form-0-round': '',
            'form-0-DELETE': 'on',
            'form-1-id': str(updated.pk),
            'form-1-tournament': str(self.tournament.pk),
            'form-1-type': updated.type,
            'form-1-title': 'Opening briefing',
            'form-1-start_time': '2026-08-15T10:00',
            'form-1-end_time': '',
            'form-1-round': '',
            'form-1-DELETE': '',
        })

        self.assertRedirects(response, self.url)
        self.assertFalse(ScheduleEvent.objects.filter(pk=deleted.pk).exists())
        updated.refresh_from_db()
        self.assertEqual(updated.title, 'Opening briefing')

    def test_invalid_post_rehydrates_values_and_errors(self):
        response = self.client.post(self.url, {
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-tournament': str(self.tournament.pk),
            'form-0-type': ScheduleEvent.Types.BRIEFING,
            'form-0-title': 'Opening briefing',
            'form-0-start_time': 'not-a-date',
            'form-0-end_time': '',
            'form-0-round': '',
        })

        self.assertEqual(response.status_code, 200)
        event_data = response.context['schedule_editor_data']['events'][0]
        self.assertEqual(event_data['title'], 'Opening briefing')
        self.assertEqual(event_data['startRaw'], 'not-a-date')
        self.assertIn('start_time', event_data['errors'])

    def test_view_only_user_receives_read_only_editor(self):
        viewer = get_user_model().objects.create_user('schedule-viewer')
        UserPermission.objects.create(
            user=viewer,
            tournament=self.tournament,
            permission=Permission.VIEW_EVENTS,
        )
        self.client.force_login(viewer)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['schedule_editor_data']['canEdit'])

    def test_blank_title_uses_event_type_and_round(self):
        round = self.tournament.round_set.first()
        response = self.client.post(self.url, {
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-tournament': str(self.tournament.pk),
            'form-0-type': ScheduleEvent.Types.DEBATE,
            'form-0-title': '',
            'form-0-start_time': '2026-08-15T10:00',
            'form-0-end_time': '2026-08-15T11:00',
            'form-0-round': str(round.pk),
        })

        self.assertRedirects(response, self.url)
        event = ScheduleEvent.objects.get(tournament=self.tournament)
        self.assertEqual(event.title, '')
        self.assertEqual(event.display_title, f'{round.name} — Debate')

    def test_custom_title_overrides_automatic_title(self):
        round = self.tournament.round_set.first()
        event = ScheduleEvent.objects.create(
            tournament=self.tournament,
            type=ScheduleEvent.Types.DEBATE,
            title='Grand final',
            start_time=timezone.make_aware(datetime(2026, 8, 15, 10)),
            round=round,
        )

        self.assertEqual(event.display_title, 'Grand final')

    def test_blank_title_without_round_uses_event_type(self):
        event = ScheduleEvent.objects.create(
            tournament=self.tournament,
            type=ScheduleEvent.Types.BRIEFING,
            title='',
            start_time=timezone.make_aware(datetime(2026, 8, 15, 9)),
        )

        self.assertEqual(event.display_title, 'Briefing')

    def test_automatic_title_is_exposed_by_api(self):
        event = ScheduleEvent.objects.create(
            tournament=self.tournament,
            type=ScheduleEvent.Types.BRIEFING,
            title='',
            start_time=timezone.make_aware(datetime(2026, 8, 15, 9)),
        )

        response = self.client.get(reverse_tournament('api-scheduleevent-list', self.tournament))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]['title'], '')
        self.assertEqual(response.json()[0]['display_title'], event.display_title)

    def test_editor_explains_optional_automatic_title(self):
        response = self.client.get(self.url)

        self.assertContains(response, '<schedule-editor-container')
        self.assertNotContains(response, 'schedule-title-badge')

    def test_editor_data_is_safely_embedded(self):
        self.create_event('</script><script>alert(1)</script>', 15, 9)

        response = self.client.get(self.url)

        self.assertNotContains(response, '</script><script>alert(1)</script>')
        self.assertContains(response, r'\u003C/script\u003E\u003Cscript\u003E')

    def test_public_schedule_is_separated_into_local_days(self):
        first = self.create_event('<b>Registration</b>', 15, 9)
        self.create_event('Round 1', 16, 10)
        self.tournament.preferences['public_features__public_schedule'] = True

        response = self.client.get(reverse_tournament('tournament-public-schedule', self.tournament))

        self.assertEqual(response.status_code, 200)
        tables = json.loads(response.context['tables_data'])
        self.assertEqual(len(tables), 2)
        self.assertEqual(tables[0]['title'], formats.date_format(
            timezone.localtime(first.start_time).date(), format='DATE_FORMAT', use_l10n=True,
        ))
        self.assertEqual([header['key'] for header in tables[0]['head']], [
            'event', 'start_time', 'end_time',
        ])
        self.assertEqual(tables[0]['data'][0][0]['text'], '&lt;b&gt;Registration&lt;/b&gt;')
        self.assertEqual(tables[0]['data'][0][1]['text'], formats.time_format(
            timezone.localtime(first.start_time), format='TIME_FORMAT', use_l10n=True,
        ))
