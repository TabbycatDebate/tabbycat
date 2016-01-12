from django import forms
from dynamic_preferences.types import BasePreferenceType
from dynamic_preferences.serializers import BaseSerializer

class FloatSerializer(BaseSerializer):

    @classmethod
    def clean_to_db_value(cls, value):
        if not isinstance(value, float):
            raise cls.exception('FloatSerializer can only serialize Float instances')
        return value

    @classmethod
    def to_python(cls, value, **kwargs):
        try:
            return float(value)
        except float.InvalidOperation:
            raise cls.exception("Value {0} cannot be converted to float".format(value))


class FloatPreference(BasePreferenceType):

    field_class = forms.FloatField
    serializer = FloatSerializer

