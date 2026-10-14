"""Test settings shared by Django and live-server tests."""

from django.conf import settings
from django.test import override_settings
from django.test.runner import DiscoverRunner


class TabbycatTestRunner(DiscoverRunner):
    def setup_test_environment(self, **kwargs):
        # Cache-clearing tests must retain sessions; pages need no production manifest.
        self.test_settings = override_settings(
            SESSION_ENGINE='django.contrib.sessions.backends.db',
            STORAGES={**settings.STORAGES,
                'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'}},
        )
        self.test_settings.enable()
        super().setup_test_environment(**kwargs)

    def teardown_test_environment(self, **kwargs):
        try:
            super().teardown_test_environment(**kwargs)
        finally:
            self.test_settings.disable()
