from django.db.models import Prefetch, Q
from dynamic_preferences.api.serializers import PreferenceSerializer
from dynamic_preferences.api.viewsets import PerInstancePreferenceViewSet
from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.viewsets import ModelViewSet

from options.models import TournamentPreferenceModel
from participants.models import Institution, Speaker
from standings.base import Standings
from tournaments.mixins import TournamentFromUrlMixin
from tournaments.models import Tournament

from . import serializers
from .mixins import AdministratorAPIMixin, PublicAPIMixin, TournamentAPIMixin, TournamentPublicAPIMixin


class APIRootView(PublicAPIMixin, GenericAPIView):
    name = "API Root"
    lookup_field = 'slug'
    lookup_url_kwarg = 'tournament_slug'

    def get(self, request, format=None):
        tournaments_create_url = reverse('api-tournament-list', request=request, format=format)
        institution_create_url = reverse('api-global-institution-list', request=request, format=format)
        return Response({
            "_links": {
                "tournaments": tournaments_create_url,
                "institutions": institution_create_url,
            },
        })


class TournamentViewSet(PublicAPIMixin, ModelViewSet):
    # Don't use TournamentAPIMixin here, it's not filtering objects by tournament.
    queryset = Tournament.objects.all()
    serializer_class = serializers.TournamentSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'tournament_slug'


class TournamentPreferenceViewSet(TournamentFromUrlMixin, AdministratorAPIMixin, PerInstancePreferenceViewSet):
    queryset = TournamentPreferenceModel.objects.all()
    serializer_class = PreferenceSerializer

    def get_related_instance(self):
        return self.tournament


class RoundViewSet(TournamentAPIMixin, PublicAPIMixin, ModelViewSet):
    serializer_class = serializers.RoundSerializer
    lookup_field = 'seq'
    lookup_url_kwarg = 'round_seq'

    def get_queryset(self):
        return self.tournament.round_set.all()


class BreakCategoryViewSet(TournamentAPIMixin, PublicAPIMixin, ModelViewSet):
    serializer_class = serializers.BreakCategorySerializer


class SpeakerCategoryViewSet(TournamentAPIMixin, PublicAPIMixin, ModelViewSet):
    serializer_class = serializers.SpeakerCategorySerializer


class BreakEligibilityView(TournamentAPIMixin, TournamentPublicAPIMixin, RetrieveUpdateAPIView):
    serializer_class = serializers.BreakEligibilitySerializer
    access_preference = 'public_break_categories'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('team_set')


class SpeakerEligibilityView(TournamentAPIMixin, TournamentPublicAPIMixin, RetrieveUpdateAPIView):
    serializer_class = serializers.SpeakerEligibilitySerializer
    access_preference = 'public_participants'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('speaker_set')


class InstitutionViewSet(TournamentAPIMixin, TournamentPublicAPIMixin, ModelViewSet):
    serializer_class = serializers.InstitutionSerializer
    access_preference = 'public_institutions_list'

    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        return Institution.objects.filter(
            Q(adjudicator__tournament=self.tournament) | Q(team__tournament=self.tournament),
        ).distinct().prefetch_related(
            Prefetch('team_set', queryset=self.tournament.team_set.all()),
            Prefetch('adjudicator_set', queryset=self.tournament.adjudicator_set.all()),
        )


class TeamViewSet(TournamentAPIMixin, TournamentPublicAPIMixin, ModelViewSet):
    serializer_class = serializers.TeamSerializer
    access_preference = 'public_participants'


class AdjudicatorViewSet(TournamentAPIMixin, TournamentPublicAPIMixin, ModelViewSet):
    serializer_class = serializers.AdjudicatorSerializer
    access_preference = 'public_participants'


class GlobalInstitutionViewSet(AdministratorAPIMixin, ModelViewSet):
    serializer_class = serializers.InstitutionSerializer

    def get_queryset(self):
        return Institution.objects.all()


class SpeakerViewSet(TournamentAPIMixin, TournamentPublicAPIMixin, ModelViewSet):
    serializer_class = serializers.SpeakerSerializer
    tournament_field = "team__tournament"
    access_preference = 'public_participants'

    def perform_create(self, serializer):
        serializer.save()


class VenueViewSet(TournamentAPIMixin, PublicAPIMixin, ModelViewSet):
    serializer_class = serializers.VenueSerializer


class VenueCategoryViewSet(TournamentAPIMixin, PublicAPIMixin, ModelViewSet):
    serializer_class = serializers.VenueCategorySerializer


class BaseStandingsView(TournamentAPIMixin, TournamentPublicAPIMixin, GenericAPIView):
    lookup_field = 'slug'
    lookup_url_kwarg = 'tournament_slug'


class SpeakerStandingsView(BaseStandingsView):
    name = "Speaker Standings"
    access_preference = 'speaker_tab_released'

    def get(self, request, format=None):
        speakers = Speaker.objects.filter(team__tournament=self.tournament)
        return Response(serializers.SpeakerStandingsSerializer(data=Standings(speakers)))


class TeamStandingsView(BaseStandingsView):
    name = 'Team Standings'
    access_preference = 'team_tab_released'

    def get(self, request, format=None):
        teams = self.tournament.team_set.all()
        return Response(serializers.TeamStandingsSerializer(data=Standings(teams)))
