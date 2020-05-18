from django.db.models import Count, Prefetch, Q
from dynamic_preferences.api.serializers import PreferenceSerializer
from dynamic_preferences.api.viewsets import PerInstancePreferenceViewSet
from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.viewsets import ModelViewSet

from adjfeedback.models import AdjudicatorFeedbackQuestion
from options.models import TournamentPreferenceModel
from participants.models import Institution, Speaker
from standings.base import Standings
from tournaments.mixins import TournamentFromUrlMixin
from tournaments.models import Round, Tournament

from . import serializers
from .mixins import AdministratorAPIMixin, PublicAPIMixin, RoundAPIMixin, TournamentAPIMixin, TournamentPublicAPIMixin
from .permissions import APIEnabledPermission, PublicPreferencePermission


class APIRootView(PublicAPIMixin, GenericAPIView):
    name = "API Root"

    def get(self, request, format=None):
        return Response({
            "_links": {
                "v1": reverse('api-v1-root', request=request, format=format),
            },
        })


class APIV1RootView(PublicAPIMixin, GenericAPIView):
    name = "API Version 1 Root"
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
    queryset = Tournament.objects.all().prefetch_related(
        'breakcategory_set',
        Prefetch('round_set',
            queryset=Round.objects.filter(completed=False).annotate(Count('debate')),
            to_attr='current_round_set'),
    )
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
        return super().get_queryset().prefetch_related('motion_set')


class MotionViewSet(TournamentAPIMixin, AdministratorAPIMixin, ModelViewSet):
    """Administrator-access as may include unreleased motions."""
    serializer_class = serializers.MotionSerializer
    tournament_field = 'round__tournament'


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
    serializer_class = serializers.PerTournamentInstitutionSerializer
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

    def get_queryset(self):
        return super().get_queryset().select_related('tournament').prefetch_related(
            Prefetch('speaker_set', queryset=Speaker.objects.all().prefetch_related('categories', 'categories__tournament').select_related('team__tournament')))


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

    def get_queryset(self):
        return super().get_queryset().select_related('tournament').prefetch_related('venuecategory_set', 'venuecategory_set__tournament')


class VenueCategoryViewSet(TournamentAPIMixin, PublicAPIMixin, ModelViewSet):
    serializer_class = serializers.VenueCategorySerializer

    def get_queryset(self):
        return super().get_queryset().select_related('tournament').prefetch_related('venues', 'venues__tournament')


class BaseStandingsView(TournamentAPIMixin, TournamentPublicAPIMixin, GenericAPIView):
    lookup_field = 'slug'
    lookup_url_kwarg = 'tournament_slug'

    def get_category_filter(self):
        """Adds a filter for categories in subclasses"""
        category = self.request.query_params.get('category', None)
        if category is not None:
            return Q(categories__pk=category)
        return Q()

    def get(self, request, format=None):
        return Response(self.get_serializer(data=Standings(self.get_queryset())).data)


class SpeakerStandingsView(BaseStandingsView):
    name = "Speaker Standings"
    serializer_class = serializers.SpeakerStandingsSerializer
    access_preference = 'speaker_tab_released'

    def get_queryset(self):
        return Speaker.objects.filter(Q(team__tournament=self.tournament) & self.get_category_filter())


class TeamStandingsView(BaseStandingsView):
    name = 'Team Standings'
    serializer_class = serializers.TeamStandingsSerializer
    access_preference = 'team_tab_released'

    def get_queryset(self):
        return self.tournament.team_set.filter(self.get_category_filter())


class PairingViewSet(RoundAPIMixin, ModelViewSet):

    class Permission(PublicPreferencePermission):
        def get_tournament_preference(self, view, op):
            return {
                'off': False,
                'current': view.tournament.current_round.id == view.round.id and self.get_round_status(view),
                'all-released': self.get_round_status(view),
            }[view.tournament.pref(view.access_preference)]

        def get_round_status(self, view):
            return getattr(view.round, view.round_released_field) == view.round_released_value

    serializer_class = serializers.RoundPairingSerializer

    access_preference = 'public_draw'

    round_released_field = 'draw_status'
    round_released_value = Round.STATUS_RELEASED

    permission_classes = [APIEnabledPermission, Permission]

    def get_queryset(self):
        return super().get_queryset().select_related('round', 'round__tournament', 'venue', 'venue__tournament').prefetch_related(
            'debateteam_set', 'debateteam_set__team', 'debateteam_set__team__tournament',
            'debateadjudicator_set', 'debateadjudicator_set__adjudicator', 'debateadjudicator_set__adjudicator__tournament',
        )


class FeedbackQuestionViewSet(TournamentAPIMixin, PublicAPIMixin, ModelViewSet):
    serializer_class = serializers.FeedbackQuestionSerializer

    def get_queryset(self):
        q = super().get_queryset().filter()
        if self.request.query_params.get('from_adj'):
            q.filter(from_adj=True)
        if self.request.query_params.get('from_team'):
            q.filter(from_team=True)
        return q


class FeedbackViewSet(TournamentAPIMixin, AdministratorAPIMixin, ModelViewSet):
    serializer_class = serializers.FeedbackSerializer
    tournament_field = 'adjudicator__tournament'

    def get_queryset(self):
        answers_prefetch = [
            Prefetch(
                typ.__name__.lower() + "_set",
                queryset=typ.objects.all().select_related('question', 'question__tournament'),
                to_attr=typ.__name__,
            )
            for typ in AdjudicatorFeedbackQuestion.ANSWER_TYPE_CLASSES_REVERSE.keys()
        ]
        return super().get_queryset().select_related(
            'adjudicator', 'adjudicator__tournament',
            'source_adjudicator', 'source_team', 'source_team__team',
            'source_adjudicator__adjudicator__tournament', 'source_team__team__tournament',
            'source_adjudicator__debate', 'source_team__debate',
            'source_adjudicator__debate__round', 'source_team__debate__round',
            'source_adjudicator__debate__round__tournament', 'source_team__debate__round__tournament',
        ).prefetch_related(*answers_prefetch)
