from unittest.mock import Mock, patch

from django.contrib.messages import get_messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory, TestCase

from notifications.forms import BasicEmailForm
from notifications.models import BulkNotification
from notifications.views import TemplateEmailCreateView
from participants.models import Adjudicator
from tournaments.models import Tournament


class TemplateEmailCreateViewTests(TestCase):

    def setUp(self):
        self.tournament = Tournament.objects.create(
            name="Email Test Tournament", short_name="Email Test", slug="email-test",
        )
        self.valid_recipient = Adjudicator.objects.create(
            tournament=self.tournament, name="Valid Recipient", email="valid@example.com",
        )
        self.invalid_recipient = Adjudicator.objects.create(
            tournament=self.tournament, name="Invalid Recipient", email="invalid@example.com\u200f",
        )

        self.request = RequestFactory().post('/')
        self.request.session = {}
        self.request._messages = FallbackStorage(self.request)

        self.view = TemplateEmailCreateView()
        self.view.request = self.request
        self.view._tournament_from_url = self.tournament

    def test_invalid_email_recipients_are_excluded_before_queueing(self):
        recipient_ids = self.view.get_valid_email_recipient_ids([
            self.valid_recipient.id, self.invalid_recipient.id,
        ])

        self.assertEqual(recipient_ids, [self.valid_recipient.id])
        message = list(get_messages(self.request))[0]
        self.assertIn(self.invalid_recipient.name, str(message))
        self.assertIn("not queued", str(message))

    @patch('notifications.views.get_channel_layer')
    @patch('notifications.views.async_to_sync')
    def test_form_only_queues_valid_email_recipients(self, mock_async_to_sync, mock_get_channel_layer):
        self.request.POST = self.request.POST.copy()
        self.request.POST.update({
            'subject_line': 'Test subject',
            'message_body': 'Test message',
        })
        self.request.POST.setlist('recipients', [
            str(self.valid_recipient.id), str(self.invalid_recipient.id),
        ])
        form = BasicEmailForm(self.request.POST)
        self.assertTrue(form.is_valid())

        sender = Mock()
        mock_async_to_sync.return_value = sender
        self.view.event = BulkNotification.EventType.CUSTOM
        self.view.get_extra = Mock(return_value={'tournament_id': self.tournament.id})
        self.view.get_success_url = Mock(return_value='/')

        self.view.form_valid(form)

        mock_async_to_sync.assert_called_once_with(mock_get_channel_layer.return_value.send)
        sender.assert_called_once()
        event = sender.call_args.args[1]
        self.assertEqual(event['send_to'], [self.valid_recipient.id])
