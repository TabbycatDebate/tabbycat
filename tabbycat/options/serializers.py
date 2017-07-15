from dynamic_preferences.serializers import BaseSerializer


class MultiValueSerializer(BaseSerializer):

    separator = "//"

    @classmethod
    def clean_to_db_value(cls, value):
        if not isinstance(value, list):
            raise cls.exception('MultiValueSerializer can only serialize lists')
        value = [str(x) for x in value]
        if any([cls.separator in x for x in value]):
            raise cls.exception('The separator ({0!r}) must not be in lists passed to MultiValueSerializer'.format(cls.separator))
        return cls.separator.join(value)

    @classmethod
    def to_python(cls, value, **kwargs):
        if not value:
            return []
        try:
            return value.split(cls.separator)
        except AttributeError:
            raise cls.exception('MultiValueSerializer only deserializes strings separated by {0!r}'.format(cls.separator))
