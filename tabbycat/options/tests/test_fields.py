import unittest
from unittest.mock import patch

from options.fields import EMPTY_CHOICE, MultiSelect, MultiValueChoiceField


class MultiWidgetTest(unittest.TestCase):

    @patch('options.fields.MultiWidget.render')
    def test_appends_empty_for_render(self, mock_render):
        MultiSelect(nfields=5).render('test', ['a'])
        mock_render.assert_called_with('test', ['a'] + ([EMPTY_CHOICE] * 4), attrs=None)


class MultiValueChoiceFieldTest(unittest.TestCase):

    def test_compresses_empty(self):
        field = MultiValueChoiceField(choices=[('a', 'a'), ('b', 'b')], allow_empty=True)
        self.assertEqual(
            field.compress(['a', EMPTY_CHOICE, 'b']),
            ['a', 'b'],
        )
