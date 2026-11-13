from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from checkins.models import Event, PersonIdentifier
from checkins.utils import self_checkins_open
from participants.models import Adjudicator
from tournaments.models import ScheduleEvent, Tournament
from utils.misc import reverse_tournament


class SelfCheckinsTestMixin:

    fixtures = ['after_round_4.json']
    scheduled = True

    def setUp(self):
        super().setUp()
        self.tournament = Tournament.objects.first()
        self.tournament.preferences['data_entry__public_checkins_submit'] = True
        self.tournament.preferences['data_entry__public_checkins_submit_scheduled'] = self.scheduled
        self.now = timezone.now()

    def add_event(self, event_type, start, end=None):
        """Adds a schedule event starting `start` and ending `end` (if given)
        minutes from now."""
        return ScheduleEvent.objects.create(
            tournament=self.tournament, type=event_type,
            start_time=self.now + timedelta(minutes=start),
            end_time=self.now + timedelta(minutes=end) if end is not None else None,
        )

    def add_checkin_event(self, start, end=None):
        return self.add_event(ScheduleEvent.Types.CHECK_IN, start, end)


class SelfCheckinsOpenTests(SelfCheckinsTestMixin, TestCase):

    def assertOpen(self, expected):  # noqa: N802
        self.assertIs(self_checkins_open(Tournament.objects.get(pk=self.tournament.pk)), expected)

    def test_closed_when_self_checkins_disabled(self):
        self.tournament.preferences['data_entry__public_checkins_submit'] = False
        self.add_checkin_event(-10, 10)
        self.assertOpen(False)

    def test_always_open_when_not_scheduled(self):
        self.tournament.preferences['data_entry__public_checkins_submit_scheduled'] = False
        self.assertOpen(True)

    def test_closed_without_checkin_events(self):
        self.add_event(ScheduleEvent.Types.DEBATE, -10, 10)
        self.assertOpen(False)

    def test_open_during_checkin_event(self):
        self.add_checkin_event(-10, 10)
        self.assertOpen(True)

    def test_closed_before_checkin_event(self):
        self.add_checkin_event(10, 20)
        self.assertOpen(False)

    def test_closed_after_checkin_event(self):
        self.add_checkin_event(-20, -10)
        self.assertOpen(False)

    def test_open_during_any_checkin_event(self):
        self.add_checkin_event(-60 * 24, -60 * 24 + 30)
        self.add_checkin_event(-10, 10)
        self.add_checkin_event(60 * 24, 60 * 24 + 30)
        self.assertOpen(True)

    def test_other_events_do_not_open_self_checkins(self):
        self.add_event(ScheduleEvent.Types.BRIEFING, -10, 10)
        self.add_event(ScheduleEvent.Types.OTHER, -10)
        self.assertOpen(False)

    def test_checkin_event_overlapping_other_events_stays_open_until_its_end(self):
        self.add_checkin_event(-20, 20)
        self.add_event(ScheduleEvent.Types.BRIEFING, -10, 10)
        self.assertOpen(True)

    def test_open_ended_checkin_event_open_until_next_event(self):
        self.add_checkin_event(-10)
        self.add_event(ScheduleEvent.Types.BRIEFING, 10, 20)
        self.assertOpen(True)

    def test_open_ended_checkin_event_open_without_later_events(self):
        self.add_checkin_event(-10)
        self.assertOpen(True)

    def test_open_ended_checkin_event_open_with_simultaneous_event(self):
        self.add_checkin_event(-10)
        self.add_event(ScheduleEvent.Types.OTHER, -10)
        self.assertOpen(True)

    def test_open_ended_checkin_event_closed_after_next_event_starts(self):
        self.add_checkin_event(-20)
        self.add_event(ScheduleEvent.Types.BRIEFING, -10, 10)
        self.assertOpen(False)

    def test_open_ended_checkin_event_closed_after_next_event_ends(self):
        self.add_checkin_event(-30)
        self.add_event(ScheduleEvent.Types.BRIEFING, -20, -10)
        self.assertOpen(False)

    def test_other_tournaments_events_ignored(self):
        other = Tournament.objects.create(slug="other")
        ScheduleEvent.objects.create(tournament=other, type=ScheduleEvent.Types.CHECK_IN,
            start_time=self.now - timedelta(minutes=10))
        self.assertOpen(False)


class ParticipantSelfCheckinViewTestMixin(SelfCheckinsTestMixin):

    def setUp(self):
        super().setUp()
        self.adjudicator = Adjudicator.objects.filter(tournament=self.tournament).first()
        self.adjudicator.url_key = 'selfcheckinkey'
        self.adjudicator.save()
        self.identifier = PersonIdentifier.objects.create(person=self.adjudicator)

    def landing_url(self):
        return reverse_tournament('privateurls-person-index', self.tournament,
            kwargs={'url_key': self.adjudicator.url_key})

    def submit(self, action):
        url = reverse_tournament('checkins-public-submit', self.tournament,
            kwargs={'url_key': self.adjudicator.url_key})
        return self.client.post(url, {'action': action}, follow=True)


class ScheduledParticipantSelfCheckinViewTests(ParticipantSelfCheckinViewTestMixin, TestCase):

    def test_checkin_accepted_while_open(self):
        self.add_checkin_event(-10, 10)
        response = self.submit('checkin')
        self.assertContains(response, "You are now checked in.")
        self.assertTrue(Event.objects.filter(identifier=self.identifier).exists())

    def test_checkin_rejected_while_closed(self):
        self.add_checkin_event(-20, -10)
        response = self.submit('checkin')
        self.assertContains(response, "Self check-in is currently closed.")
        self.assertFalse(Event.objects.filter(identifier=self.identifier).exists())

    def test_revoke_rejected_while_closed(self):
        Event.objects.create(identifier=self.identifier, tournament=self.tournament)
        response = self.submit('revoke')
        self.assertContains(response, "Self check-in is currently closed.")
        self.assertTrue(Event.objects.filter(identifier=self.identifier).exists())

    def test_landing_page_shows_form_while_open(self):
        self.add_checkin_event(-10, 10)
        response = self.client.get(self.landing_url())
        self.assertTrue(response.context['self_checkins_open'])
        self.assertContains(response, 'class="checkInForm"')
        self.assertNotContains(response, "Self check-in is currently closed.")

    def test_landing_page_shows_status_while_closed(self):
        Event.objects.create(identifier=self.identifier, tournament=self.tournament)
        response = self.client.get(self.landing_url())
        self.assertFalse(response.context['self_checkins_open'])
        self.assertNotContains(response, 'class="checkInForm"')
        self.assertContains(response, "Self check-in is currently closed.")
        self.assertContains(response, "You have been checked in at")


class UnscheduledParticipantSelfCheckinViewTests(ParticipantSelfCheckinViewTestMixin, TestCase):

    scheduled = False

    def test_checkin_accepted_outside_checkin_events(self):
        self.add_checkin_event(-20, -10)
        response = self.submit('checkin')
        self.assertContains(response, "You are now checked in.")
        self.assertTrue(Event.objects.filter(identifier=self.identifier).exists())

    def test_revoke_accepted_outside_checkin_events(self):
        Event.objects.create(identifier=self.identifier, tournament=self.tournament)
        response = self.submit('revoke')
        self.assertContains(response, "You have revoked your check-in.")
        self.assertFalse(Event.objects.filter(identifier=self.identifier).exists())

    def test_landing_page_shows_form_outside_checkin_events(self):
        response = self.client.get(self.landing_url())
        self.assertTrue(response.context['self_checkins_open'])
        self.assertContains(response, 'class="checkInForm"')
        self.assertNotContains(response, "Self check-in is currently closed.")
