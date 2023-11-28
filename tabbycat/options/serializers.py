from dynamic_preferences.serializers import MultipleSerializer


class MultiValueSerializer(MultipleSerializer):
    separator = "//"
    sort = False
