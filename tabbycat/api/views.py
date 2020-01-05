from dynamic_preferences.api.viewsets import PerInstancePreferenceViewSet
from dynamic_preferences.api.serializers import PreferenceSerializer
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser

from options.models import TournamentPreferenceModel
from tournaments.mixins import TournamentMixin

from participants.models import Institution,Speaker

from django.db.models import Prefetch

from . import serializers


class TournamentAPIMixin(TournamentMixin):
    tournament_field = 'tournament'

    def perform_create(self, serializer):
        serializer.save(**{self.tournament_field: self.tournament})

    def get_queryset(self):
        return self.serializer_class.Meta.model.objects.filter(**{self.tournament_field: self.tournament})

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['tournament'] = self.tournament
        return context


class AdministratorAPIMixin:
    permission_classes = [IsAdminUser]


class TournamentPreferenceViewSet(TournamentMixin, AdministratorAPIMixin, PerInstancePreferenceViewSet):
    queryset = TournamentPreferenceModel.objects.all()
    serializer_class = PreferenceSerializer

    def get_related_instance(self):
        return self.tournament


class BreakCategoryViewSet(TournamentAPIMixin, AdministratorAPIMixin, ModelViewSet):
    serializer_class = serializers.BreakCategorySerializer
    lookup_field = 'slug'


class SpeakerCategoryViewSet(TournamentAPIMixin, AdministratorAPIMixin, ModelViewSet):
    serializer_class = serializers.SpeakerCategorySerializer
    lookup_field = 'slug'


class BreakEligibilityView(TournamentAPIMixin, AdministratorAPIMixin, RetrieveUpdateAPIView):
    serializer_class = serializers.BreakEligibilitySerializer
    lookup_field = 'slug'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('team_set')


class SpeakerEligibilityView(TournamentAPIMixin, AdministratorAPIMixin, RetrieveUpdateAPIView):
    serializer_class = serializers.SpeakerEligibilitySerializer
    lookup_field = 'slug'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('speaker_set')


class InstitutionViewSet(TournamentAPIMixin, AdministratorAPIMixin, ModelViewSet):
    serializer_class = serializers.InstitutionSerializer

    def get_queryset(self):
        return Institution.objects.all().prefetch_related(Prefetch('team_set',queryset=self.tournament.team_set.all()))


class TeamViewSet(TournamentAPIMixin, AdministratorAPIMixin, ModelViewSet):
    serializer_class = serializers.TeamSerializer


class AdjudicatorViewSet(TournamentAPIMixin, AdministratorAPIMixin, ModelViewSet):
    serializer_class = serializers.AdjudicatorSerializer


class GlobalInstitutionViewSet(AdministratorAPIMixin, ModelViewSet):
    serializer_class = serializers.InstitutionSerializer

    def get_queryset(self):
        return Institution.objects.all()


class SpeakerViewSet(TournamentAPIMixin, AdministratorAPIMixin, ModelViewSet):
    serializer_class = serializers.SpeakerSerializer

    def get_queryset(self):
        return Speaker.objects.all()
