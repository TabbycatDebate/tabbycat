import json
from django.core.urlresolvers import reverse
from django.test import Client, TestCase

from tournaments.models import Tournament

class TableViewTest(TestCase):

    fixtures = ['completed_demo.json']

    def setUp(self):
        self.t = Tournament.objects.first()
        self.client = Client()

class AdminTableViewTest(TableViewTest):

    admin_view_name = None

    def test(self):
        response = self.client.get(reverse(self.admin_view_name,
           kwargs={'tournament_slug': self.t.slug, 'round_seq': 3}))

        # 200 OK should be issued if setting is not enabled
        self.assertEqual(response.status_code, 200)

class PublicTableViewTest(TableViewTest):

    def test_set_preference(self):
        # Check a page IS resolving when the preference is set
        self.t.preferences[self.view_toggle] = True

        response = self.client.get(reverse(self.public_view_name,
            kwargs={'tournament_slug': self.t.slug, 'round_seq': 3}))

        # 200 OK should be issued if setting is not enabled
        self.assertEqual(response.status_code, 200)

        if hasattr(response.context, 'tableData') and hasattr(self, 'validate_table_data'):
            data = len(json.loads(response.context['tableData']))
            self.assertEqual(self.validate_table_data, data)
        if hasattr(response.context, 'tableDataA') and hasattr(self, 'validate_table_data_a'):
            data_a = len(json.loads(response.context['tableDataA']))
            self.assertEqual(self.validate_table_data_a(), data_a)
            data_b = len(json.loads(response.context['tableDataB']))
            self.assertEqual(self.validate_table_data_b(), data_b)

    def test_unset_preference(self):
        # Check a page is not resolving when the preference is not set
        self.t.preferences[self.view_toggle] = False

        response = self.client.get(reverse(self.public_view_name,
           kwargs={'tournament_slug': self.t.slug, 'round_seq': 3}))

        # 302 redirect shoould be issued if setting is not enabled
        self.assertEqual(response.status_code, 302)


