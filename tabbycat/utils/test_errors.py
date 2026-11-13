import sentry_sdk
from django.test import Client, override_settings, SimpleTestCase
from django.urls import get_resolver, path
from django.views.i18n import set_language
from rest_framework.views import APIView
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.transport import Transport

handler500 = get_resolver('urls').resolve_error_handler(500)


def failing_view(request):
    raise RuntimeError('deliberate failure')


class FailingAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        raise RuntimeError('deliberate failure')


urlpatterns = [
    path('html/', failing_view),
    path('api/', FailingAPIView.as_view()),
    path('i18n/setlang/', set_language, name='set_language'),
]


class EventTransport(Transport):
    def __init__(self, options):
        super().__init__(options)
        self.events = []

    def capture_envelope(self, envelope):
        event = envelope.get_event()
        if event:
            self.events.append(event)


@override_settings(
    DEBUG=False,
    ROOT_URLCONF=__name__,
    MIDDLEWARE=[],
    STORAGES={'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'}},
)
class ServerErrorTests(SimpleTestCase):
    def setUp(self):
        scope = sentry_sdk.get_global_scope()
        self.addCleanup(scope.set_client, scope.client)
        scope.set_client(None)

    def test_responses_include_reported_trace_id(self):
        with sentry_sdk.Client(
            dsn='https://public@example.com/1',
            integrations=[DjangoIntegration()],
            transport=EventTransport,
        ) as client:
            sentry_sdk.get_global_scope().set_client(client)
            for url in ('/api/', '/html/'):
                with self.subTest(url=url):
                    client.transport.events.clear()
                    response = Client(raise_request_exception=False).get(url)
                    self.assertEqual(response.status_code, 500)
                    self.assertTrue(client.transport.events)
                    trace_id = client.transport.events[0]['contexts']['trace']['trace_id']
                    if url == '/api/':
                        self.assertEqual(response.json()['sentry_trace_id'], trace_id)
                        self.assertEqual(response.json()['detail'], 'A server error occurred.')
                    else:
                        self.assertContains(response, f'<code>{trace_id}</code>', status_code=500)
                        self.assertContains(response, 'and the Sentry trace ID shown above in your post.', status_code=500)
                        self.assertContains(response, 'An error report has been sent to the developers of Tabbycat.', status_code=500)
                        self.assertNotContains(response, 'Heroku', status_code=500)
                        self.assertNotContains(response, 'Tabbykitten', status_code=500)
                        self.assertNotContains(response, 'github.com/TabbycatDebate/tabbycat/issues/new', status_code=500)
                        self.assertContains(response, 'https://www.facebook.com/groups/tabbycat.debate/', status_code=500)

    def test_responses_without_sentry(self):
        for url in ('/api/', '/html/'):
            with self.subTest(url=url):
                response = Client(raise_request_exception=False).get(url)
                self.assertEqual(response.status_code, 500)
                if url == '/api/':
                    self.assertEqual(response.json(), {'detail': 'A server error occurred.'})
                else:
                    self.assertNotContains(response, 'Sentry trace ID', status_code=500)
                    self.assertNotContains(response, 'An error report has been sent', status_code=500)
