import unittest
from unittest.mock import patch

from dynamic_preferences.forms import GlobalPreferenceForm

from options.forms import tournament_preference_form_builder


class FormBuilderTest(unittest.TestCase):

    @patch('options.forms.preference_form_builder')
    def test_create_global_form(self, mock_builder):
        tournament_preference_form_builder(None, section='global')
        mock_builder.assert_called_with(GlobalPreferenceForm, [], section='global')
