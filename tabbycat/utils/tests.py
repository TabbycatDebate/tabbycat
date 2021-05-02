import json
import logging
from contextlib import contextmanager
from unittest import expectedFailure

from django.contrib.auth import get_user, get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.cache import cache
from django.test import Client, tag, TestCase
from django.urls import reverse
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from draw.models import DebateTeam
from participants.models import Adjudicator, Institution, Speaker, Team
from tournaments.models import Tournament
from utils.misc import add_query_string_parameter, reverse_tournament
from venues.models import Venue

logger = logging.getLogger(__name__)


@contextmanager
def suppress_logs(name, level, returnto=logging.NOTSET):
    """Suppresses logging at or below `level` from the logger named `name` while
    in the context manager. The name of the logger must be provided, and as a
    matter of practice should be as specific as possible, to avoid overly
    suppressing logs.

    Usage:
        import logging
        from utils.tests import suppress_logs

        with suppress_logs('results.result', logging.WARNING): # or other level
            # test code
    """
    if '.' not in name and returnto == logging.NOTSET:
        logger.warning("Top-level modules (%s) should not be passed to suppress_logs", name)

    suppressed_logger = logging.getLogger(name)
    suppressed_logger.setLevel(level+1)
    yield
    suppressed_logger.setLevel(returnto)


class CompletedTournamentTestMixin:
    """Mixin providing a few convenience functions for tests:
      - Loads a completed demonstration tournament
      - Assumes URLs are from said tournament and, optionally, a particular round
    """

    fixtures = ['after_round_4.json']
    round_seq = None
    use_post = False

    def get_tournament(self):
        return Tournament.objects.first()

    def setUp(self):
        super().setUp()
        self.tournament = self.get_tournament()
        if self.round_seq is not None:
            self.round = self.tournament.round_set.get(seq=self.round_seq)
        self.client = Client()

    def reverse_url(self, view_name, **kwargs):
        """Convenience function for reversing a URL for the demo tournament,
        and the round if one is specified in the class."""
        if self.round_seq is not None:
            kwargs.setdefault('round_seq', self.round_seq)
        return reverse_tournament(view_name, self.tournament, kwargs=kwargs)

    def get_response(self, view_name, use_post=False, **kwargs):
        cache.clear()
        url = self.reverse_url(view_name, **kwargs)
        return self.client.get(url)

    def assertResponseOK(self, response):  # noqa: N802
        if response.status_code in [301, 302]:
            self.fail("View %r gave response with status code %d, redirecting "
                      "to %s (expected 200)" %
                      (self.view_name, response.status_code, response.url))
        elif response.status_code != 200:
            self.fail("View %r gave response with status code %d (expected 200)" %
                      (self.view_name, response.status_code))

    def assertResponsePermissionDenied(self, response):  # noqa: N802
        self.assertEqual(response.status_code, 403)


class SingleViewTestMixin(CompletedTournamentTestMixin):
    """Mixin for TestCases relating to a single view."""

    view_name = None
    view_reverse_kwargs = {}

    def get_view_reverse_kwargs(self):
        return self.view_reverse_kwargs.copy()

    def get_response(self):
        kwargs = self.get_view_reverse_kwargs()
        response = super().get_response(self.view_name, **kwargs)
        return response


class TournamentViewSimpleLoadTestMixin(SingleViewTestMixin):

    def test_response(self):
        response = self.get_response()
        self.assertResponseOK(response)


class AuthenticatedTournamentViewSimpleLoadTextMixin(SingleViewTestMixin):

    def authenticate(self):
        raise NotImplementedError

    @expectedFailure
    def test_authenticated_response(self):
        self.authenticate()
        response = self.get_response()
        self.assertResponseOK(response)

    def test_unauthenticated_response(self):
        self.client.logout()
        response = self.get_response()
        target_url = self.reverse_url(self.view_name, **self.get_view_reverse_kwargs())
        login_url = reverse('login')
        expected_url = add_query_string_parameter(login_url, 'next', target_url)
        self.assertRedirects(response, expected_url)  # in django.test.SimpleTestCase


class AssistantTournamentViewSimpleLoadTestMixin(AuthenticatedTournamentViewSimpleLoadTextMixin):
    """Mixin for testing that assistant pages resolve when user is logged in,
    and don't when user is logged out."""

    def authenticate(self):
        user, _ = get_user_model().objects.get_or_create(username='test_assistant')
        self.client.force_login(user)

        # Double-check authentication, raise error if it looks wrong
        if not get_user(self.client).is_authenticated:
            raise RuntimeError("User authentication failed")


class AdminTournamentViewSimpleLoadTestMixin(AuthenticatedTournamentViewSimpleLoadTextMixin):
    """Mixin for testing that admin pages resolve when user is logged in, and
    don't when user is logged out."""

    def authenticate(self):
        user, _ = get_user_model().objects.get_or_create(username='test_admin', is_superuser=True)
        self.client.force_login(user)

        # Double-check authentication, raise error if it looks wrong
        user = get_user(self.client)
        if not user.is_authenticated:
            raise RuntimeError("User authentication failed")
        if not user.is_superuser:
            raise RuntimeError("User is not a superuser")


class ConditionalTournamentTestsMixin(SingleViewTestMixin):
    """Mixin that provides tests for testing a view class that is conditionally
    shown depending on whether a user preference is set.

    Subclasses must inherit from TestCase separately. This can't be a TestCase
    subclass, because it provides tests which would be run on the base class."""

    view_toggle_preference = None
    view_toggle_on_value = True
    view_toggle_off_value = False

    def validate_response(self, response):
        raise NotImplementedError

    def test_view_enabled(self):
        values = getattr(self, 'view_toggle_on_values', [self.view_toggle_on_value])
        for value in values:
            with self.subTest(value=value):
                self.tournament.preferences[self.view_toggle_preference] = value
                response = self.get_response()
                self.assertResponseOK(response)
                self.validate_response(response)

    def test_view_disabled(self):
        values = getattr(self, 'view_toggle_off_values', [self.view_toggle_off_value])
        for value in values:
            with self.subTest(value=value):
                self.tournament.preferences[self.view_toggle_preference] = value
                with self.assertLogs('tournaments.mixins', logging.WARNING):
                    with suppress_logs('django.request', logging.WARNING):
                        response = self.get_response()
                self.assertResponsePermissionDenied(response)


class ConditionalTournamentViewSimpleLoadTestMixin(ConditionalTournamentTestsMixin):
    """Simply checks the view and only fails if an error is thrown"""

    def validate_response(self, response):
        pass


class TournamentTestCase(SingleViewTestMixin, TestCase):
    """Extension of django.test.TestCase that provides methods for testing a
    populated view on a tournament, with a prepopulated database.
    Selenium tests can't inherit from this otherwise fixtures wont be loaded;
    as per https://stackoverflow.com/questions/12041315/how-to-have-django-test-case-and-selenium-server-use-same-database"""
    pass


class TableViewTestsMixin:
    """Mixin providing utility functions for table views."""

    def get_table_data(self, response):
        self.assertIn('tables_data', response.context)
        return json.loads(response.context['tables_data'])

    def assertNoTables(self, response):  # noqa: N802
        data = self.get_table_data(response)
        self.assertEqual(len(data), 0)

    def assertResponseTableRowCountsEqual(self, response, counts, allow_vacuous=False):  # noqa: N802
        data = self.get_table_data(response)
        self.assertEqual(len(counts), len(data))
        for count, table in zip(counts, data):
            if not allow_vacuous:
                self.assertNotEqual(count, 0)  # check the test isn't vacuous
            self.assertEqual(count, len(table['data']))


class ConditionalTableViewTestsMixin(TableViewTestsMixin, ConditionalTournamentTestsMixin):
    """Combination of TableViewTestsMixin and ConditionalTournamentTestsMixin,
    for convenience."""

    def validate_response(self, response):
        counts = self.expected_row_counts()
        self.assertResponseTableRowCountsEqual(response, counts)

    def expected_row_counts(self):
        raise NotImplementedError


class BaseMinimalTournamentTestCase(TestCase):
    """Currently used in availability and participants tests as a pseudo fixture
    to create the basic data to simulate simple tournament functions"""

    def setUp(self):
        super().setUp()
        # add test models
        self.tournament = Tournament.objects.create(slug="tournament")
        for i in range(4):
            ins = Institution.objects.create(code="INS%s" % i, name="Institution %s" % i)
            for j in range(3):
                t = Team.objects.create(tournament=self.tournament, institution=ins,
                         reference="Team%s%s" % (i, j))
                for k in range(2):
                    Speaker.objects.create(team=t, name="Speaker%s%s%s" % (i, j, k))
            for j in range(2):
                Adjudicator.objects.create(tournament=self.tournament, institution=ins,
                                           name="Adjudicator%s%s" % (i, j), base_score=0)

        for i in range(8):
            Venue.objects.create(name="Venue %s" % i, priority=i, tournament=self.tournament)
            Venue.objects.create(name="IVenue %s" % i, priority=i)

    def tearDown(self):
        DebateTeam.objects.all().delete()
        Institution.objects.all().delete()
        self.tournament.delete()


@tag('selenium') # Tagged so we can exclude from CI
class SeleniumTestCase(StaticLiveServerTestCase):
    """Used to verify rendered html and javascript functionality on the site as
    rendered. Opens a Chrome window and checks for JS/DOM state on the fixture
    debate."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Capabilities provide access to JS console
        capabilities = DesiredCapabilities.CHROME
        capabilities['loggingPrefs'] = {'browser': 'ALL'}
        cls.selenium = WebDriver(desired_capabilities=capabilities)
        cls.selenium.implicitly_wait(10)

    def test_no_js_errors(self):
        # Check console for errors; fail the test if so
        for entry in self.selenium.get_log('browser'):
            if entry['level'] == 'SEVERE':
                raise RuntimeError('Page loaded in selenium has a JS error')

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()


class SeleniumTournamentTestCase(SingleViewTestMixin, SeleniumTestCase):
    """ Basically reimplementing BaseTournamentTest; but use cls not self """

    set_preferences = None
    unset_preferences = None

    def setUp(self):
        super().setUp()
        if self.set_preferences:
            for pref in self.set_preferences:
                self.tournament.preferences[pref] = True
        if self.unset_preferences:
            for pref in self.unset_preferences:
                self.tournament.preferences[pref] = False
