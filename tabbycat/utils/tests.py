import json
import logging

from django.core.urlresolvers import reverse
from django.test import Client, override_settings, TestCase

from draw.models import DebateTeam
from tournaments.models import Tournament
from participants.models import Adjudicator, Institution, Speaker, Team
from venues.models import Venue


class BaseTableViewTest():
    """Base class for testing table views; provides a default fixture and
    methods for setting tournament/clients and validating data. If inheriting
    classes are validating data they should overwrite table_data methods"""

    fixtures = ['completed_demo.json']
    view_name = None
    round_seq = None

    def setUp(self):
        self.t = Tournament.objects.first()
        self.client = Client()

    @override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
    def get_response(self):
        with self.modify_settings(
            # Remove whitenoise middleware as it won't resolve on Travis
            MIDDLEWARE={
                'remove': [
                    'whitenoise.middleware.WhiteNoiseMiddleware',
                ],
            }
        ):
            return self.client.get(reverse(self.view_name, kwargs=self.get_url_kwargs()))

    def get_url_kwargs(self):
        kwargs = {'tournament_slug': self.t.slug}
        if self.round_seq is not None:
            kwargs['round_seq'] = self.round_seq
        return kwargs

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


class TableViewTest(BaseTableViewTest):
    """For testing a view class that is always available. Inheriting classes
    must also inherit from TestCase"""

    def test(self):
        response = self.get_response()
        # 200 OK should be issued if setting is not enabled
        self.assertEqual(response.status_code, 200)
        self.validate_table_data(response)


class ConditionalTableViewTest(BaseTableViewTest):
    """For testing a view class that is conditionally shown depending on a
    preference being set or not. Inheriting classes must also inherit from
    TestCase and provide a view_toggle as a dynamic preferences path"""

    view_toggle = None

    def test_set_preference(self):
        # Check a page IS resolving when the preference is set
        self.t.preferences[self.view_toggle] = True
        response = self.get_response()

        # 200 OK should be issued if setting is not enabled
        self.assertEqual(response.status_code, 200)
        self.validate_table_data(response)

    def test_unset_preference(self):
        # Check a page is not resolving when the preference is not set
        self.t.preferences[self.view_toggle] = False

        # Disable logging to silence the admin-page-only warning
        logging.disable(logging.CRITICAL)
        response = self.get_response()
        logging.disable(logging.NOTSET)

        # 302 redirect shoould be issued if setting is not enabled
        self.assertEqual(response.status_code, 302)


class BaseDebateTestCase(TestCase):
    """Currently used in availability and participants tests as a pseudo fixture
    to create the basic data to simulate simple tournament functions"""

    def setUp(self):
        super(BaseDebateTestCase, self).setUp()
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
