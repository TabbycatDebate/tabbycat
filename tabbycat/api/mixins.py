from rest_framework.permissions import IsAdminUser

from tournaments.mixins import TournamentFromUrlMixin

from .permissions import IsAdminOrReadOnly, PublicPreferencePermission


class TournamentAPIMixin(TournamentFromUrlMixin):
    tournament_field = 'tournament'
    access_setting = True

    def perform_create(self, serializer):
        serializer.save(**{self.tournament_field: self.tournament})

    def get_queryset(self):
        return self.get_serializer_class().Meta.model.objects.filter(**{self.tournament_field: self.tournament})

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['tournament'] = self.tournament
        return context


class AdministratorAPIMixin:
    permission_classes = [IsAdminUser]


class TournamentPublicAPIMixin:
    permission_classes = [PublicPreferencePermission]


class PublicAPIMixin:
    permission_classes = [IsAdminOrReadOnly]
