from unittest.mock import patch

from django.test import TestCase

from options.preferences import SpeakerStandingsPrecedence, TeamStandingsPrecedence


class PrefValidationTests(TestCase):

    @patch('options.preferences.validate_metric_duplicates')
    def test_validation_runs(self, mock_validate_metric_duplicates):
        for pref in (SpeakerStandingsPrecedence, TeamStandingsPrecedence):
            with self.subTest(preference=pref.name):
                self.assertIsNone(pref().validate([]))
