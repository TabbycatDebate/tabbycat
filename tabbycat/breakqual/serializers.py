from rest_framework import serializers

from .models import BreakCategory


class BreakCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BreakCategory
        fields = ('id', 'name', 'seq')
