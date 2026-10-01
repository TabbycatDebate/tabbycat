from django.core import mail
from django.test import override_settings, TestCase

from notifications.consumers import NotificationQueueConsumer
from notifications.models import BulkNotification, EmailStatus, SentMessage
from participants.models import Adjudicator
from tournaments.models import Tournament


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class NotificationQueueConsumerTests(TestCase):

    def setUp(self):
        self.tournament = Tournament.objects.create(
            name="Email Test Tournament", short_name="Email Test", slug="email-test",
        )

    def test_invalid_email_does_not_prevent_other_emails_sending(self):
        valid_recipient = Adjudicator.objects.create(
            tournament=self.tournament, name="Valid Recipient",
            email="valid@example.com", url_key="valid-recipient",
        )
        invalid_recipient = Adjudicator.objects.create(
            tournament=self.tournament, name="Invalid Recipient",
            email="invalid@example.com\u200f", url_key="invalid-recipient",
        )

        NotificationQueueConsumer().email({
            'type': 'email',
            'message': BulkNotification.EventType.URL,
            'extra': {
                'tournament_id': self.tournament.id,
                'url': 'https://example.com/private/',
            },
            'send_to': [valid_recipient.id, invalid_recipient.id],
            'subject': 'Private URL for {{ USER }}',
            'body': 'Your URL is {{ URL }}',
        })

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['Valid Recipient <valid@example.com>'])

        notification = BulkNotification.objects.get()
        sent_messages = notification.sentmessage_set.order_by('recipient_id')
        self.assertEqual(sent_messages.count(), 2)

        valid_message = sent_messages.get(recipient=valid_recipient)
        self.assertIsNotNone(valid_message.message_id)
        self.assertFalse(valid_message.emailstatus_set.exists())

        invalid_message = sent_messages.get(recipient=invalid_recipient)
        self.assertIsNone(invalid_message.message_id)
        failed_status = invalid_message.emailstatus_set.get()
        self.assertEqual(failed_status.event, EmailStatus.EventType.FAILED)
        self.assertTrue(failed_status.data['error'])

        self.assertEqual(SentMessage.objects.count(), 2)
