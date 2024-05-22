import operator

from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser

from actionlog.mixins import LogActionMixin
from actionlog.models import ActionLogEntry
from tournaments.models import Round, Tournament

from .permissions import APIEnabledPermission, IsAdminOrReadOnly, PerTournamentPermissionRequired, PublicIfReleasedPermission, PublicPreferencePermission


class APILogActionMixin(LogActionMixin):
    action_log_content_object_attr = 'obj'

    def perform_create(self, serializer):
        self.obj = serializer.save(**self.lookup_kwargs())
        self.log_action(type=self.action_log_type_created, agent=ActionLogEntry.Agent.API)

    def perform_update(self, serializer):
        self.obj = serializer.save()
        self.log_action(type=self.action_log_type_updated, agent=ActionLogEntry.Agent.API)

    def lookup_kwargs(self):
        return {}


class TournamentAPIMixin(APILogActionMixin):
    tournament_field = 'tournament'

    access_operator = operator.eq
    access_setting = True

    @property
    def tournament(self):
        if not hasattr(self, "_tournament"):
            self._tournament = get_object_or_404(Tournament, slug=self.kwargs['tournament_slug'])
        return self._tournament

    def lookup_kwargs(self):
        return {self.tournament_field: self.tournament}

    def get_queryset(self):
        return self.get_serializer_class().Meta.model.objects.filter(**self.lookup_kwargs()).select_related(self.tournament_field)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['tournament'] = self.tournament
        return context


class RoundAPIMixin(TournamentAPIMixin):
    tournament_field = 'round__tournament'
    round_field = 'round'

    @property
    def round(self):
        if not hasattr(self, "_round"):
            self._round = get_object_or_404(Round, tournament=self.tournament, seq=self.kwargs['round_seq'])
        return self._round

    def lookup_kwargs(self):
        return {self.round_field: self.round}

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['round'] = self.round
        return context


class AdministratorAPIMixin:
    permission_classes = [APIEnabledPermission, IsAdminUser | PerTournamentPermissionRequired]


class TournamentPublicAPIMixin:
    permission_classes = [APIEnabledPermission, PublicPreferencePermission | PerTournamentPermissionRequired]


class OnReleasePublicAPIMixin(TournamentPublicAPIMixin):
    permission_classes = [APIEnabledPermission, PublicIfReleasedPermission | PerTournamentPermissionRequired]


class PublicAPIMixin:
    permission_classes = [APIEnabledPermission, IsAdminOrReadOnly | PerTournamentPermissionRequired]
