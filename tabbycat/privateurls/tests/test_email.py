from django.contrib.messages import get_messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core import mail
from django.test import override_settings, RequestFactory, TestCase

from notifications.consumers import NotificationQueueConsumer
from notifications.models import BulkNotification
from participants.models import Adjudicator
from privateurls.views import EmailRandomisedUrlsView
from tournaments.models import Tournament


class PrivateUrlEmailTestMixin:

    def setUp(self):
        self.tournament = Tournament.objects.create(
            name="Email Test Tournament", short_name="Email Test", slug="email-test",
        )
        self.with_url = Adjudicator.objects.create(
            tournament=self.tournament, name="With URL", email="with-url@example.com", url_key="withurl",
        )
        self.without_url = Adjudicator.objects.create(
            tournament=self.tournament, name="Without URL", email="without-url@example.com",
        )


class EmailRandomisedUrlsViewTests(PrivateUrlEmailTestMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.request = RequestFactory().post('/')
        self.request.session = {}
        self.request._messages = FallbackStorage(self.request)

        self.view = EmailRandomisedUrlsView()
        self.view.request = self.request
        self.view._tournament_from_url = self.tournament

    def test_recipients_without_private_url_are_excluded_before_queueing(self):
        recipient_ids = self.view.get_valid_email_recipient_ids([self.with_url.id, self.without_url.id])

        self.assertEqual(recipient_ids, [self.with_url.id])
        message = str(list(get_messages(self.request))[0])
        self.assertIn(self.without_url.name, message)
        self.assertIn("not queued", message)

    def test_recipients_without_private_url_are_not_selected_by_default(self):
        default_send_ids = set(self.view.get_default_send_queryset().values_list('id', flat=True))
        self.assertIn(self.with_url.id, default_send_ids)
        self.assertNotIn(self.without_url.id, default_send_ids)


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class PrivateUrlEmailConsumerTests(PrivateUrlEmailTestMixin, TestCase):

    def test_recipient_without_private_url_does_not_prevent_other_emails_sending(self):
        NotificationQueueConsumer().email({
            'type': 'email',
            'message': BulkNotification.EventType.URL,
            'extra': {
                'tournament_id': self.tournament.id,
                'url': 'https://example.com/email-test/privateurls/',
            },
            'send_to': [self.with_url.id, self.without_url.id],
            'subject': 'Private URL for {{ USER }}',
            'body': 'Your URL is {{ URL }}',
        })

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['With URL <with-url@example.com>'])
        self.assertIn('https://example.com/email-test/privateurls/withurl/', mail.outbox[0].body)
