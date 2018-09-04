from contextlib import contextmanager
import json
import logging

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from django.test import Client, tag, TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from draw.models import DebateTeam
from tournaments.models import Tournament
from participants.models import Adjudicator, Institution, Speaker, Team
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


class TournamentTestsMixin:
    """Mixin that provides methods for testing a populated view on a tournament,
    with a prepopulated database."""

    fixtures = ['completed_demo.json']
    round_seq = None

    def identify_tournament(self):
        return Tournament.objects.first()

    def setUp(self):
        super().setUp()
        self.t = self.identify_tournament()
        self.client = Client()

    def get_view_url(self, provided_view_name):
        return reverse(provided_view_name, kwargs=self.get_url_kwargs())

    def get_url_kwargs(self):
        kwargs = {'tournament_slug': self.identify_tournament().slug}
        if self.round_seq is not None:
            kwargs['round_seq'] = self.round_seq
        return kwargs

    def get_response(self):
        cache.clear() # overriding the CACHE setting itself isn't enough
        return self.client.get(self.get_view_url(self.view_name), kwargs=self.get_url_kwargs())


class TournamentViewDoesLoadTest(TournamentTestsMixin):
    """For testing that a given view_name will merely load"""

    def test_response(self):
        response = self.get_response()
        self.assertEqual(response.status_code, 200)


class AssistantTournamentViewDoesLoadTest(TournamentTestsMixin):
    """For testing that a given view_name will merely load properly with auth"""

    def test_authenticated_response(self):
        get_user_model().objects.create_user('testb', 'b@gmail.com', 'pwd',
                                             is_staff=True)
        self.client.login(username='testb', password='pwd')

        self.assertEqual(self.get_response().status_code, 200)

    def test_unauthenticated_response(self):
        self.assertEqual(self.get_response().status_code, 302) # Redirect to login


class AdminTournamentViewDoesLoadTest(TournamentTestsMixin):
    """For testing that a given view_name will merely load properly with auth"""

    def test_authenticated_response(self):
        get_user_model().objects.create_superuser('testa', 'a@a.com', 'pwd')
        self.client.login(username='testa', password='pwd')

        self.assertEqual(self.get_response().status_code, 200)

    def test_unauthenticated_response(self):
        self.assertEqual(self.get_response().status_code, 302) # Redirect to login


class ConditionalTournamentTestsMixin(TournamentTestsMixin):
    """Mixin that provides tests for testing a view class that is conditionally
    shown depending on whether a user preference is set.

    Subclasses must inherit from TestCase separately. This can't be a TestCase
    subclass, because it provides tests which would be run on the base class."""

    view_toggle = None
    view_toggle_on = None  # Otherwise will assign True as the set state
    view_toggle_off = None  # Otherwise False as the config's unset state

    def validate_response(self, response):
        raise NotImplementedError

    def test_set_preference(self):
        # Check a page IS resolving when the preference is set
        if self.view_toggle_on is None:
            self.t.preferences[self.view_toggle] = True
        else:
            self.t.preferences[self.view_toggle] = self.view_toggle_on

        response = self.get_response()

        # 200 OK should be issued if setting is not enabled
        self.assertEqual(response.status_code, 200)
        self.validate_response(response)

    def test_unset_preference(self):
        # Check a page is not resolving when the preference is not set
        if self.view_toggle_off is None:
            self.t.preferences[self.view_toggle] = False
        else:
            self.t.preferences[self.view_toggle] = self.view_toggle_off

        with self.assertLogs('tournaments.mixins', logging.WARNING):
            response = self.get_response()

        # 403 (permission denied) should be issued if setting is not enabled
        self.assertEqual(response.status_code, 403)


class ConditionalTournamentViewLoadTest(ConditionalTournamentTestsMixin):
    """Simply checks the view and only fails if an error is thrown"""

    def validate_response(self, response):
        return True


class TournamentTestCase(TournamentTestsMixin, TestCase):
    """Extension of django.test.TestCase that provides methods for testing a
    populated view on a tournament, with a prepopulated database.
    Selenium tests can't inherit from this otherwise fixtures wont be loaded;
    as per https://stackoverflow.com/questions/12041315/how-to-have-django-test-case-and-selenium-server-use-same-database"""
    pass


class TableViewTestsMixin:
    """Mixin that provides methods for validating row counts in table views.
    Subclasses must override `expected_row_counts()`.
    """

    # This can't be a TestCase subclass, because it is inherited by
    # ConditionalTableViewTestsMixin, which provides tests.

    def validate_response(self, response):
        self.validate_row_counts(response)

    @staticmethod
    def get_table_data(response):
        return json.loads(response.context.get('tables_data', '[]'))

    def validate_row_counts(self, response):
        data = self.get_table_data(response)
        for count, table in zip(self.expected_row_counts(), data):
            self.assertNotEqual(count, 0)  # check the test isn't vacuous
            self.assertEqual(count, len(table['data']))

    def expected_row_counts(self):
        raise NotImplementedError


class ConditionalTableViewTestsMixin(TableViewTestsMixin, ConditionalTournamentTestsMixin):
    """Combination of TableViewTestsMixin and ConditionalTournamentTestsMixin,
    for convenience."""


class BaseDebateTestCase(TestCase):
    """Currently used in availability and participants tests as a pseudo fixture
    to create the basic data to simulate simple tournament functions"""

    def setUp(self):
        super().setUp()
        # add test models
        self.t = Tournament.objects.create(slug="tournament")
        for i in range(4):
            ins = Institution.objects.create(code="INS%s" % i, name="Institution %s" % i)
            for j in range(3):
                t = Team.objects.create(tournament=self.t, institution=ins,
                         reference="Team%s%s" % (i, j))
                for k in range(2):
                    Speaker.objects.create(team=t, name="Speaker%s%s%s" % (i, j, k))
            for j in range(2):
                Adjudicator.objects.create(tournament=self.t, institution=ins,
                                           name="Adjudicator%s%s" % (i, j), test_score=0)

        for i in range(8):
            Venue.objects.create(name="Venue %s" % i, priority=i, tournament=self.t)
            Venue.objects.create(name="IVenue %s" % i, priority=i)

    def tearDown(self):
        DebateTeam.objects.all().delete()
        Institution.objects.all().delete()
        self.t.delete()


@tag('selenium') # Exclude from Travis
class SeleniumTestCase(StaticLiveServerTestCase):
    """Used to verify rendered html and javascript functionality on the site as
    rendered. Opens a Chrome window and checks for JS/DOM state on the fixture
    debate."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Capabilities provide access to JS console
        capabilities = DesiredCapabilities.CHROME
        capabilities['loggingPrefs'] = {'browser':'ALL'}
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


class SeleniumTournamentTestCase(TournamentTestsMixin, SeleniumTestCase):
    """ Basically reimplementing BaseTournamentTest; but use cls not self """

    set_preferences = None
    unset_preferences = None

    def setUp(self):
        super().setUp()
        if self.set_preferences:
            for pref in self.set_preferences:
                self.t.preferences[pref] = True
        if self.unset_preferences:
            for pref in self.unset_preferences:
                self.t.preferences[pref] = False
