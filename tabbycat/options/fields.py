import logging

from django.forms import ChoiceField, MultiValueField, MultiWidget, Select

logger = logging.getLogger(__name__)

EMPTY_CHOICE = '__no_choice__'


class MultiSelect(MultiWidget):

    def __init__(self, nfields=5, choices=(), attrs=None):
        self.nfields = nfields
        widgets = [Select(choices=choices, attrs=attrs) for i in range(self.nfields)]
        super(MultiSelect, self).__init__(widgets, attrs)

    def render(self, name, value, attrs=None, renderer=None):
        # Extend to the appropriate number of values. Note that because
        # compress() compresses to a list, decompress() is not called by
        # MultiWidget.
        if len(value) < self.nfields:
            value.extend([EMPTY_CHOICE] * (self.nfields - len(value)))
        return super(MultiSelect, self).render(name, value, attrs=attrs)


class MultiValueChoiceField(MultiValueField):

    def __init__(self, *args, **kwargs):
        self.nfields = kwargs.pop('nfields', 5)
        allow_empty = kwargs.pop('allow_empty', False)

        choices = kwargs.pop('choices')
        choices = list(choices)
        if allow_empty:
            choices.insert(0, (EMPTY_CHOICE, '--------'))

        fields = tuple(ChoiceField(choices=choices) for i in range(self.nfields))
        self.widget = MultiSelect(nfields=self.nfields, choices=choices)
        super(MultiValueChoiceField, self).__init__(fields=fields, *args, **kwargs)

    def compress(self, data_list):
        """Removes empty items from the list."""
        result = [x for x in data_list if x != EMPTY_CHOICE]
        logger.debug("compressing: %s to %s", data_list, result)
        return result
