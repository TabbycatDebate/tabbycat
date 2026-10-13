"""Test settings shared by Django and live-server tests."""

from django.conf import settings
from django.test import override_settings
from django.test.runner import DiscoverRunner


class TabbycatTestRunner(DiscoverRunner):
    def setup_test_environment(self, **kwargs):
        # Rendering pages should not require a production collectstatic manifest.
        self.storage_settings = override_settings(STORAGES={**settings.STORAGES,
            'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'}})
        self.storage_settings.enable()
        super().setup_test_environment(**kwargs)

    def teardown_test_environment(self, **kwargs):
        try:
            super().teardown_test_environment(**kwargs)
        finally:
            self.storage_settings.disable()
