from rest_framework import serializers

from utils.misc import reverse_round

from .models import Round, Tournament


class RoundSerializer(serializers.ModelSerializer):
    back_url = serializers.SerializerMethodField()

    def get_back_url(self, obj):
        return reverse_round('draw', obj)

    class Meta:
        model = Round
        fields = ('seq', 'stage', 'draw_type', 'back_url')


class TournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = ('slug', 'sides')
