from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from tournaments.models import ScheduleEvent, Tournament
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

    def test_groups_events_by_local_start_date(self):
        first = self.create_event('Registration', 15, 9)
        second = self.create_event('Round 1', 16, 10)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['schedule_days']), 2)
        self.assertEqual(response.context['schedule_days'][0]['forms'][0].instance, first)
        self.assertEqual(response.context['schedule_days'][1]['forms'][0].instance, second)
        self.assertEqual(response.context['schedule_event_count'], 2)
        self.assertContains(response, 'data-persisted="true"', count=2)
        self.assertContains(response, 'value="2026-08-15T09:00"')

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

        self.assertContains(response, 'Custom title')
        self.assertContains(response, 'Leave blank to show')
