from rest_framework.generics import CreateAPIView, GenericAPIView, RetrieveUpdateAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.reverse import reverse

from tournaments.models import Tournament
from tournaments.mixins import TournamentMixin

from participants.models import Institution

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


class APIRootView(AdministratorAPIMixin, GenericAPIView):
    name = "API Root"
    queryset = Tournament.objects.all()
    serializer_class = serializers.TournamentAtRootSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'tournament_slug'

    def get(self, request, format=None):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        tournaments_create_url = reverse('api-tournament-create', request=request, format=format)
        return Response({
            "tournaments": serializer.data,
            "urls": {"create_tournament": tournaments_create_url}
        })


class TournamentCreateView(CreateAPIView):
    queryset = Tournament.objects.all()
    serializer_class = serializers.TournamentSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'tournament_slug'


class TournamentDetailView(RetrieveUpdateAPIView):
    # Don't use TournamentAPIMixin here, it's not filtering objects by tournament.
    queryset = Tournament.objects.all()
    serializer_class = serializers.TournamentSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'tournament_slug'


class BreakCategoryViewSet(TournamentAPIMixin, AdministratorAPIMixin, ModelViewSet):
    serializer_class = serializers.BreakCategorySerializer
    lookup_field = 'slug'


class SpeakerCategoryViewSet(TournamentAPIMixin, AdministratorAPIMixin, ModelViewSet):
    serializer_class = serializers.SpeakerCategorySerializer
    lookup_field = 'slug'


class BreakEligibilityView(TournamentAPIMixin, AdministratorAPIMixin, RetrieveUpdateAPIView):
    serializer_class = serializers.BreakEligibilitySerializer
    lookup_field = 'slug'


class SpeakerEligibilityView(TournamentAPIMixin, AdministratorAPIMixin, RetrieveUpdateAPIView):
    serializer_class = serializers.SpeakerEligibilitySerializer
    lookup_field = 'slug'

class InstitutionViewSet(TournamentAPIMixin, AdministratorAPIMixin, ModelViewSet):
    serializer_class = serializers.InstitutionSerializer
    queryset = Institution.objects.all()
    def get_queryset(self):
        return Institution.objects.all()

class InstitutionViewSetCreateView(CreateAPIView):
    serializer_class = serializers.InstitutionSerializer

