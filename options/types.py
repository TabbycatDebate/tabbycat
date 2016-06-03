from dynamic_preferences.types import BasePreferenceType

from .fields import MultiValueChoiceField
from .serializers import MultiValueSerializer


class MultiValueChoicePreference(BasePreferenceType):

    choices = ()
    nfields = 5
    allow_empty = False
    field_class = MultiValueChoiceField
    serializer = MultiValueSerializer

    def get_field_kwargs(self):
        field_kwargs = super(MultiValueChoicePreference, self).get_field_kwargs()
        field_kwargs['nfields'] = self.nfields
        field_kwargs['choices'] = self.choices or self.field_attribute['initial']
        field_kwargs['allow_empty'] = self.allow_empty
        return field_kwargs
