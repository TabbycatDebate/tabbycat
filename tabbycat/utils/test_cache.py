from types import SimpleNamespace
from unittest.mock import patch

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from django.test import override_settings, RequestFactory, SimpleTestCase
from django.utils.cache import patch_vary_headers
from django.views import View

from .mixins import CacheMixin


@override_settings(
    ALLOWED_HOSTS=['testserver', 'other.test'],
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}},
)
class PageCacheTests(SimpleTestCase):
    def setUp(self):
        cache.clear()
        self.factory = RequestFactory()

    def tearDown(self):
        cache.clear()

    def make_view(self, timeout, personalize=False):
        class PublicView(CacheMixin, View):
            cache_timeout = timeout
            calls = 0

            def get(self, request):
                PublicView.calls += 1
                response = HttpResponse(str(PublicView.calls))
                if personalize:
                    response.set_cookie('sessionid', 'private')
                    patch_vary_headers(response, ['Cookie'])
                return response

        return PublicView.as_view()

    def test_subclass_timeout_controls_expiry(self):
        for timeout in (5, 210, 7200):
            with self.subTest(timeout=timeout):
                cache.clear()
                view = self.make_view(timeout)
                with patch('django.core.cache.backends.locmem.time.time', return_value=100):
                    self.assertEqual(view(self.factory.get('/')).content, b'1')
                with patch('django.core.cache.backends.locmem.time.time', return_value=100 + timeout - 1):
                    self.assertEqual(view(self.factory.get('/')).content, b'1')
                with patch('django.core.cache.backends.locmem.time.time', return_value=101 + timeout):
                    self.assertEqual(view(self.factory.get('/')).content, b'2')

    def test_cache_is_separate_for_each_host(self):
        view = self.make_view(210)
        self.assertEqual(view(self.factory.get('/', HTTP_HOST='testserver')).content, b'1')
        self.assertEqual(view(self.factory.get('/', HTTP_HOST='other.test')).content, b'2')
        self.assertEqual(view(self.factory.get('/', HTTP_HOST='testserver')).content, b'1')

    def test_cookie_setting_response_is_not_shared_with_new_visitors(self):
        view = self.make_view(210, personalize=True)
        self.assertEqual(view(self.factory.get('/')).content, b'1')
        self.assertEqual(view(self.factory.get('/')).content, b'2')

    def test_authenticated_visitors_neither_read_nor_populate_public_cache(self):
        view = self.make_view(210)
        authenticated = self.factory.get('/')
        authenticated.user = SimpleNamespace(is_authenticated=True)
        self.assertEqual(view(authenticated).content, b'1')
        self.assertEqual(view(self.factory.get('/')).content, b'2')
        self.assertEqual(view(authenticated).content, b'3')
        self.assertEqual(view(self.factory.get('/')).content, b'2')

    def test_session_and_authorization_requests_bypass_public_cache(self):
        view = self.make_view(210)
        self.assertEqual(view(self.factory.get('/')).content, b'1')
        for headers in ({'HTTP_COOKIE': f'{settings.SESSION_COOKIE_NAME}=abc'},
                        {'HTTP_AUTHORIZATION': 'Bearer secret'}):
            with self.subTest(headers=headers):
                self.assertNotEqual(view(self.factory.get('/', **headers)).content, b'1')
        self.assertEqual(view(self.factory.get('/')).content, b'1')

    def test_browser_must_revalidate_even_with_long_server_cache_lifetime(self):
        response = self.make_view(7200)(self.factory.get('/'))
        self.assertIn('no-store', response['Cache-Control'])
        self.assertIn('private', response['Cache-Control'])

    def test_template_responses_are_cached_before_browser_cache_headers_are_added(self):
        from django.template import engines
        from django.template.response import SimpleTemplateResponse

        class PublicView(CacheMixin, View):
            calls = 0

            def get(self, request):
                PublicView.calls += 1
                return SimpleTemplateResponse(
                    engines['django'].from_string('{{ value }}'), {'value': PublicView.calls},
                )

        view = PublicView.as_view()
        for _ in range(2):
            response = view(self.factory.get('/')).render()
            self.assertEqual(response.content, b'1')
            self.assertIn('no-store', response['Cache-Control'])

    @override_settings(DISABLE_SENTRY=True)
    def test_disabling_public_page_still_blocks_previously_cached_response(self):
        from tournaments.mixins import PublicTournamentPageMixin

        release = {'enabled': True}

        class PublicView(PublicTournamentPageMixin, View):
            public_page_preference = 'released'
            tournament = SimpleNamespace(current_round=object(), pref=lambda name: release['enabled'])

            def get(self, request):
                return HttpResponse('public results')

        view = PublicView.as_view()
        self.assertEqual(view(self.factory.get('/')).status_code, 200)
        release['enabled'] = False
        self.assertEqual(view(self.factory.get('/')).status_code, 403)
