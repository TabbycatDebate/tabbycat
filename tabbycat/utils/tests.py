from contextlib import contextmanager
import json
import logging

from django.core.urlresolvers import reverse
from django.test import Client, override_settings, TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.chrome.webdriver import WebDriver

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

    def get_tournament(self):
        return Tournament.objects.first()

    def setUp(self):
        super().setUp()
        self.t = self.get_tournament()
        self.client = Client()

    def get_view_url(self, provided_view_name):
        return reverse(provided_view_name, kwargs=self.get_url_kwargs())

    def get_url_kwargs(self):
        t = self.get_tournament()
        kwargs = {'tournament_slug': t.slug}
        if self.round_seq is not None:
            kwargs['round_seq'] = self.round_seq
        return kwargs

    @override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
    def get_response(self):
        with self.modify_settings(
            # Remove whitenoise middleware as it won't resolve on Travis
            MIDDLEWARE={'remove': ['whitenoise.middleware.WhiteNoiseMiddleware']}
        ):
            return self.client.get(self.get_view_url(self.view_name), kwargs=self.get_url_kwargs())


class ConditionalTournamentTestsMixin(TournamentTestsMixin):
    """Mixin that provides tests for testing a view class that is conditionally
    shown depending on whether a user preference is set.

    Subclasses must inherit from TestCase separately. This can't be a TestCase
    subclass, because it provides tests which would be run on the base class."""

    view_toggle = None

    def validate_response(self, response):
        raise NotImplementedError

    def test_set_preference(self):
        # Check a page IS resolving when the preference is set
        self.t.preferences[self.view_toggle] = True
        response = self.get_response()

        # 200 OK should be issued if setting is not enabled
        self.assertEqual(response.status_code, 200)
        self.validate_response(response)

    def test_unset_preference(self):
        # Check a page is not resolving when the preference is not set
        self.t.preferences[self.view_toggle] = False

        with self.assertLogs('tournaments.mixins', logging.WARNING):
            response = self.get_response()

        # 302 redirect should be issued if setting is not enabled
        self.assertEqual(response.status_code, 302)


class ConditionalTournamentViewBasicCheckMixin(ConditionalTournamentTestsMixin):
    """Simply checks the view and only fails if an error is thrown"""

    def validate_response(self, response):
        return True


class TournamentTestCase(TournamentTestsMixin, TestCase):
    """Extension of django.test.TestCase that provides methods for testing a
    populated view on a tournament, with a prepopulated database."""
    pass


class TableViewTestsMixin:
    """Mixin that provides methods for validating data in table views.
    Subclasses should override the `table_data` methods."""

    # This can't be a TestCase subclass, because it is inherited by
    # ConditionalTableViewTestsMixin, which provides tests.

    def validate_response(self, response):
        self.validate_table_data(response)

    def validate_table_data(self, r):
        if 'tableData' in r.context and self.table_data():
            data = len(json.loads(r.context['tableData']))
            self.assertEqual(self.table_data(), data)

        if 'tableDataA' in r.context and self.table_data_a():
            data_a = len(json.loads(r.context['tableDataA']))
            self.assertEqual(self.table_data_a(), data_a)

        if 'tableDataB' in r.context and self.table_data_b():
            data_b = len(json.loads(r.context['tableDataB']))
            self.assertEqual(self.table_data_b(), data_b)

    def table_data(self):
        return False

    def table_data_a(self):
        return False

    def table_data_b(self):
        return False



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


class SeleniumTestCase(StaticLiveServerTestCase):
    """Used to verify rendered html and javascript functionality on the site as
    rendered. Opens a Chrome window and checks for JS/DOM state on the fixture
    debate."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()


class SeleniumTournamentTestCase(TournamentTestCase, SeleniumTestCase):
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
