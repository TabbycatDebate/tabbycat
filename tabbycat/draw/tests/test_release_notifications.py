import json
from unittest.mock import Mock, patch

from django.contrib.messages.storage.fallback import FallbackStorage
from django.http import HttpResponseRedirect
from django.test import override_settings, RequestFactory, SimpleTestCase

from draw.views import DrawReleaseView, DrawStatusEdit
from tournaments.models import Round
from utils.misc import reverse_tournament


class DrawReleaseNotificationTests(SimpleTestCase):

    def setUp(self):
        self.request = RequestFactory().post('/draw/release/')
        self.request.session = {}
        self.request._messages = FallbackStorage(self.request)
        self.view = DrawReleaseView()
        self.view.request = self.request
        self.view._tournament_from_url = Mock(slug='test', short_name='Test')
        self.view.round = Mock(draw_status=Round.Status.CONFIRMED, name='Round 1')

    @override_settings(ENABLE_PUSH_NOTIFICATIONS=True)
    def test_notification_failure_does_not_fail_draw_release(self):
        error = RuntimeError('Push service unavailable')
        with (
            patch.object(self.view, 'send_push_notifications', side_effect=error),
            patch.object(self.view, 'log_action'),
            patch.object(DrawStatusEdit, 'post', return_value=HttpResponseRedirect('/draw/')),
            self.assertLogs('draw.views', level='ERROR') as logs,
        ):
            response = self.view.post(self.request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.view.round.draw_status, Round.Status.RELEASED)
        self.view.round.save.assert_called_once_with()
        self.assertIs(logs.records[0].exc_info[1], error)
        self.assertIn('Released the draw.', [str(message) for message in self.request._messages])

    def test_push_notifications_link_to_adjudicator_and_speaker_private_urls(self):
        adjudicator_device = Mock(language='en')
        speaker_device = Mock(language='en')
        adjudicator = Mock(url_key='adjudicator-key')
        adjudicator.participantwebpushdevice_set.all.return_value = [adjudicator_device]
        speaker = Mock(url_key='speaker-key')
        speaker.participantwebpushdevice_set.all.return_value = [speaker_device]
        debate_team = Mock()
        debate_team.team.speaker_set.all.return_value = [speaker]
        debate = Mock(matchup='Team A vs Team B')
        debate.debateadjudicator_set.all.return_value = [Mock(adjudicator=adjudicator, type='C', get_type_display=lambda: 'Chair')]
        debate_team.get_side_name.return_value = 'Government'
        debate.debateteam_set.all.return_value = [debate_team]
        debate.venue.display_name = 'Room 1'
        self.view.round.debate_set.select_related.return_value.prefetch_related.return_value.all.return_value = [debate]

        with patch('draw.views.use_team_code_names', return_value=False):
            self.view.send_push_notifications()

        for device, url_key in [(adjudicator_device, 'adjudicator-key'), (speaker_device, 'speaker-key')]:
            device.send_message.assert_called_once()
            payload = json.loads(device.send_message.call_args.kwargs['message'])
            self.assertEqual(payload['url'], self.request.build_absolute_uri(reverse_tournament(
                'privateurls-person-index', self.view.tournament, kwargs={'url_key': url_key},
            )))
