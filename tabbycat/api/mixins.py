from rest_framework.permissions import IsAdminUser

from tournaments.mixins import RoundFromUrlMixin, TournamentFromUrlMixin

from .permissions import IsAdminOrReadOnly, PublicPreferencePermission


class TournamentAPIMixin(TournamentFromUrlMixin):
    tournament_field = 'tournament'
    access_setting = True

    def lookup_kwargs(self):
        return {self.tournament_field: self.tournament}

    def perform_create(self, serializer):
        serializer.save(**self.lookup_kwargs())

    def get_queryset(self):
        return self.get_serializer_class().Meta.model.objects.filter(**self.lookup_kwargs())

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['tournament'] = self.tournament
        return context


class RoundAPIMixin(TournamentAPIMixin, RoundFromUrlMixin):
    tournament_field = 'round__tournament'
    round_field = 'round'

    def perform_create(self, serializer):
        serializer.save(**{self.round_field: self.round})

    def lookup_kwargs(self):
        kwargs = super().lookup_kwargs()
        kwargs[self.round_field] = self.round
        return kwargs

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['round'] = self.round
        return context


class AdministratorAPIMixin:
    permission_classes = [IsAdminUser]


class TournamentPublicAPIMixin:
    permission_classes = [PublicPreferencePermission]


class PublicAPIMixin:
    permission_classes = [IsAdminOrReadOnly]
