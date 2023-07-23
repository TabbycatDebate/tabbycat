from dynamic_preferences.types import ChoicePreference

from .fields import MultiValueChoiceField
from .serializers import MultiValueSerializer


class MultiValueChoicePreference(ChoicePreference):

    nfields = 5
    allow_empty = False
    field_class = MultiValueChoiceField
    serializer = MultiValueSerializer

    def get_field_kwargs(self):
        field_kwargs = super().get_field_kwargs()
        field_kwargs['nfields'] = self.nfields
        field_kwargs['allow_empty'] = self.allow_empty
        return field_kwargs

    def validate(self, value):
        for v in value:
            super().validate(v)
