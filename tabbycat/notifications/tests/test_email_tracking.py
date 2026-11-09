import base64
import json
import os
import runpy
from datetime import datetime, timezone
from unittest.mock import patch

from anymail.exceptions import AnymailAPIError
from anymail.signals import AnymailTrackingEvent, tracking
from django.conf import settings
from django.core import mail
from django.test import override_settings, SimpleTestCase, TestCase

from notifications.consumers import NotificationQueueConsumer
from notifications.email_tracking import send_with_retry
from notifications.models import BulkNotification, EmailStatus, SentMessage
from participants.models import Adjudicator
from tournaments.models import Tournament

EMAIL_SETTINGS_PATH = os.path.join(settings.BASE_DIR, 'settings', 'email.py')


class EmailSettingsTests(SimpleTestCase):

    def load_settings(self, **env):
        with patch.dict(os.environ, env, clear=True):
            return runpy.run_path(EMAIL_SETTINGS_PATH)

    def test_no_email_config(self):
        result = self.load_settings()
        self.assertNotIn('EMAIL_BACKEND', result)
        self.assertNotIn('EMAIL_HOST', result)
        self.assertEqual(result['ANYMAIL'], {})

    def test_email_provider_uses_anymail(self):
        result = self.load_settings(
            EMAIL_PROVIDER='Brevo', ANYMAIL_BREVO_API_KEY='key', ANYMAIL_WEBHOOK_SECRET='user:pass',
            DEFAULT_FROM_EMAIL='tab@example.com',
        )
        self.assertEqual(result['EMAIL_BACKEND'], 'anymail.backends.brevo.EmailBackend')
        self.assertEqual(result['EMAIL_PROVIDER'], 'brevo')
        self.assertEqual(result['ANYMAIL'], {'BREVO_API_KEY': 'key', 'WEBHOOK_SECRET': 'user:pass'})
        self.assertEqual(result['DEFAULT_FROM_EMAIL'], 'tab@example.com')

    def test_email_provider_takes_precedence(self):
        result = self.load_settings(
            EMAIL_PROVIDER='amazon-ses', EMAIL_HOST='smtp.example.com', SENDGRID_API_KEY='SG.key',
        )
        self.assertEqual(result['EMAIL_BACKEND'], 'anymail.backends.amazon_ses.EmailBackend')
        self.assertNotIn('EMAIL_HOST', result)

    def test_smtp_config_unchanged(self):
        result = self.load_settings(
            EMAIL_HOST='smtp.example.com', EMAIL_HOST_USER='user', EMAIL_HOST_PASSWORD='pass',
            DEFAULT_FROM_EMAIL='tab@example.com', SENDGRID_API_KEY='SG.key',
        )
        self.assertNotIn('EMAIL_BACKEND', result)
        self.assertEqual(result['EMAIL_HOST'], 'smtp.example.com')
        self.assertEqual(result['EMAIL_HOST_USER'], 'user')
        self.assertEqual(result['EMAIL_PORT'], 587)
        self.assertTrue(result['EMAIL_USE_TLS'])

    def test_sendgrid_api_key_config_unchanged(self):
        result = self.load_settings(SENDGRID_API_KEY='SG.key', DEFAULT_FROM_EMAIL='tab@example.com')
        self.assertNotIn('EMAIL_BACKEND', result)
        self.assertEqual(result['EMAIL_HOST'], 'smtp.sendgrid.net')
        self.assertEqual(result['EMAIL_HOST_USER'], 'apikey')
        self.assertEqual(result['EMAIL_HOST_PASSWORD'], 'SG.key')

    def test_legacy_sendgrid_config_unchanged(self):
        result = self.load_settings(SENDGRID_USERNAME='user', SENDGRID_PASSWORD='pass')
        self.assertTrue(result['USING_LEGACY_SENDGRID_CONFIG_VARS'])
        self.assertEqual(result['EMAIL_HOST'], 'smtp.sendgrid.net')
        self.assertEqual(result['DEFAULT_FROM_EMAIL'], 'user')


class EmailTrackingTestMixin:

    def setUp(self):
        self.tournament = Tournament.objects.create(
            name="Email Test Tournament", short_name="Email Test", slug="email-test",
        )
        self.recipient = Adjudicator.objects.create(
            tournament=self.tournament, name="Recipient", email="recipient@example.com", url_key="recipient",
        )

    def send_notification(self):
        NotificationQueueConsumer().email({
            'type': 'email',
            'message': BulkNotification.EventType.URL,
            'extra': {
                'tournament_id': self.tournament.id,
                'url': 'https://example.com/private/',
            },
            'send_to': [self.recipient.id],
            'subject': 'Private URL for {{ USER }}',
            'body': 'Your URL is {{ URL }}',
        })
        return SentMessage.objects.get()


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class SMTPEmailTrackingTests(EmailTrackingTestMixin, TestCase):

    def test_sendgrid_hook_id_header(self):
        record = self.send_notification()
        message = mail.outbox[0]
        self.assertEqual(json.loads(message.extra_headers['X-SMTPAPI']),
                         {'unique_args': {'hook-id': record.hook_id}})
        self.assertEqual(message.extra_headers['X-RECORDID'], str(record.id))
        self.assertIsNone(record.esp_message_id)


@override_settings(EMAIL_BACKEND='anymail.backends.test.EmailBackend', EMAIL_PROVIDER='test')
class AnymailEmailTrackingTests(EmailTrackingTestMixin, TestCase):

    def send_tracking_event(self, **kwargs):
        event = AnymailTrackingEvent(timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
                                     recipient=self.recipient.email, **kwargs)
        tracking.send(sender=object, event=event, esp_name="Test")

    def test_metadata_and_esp_message_id_recorded(self):
        record = self.send_notification()
        message = mail.outbox[0]
        self.assertEqual(message.metadata, {'hook_id': record.hook_id})
        self.assertNotIn('X-SMTPAPI', message.extra_headers)
        self.assertEqual(record.esp_message_id, '0')
        self.assertFalse(record.emailstatus_set.exists())

    def test_tracking_event_matched_by_hook_id(self):
        record = self.send_notification()
        self.send_tracking_event(event_type='delivered', message_id='other', metadata={'hook_id': record.hook_id})
        status = record.emailstatus_set.get()
        self.assertEqual(status.event, EmailStatus.EventType.DELIVERED)
        self.assertEqual(status.data['esp'], "Test")
        self.assertEqual(status.data['recipient'], self.recipient.email)

    def test_tracking_event_matched_by_esp_message_id(self):
        record = self.send_notification()
        self.send_tracking_event(event_type='bounced', message_id=record.esp_message_id,
                                 reject_reason='bounced', mta_response='550 No such user')
        status = record.emailstatus_set.get()
        self.assertEqual(status.event, EmailStatus.EventType.BOUNCED)
        self.assertEqual(status.data['mta_response'], '550 No such user')

    @override_settings(ANYMAIL={'WEBHOOK_SECRET': 'user:pass'})
    def test_provider_webhook_records_status(self):
        record = self.send_notification()
        payload = [{
            'email': self.recipient.email, 'timestamp': 1767225600, 'event': 'delivered',
            'sg_message_id': 'abc.123', 'hook_id': record.hook_id,
        }]
        response = self.client.post('/anymail/sendgrid/tracking/', json.dumps(payload), content_type='application/json',
                                    HTTP_AUTHORIZATION='Basic ' + base64.b64encode(b'user:pass').decode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(record.emailstatus_set.get().event, EmailStatus.EventType.DELIVERED)

    @override_settings(ANYMAIL={'WEBHOOK_SECRET': 'user:pass'}, STORAGES={
        **settings.STORAGES, 'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'}})
    def test_provider_webhook_requires_secret(self):
        response = self.client.post('/anymail/sendgrid/tracking/', '[]', content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_unknown_tracking_events_ignored(self):
        record = self.send_notification()
        self.send_tracking_event(event_type='autoresponded', metadata={'hook_id': record.hook_id})
        self.send_tracking_event(event_type='delivered', message_id='unknown-message')
        self.assertFalse(EmailStatus.objects.exists())

    @patch('notifications.email_tracking.sleep')
    def test_rate_limited_send_is_retried(self, mock_sleep):
        connection = mail.get_connection()
        message = mail.EmailMessage(to=['recipient@example.com'])
        responses = [AnymailAPIError(status_code=429), None]

        def send_messages(messages):
            response = responses.pop(0)
            if response is not None:
                raise response
            return 1

        with patch.object(connection, 'send_messages', side_effect=send_messages) as mock_send:
            send_with_retry(connection, message)
        self.assertEqual(mock_send.call_count, 2)
        mock_sleep.assert_called_once_with(1)

    def test_other_provider_errors_not_retried(self):
        connection = mail.get_connection()
        message = mail.EmailMessage(to=['recipient@example.com'])
        with patch.object(connection, 'send_messages', side_effect=AnymailAPIError(status_code=400)) as mock_send:
            with self.assertRaises(AnymailAPIError):
                send_with_retry(connection, message)
        self.assertEqual(mock_send.call_count, 1)

    def test_provider_error_recorded_as_failed(self):
        with patch('anymail.backends.test.EmailBackend.send_messages', side_effect=AnymailAPIError("Invalid API key")):
            record = self.send_notification()
        status = record.emailstatus_set.get()
        self.assertEqual(status.event, EmailStatus.EventType.FAILED)
        self.assertIn("Invalid API key", status.data['error'])
