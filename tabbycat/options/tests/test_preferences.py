import unittest
from unittest.mock import patch

from django.forms import ValidationError

from options.preferences import SpeakerStandingsPrecedence, TeamStandingsPrecedence


class PrefValidationTests(unittest.TestCase):

    @patch('options.preferences.validate_metric_duplicates')
    def test_allow_empty(self, mock_validate_metric_duplicates):
        for preference in (SpeakerStandingsPrecedence, TeamStandingsPrecedence):
            with self.subTest(preference=preference):
                self.assertIsNone(preference().validate([]))

    @patch('options.preferences.validate_metric_duplicates')
    def test_disallow_wrong_value(self, mock_validate_metric_duplicates):
        for preference in (SpeakerStandingsPrecedence, TeamStandingsPrecedence):
            with self.subTest(preference=preference), self.assertRaises(ValidationError):
                preference().validate(['invalidkey'])

    @patch('options.preferences.validate_metric_duplicates')
    def test_number_of_fields(self, mock_validate_metric_duplicates):
        for preference in (SpeakerStandingsPrecedence, TeamStandingsPrecedence):
            with self.subTest(preference=preference):
                self.assertEqual(preference().get_field_kwargs()['nfields'], preference.nfields)
