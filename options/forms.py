from django import forms
from dynamic_preferences.types import BasePreferenceType
from dynamic_preferences.serializers import BaseSerializer

class FloatSerializer(BaseSerializer):

    @classmethod
    def clean_to_db_value(cls, value):
        if not isinstance(value, float):
            raise cls.exception('FloatSerializer can only serialize float values')
        return value

    @classmethod
    def to_python(cls, value, **kwargs):
        try:
            return float(value)
        except:
            raise cls.exception("Value {0} cannot be converted to a float")


class FloatPreference(BasePreferenceType):

    field_class = forms.FloatField
    serializer = FloatSerializer

