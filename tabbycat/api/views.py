from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import Count, Prefetch, Q
from django.http.response import Http404
from dynamic_preferences.api.serializers import PreferenceSerializer
from dynamic_preferences.api.viewsets import PerInstancePreferenceViewSet
from rest_framework.exceptions import NotFound
from rest_framework.generics import GenericAPIView, get_object_or_404, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from adjfeedback.models import AdjudicatorFeedbackQuestion
from breakqual.models import BreakCategory
from breakqual.views import GenerateBreakMixin
from checkins.consumers import CheckInEventConsumer
from checkins.models import Event
from checkins.utils import create_identifiers, get_unexpired_checkins
from draw.models import Debate
from options.models import TournamentPreferenceModel
from participants.models import Adjudicator, Institution, Speaker, SpeakerCategory, Team
from standings.speakers import SpeakerStandingsGenerator
from standings.teams import TeamStandingsGenerator
from tournaments.mixins import TournamentFromUrlMixin
from tournaments.models import Round, Tournament
from venues.models import Venue

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
            queryset=Round.objects.filter(completed=False).annotate(Count('debate')).order_by('seq'),
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
    serializer_class = serializers.MotionSerializer
    tournament_field = 'round__tournament'


class BreakCategoryViewSet(TournamentAPIMixin, PublicAPIMixin, ModelViewSet):
    serializer_class = serializers.BreakCategorySerializer


class SpeakerCategoryViewSet(TournamentAPIMixin, PublicAPIMixin, ModelViewSet):
    serializer_class = serializers.SpeakerCategorySerializer

    def get_queryset(self):
        if not self.request.user or not self.request.user.is_staff:
            return super().get_queryset().filter(public=True)
        return super().get_queryset()


class BreakEligibilityView(TournamentAPIMixin, TournamentPublicAPIMixin, RetrieveUpdateAPIView):
    serializer_class = serializers.BreakEligibilitySerializer
    access_preference = 'public_break_categories'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('team_set')


class SpeakerEligibilityView(TournamentAPIMixin, TournamentPublicAPIMixin, RetrieveUpdateAPIView):
    serializer_class = serializers.SpeakerEligibilitySerializer
    access_preference = 'public_participants'

    def get_queryset(self):
        qs = super().get_queryset().prefetch_related('speaker_set')
        if not self.request.user or not self.request.user.is_staff:
            return qs.filter(public=True)
        return qs


class BreakingTeamsView(TournamentAPIMixin, TournamentPublicAPIMixin, GenerateBreakMixin, GenericViewSet):
    serializer_class = serializers.BreakingTeamSerializer
    tournament_field = 'break_category__tournament'
    access_preference = 'public_breaking_teams'

    @property
    def break_category(self):
        if self._break_category is None:
            self._break_category = get_object_or_404(BreakCategory, tournament=self.tournament, pk=self.kwargs.get('pk'))
        return self._break_category

    def get_queryset(self):
        return super().get_queryset().select_related('team', 'team__tournament').order_by('rank')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['break_category'] = self.break_category
        return context

    def list(self, request, *args, **kwargs):
        """Pagination might be dangerous here, so disabled."""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        self.generate_break((self.break_category,))
        return self.list(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Destroy is normally for a specific instance, now QuerySet."""
        self.filter_queryset(self.get_queryset()).delete()
        return Response(status=204)  # No content

    def update(self, request, *args, **kwargs):
        """Update team remark and then regenerate break."""
        serializer = serializers.PartialBreakingTeamSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return self.create(request, *args, **kwargs)


class InstitutionViewSet(TournamentAPIMixin, TournamentPublicAPIMixin, ModelViewSet):
    serializer_class = serializers.PerTournamentInstitutionSerializer
    access_preference = 'public_institutions_list'

    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        filters = Q()
        if self.request.query_params.get('region'):
            filters &= Q(region__name=self.request.query_params['region'])

        return Institution.objects.filter(
            Q(adjudicator__tournament=self.tournament) | Q(team__tournament=self.tournament),
            filters,
        ).distinct().select_related('region').prefetch_related(
            Prefetch('team_set', queryset=self.tournament.team_set.all()),
            Prefetch('adjudicator_set', queryset=self.tournament.adjudicator_set.all()),
        )


class TeamViewSet(TournamentAPIMixin, TournamentPublicAPIMixin, ModelViewSet):
    serializer_class = serializers.TeamSerializer
    access_preference = 'public_participants'

    def get_queryset(self):
        category_prefetch = Prefetch('categories', queryset=SpeakerCategory.objects.all().select_related('tournament'))
        if not self.request.user or not self.request.user.is_staff:
            category_prefetch.queryset = category_prefetch.queryset.filter(public=True)

        return super().get_queryset().select_related('tournament').prefetch_related(
            Prefetch(
                'speaker_set',
                queryset=Speaker.objects.all().prefetch_related(category_prefetch).select_related('team__tournament'),
            ),
            'institution_conflicts',
            'break_categories', 'break_categories__tournament',
        )


class AdjudicatorViewSet(TournamentAPIMixin, TournamentPublicAPIMixin, ModelViewSet):
    serializer_class = serializers.AdjudicatorSerializer
    access_preference = 'public_participants'

    def get_break_permission(self):
        return self.request.user.is_staff or self.tournament.pref('public_breaking_adjs')

    def get_queryset(self):
        filters = Q()
        if self.request.query_params.get('break') and self.get_break_permission():
            filters &= Q(breaking=True)

        return super().get_queryset().prefetch_related(
            'team_conflicts', 'team_conflicts__tournament',
            'adjudicator_conflicts', 'adjudicator_conflicts__tournament',
            'institution_conflicts',
        ).filter(filters)


class GlobalInstitutionViewSet(AdministratorAPIMixin, ModelViewSet):
    serializer_class = serializers.InstitutionSerializer

    def get_queryset(self):
        filters = Q()
        if self.request.query_params.get('region'):
            filters &= Q(region__name=self.request.query_params['region'])
        return Institution.objects.filter(filters).select_related('region')


class SpeakerViewSet(TournamentAPIMixin, TournamentPublicAPIMixin, ModelViewSet):
    serializer_class = serializers.SpeakerSerializer
    tournament_field = "team__tournament"
    access_preference = 'public_participants'

    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        category_prefetch = Prefetch('categories', queryset=SpeakerCategory.objects.all().select_related('tournament'))
        if not self.request.user or not self.request.user.is_staff:
            category_prefetch.queryset = category_prefetch.queryset.filter(public=True)

        return super().get_queryset().prefetch_related(category_prefetch)


class VenueViewSet(TournamentAPIMixin, PublicAPIMixin, ModelViewSet):
    serializer_class = serializers.VenueSerializer

    def get_queryset(self):
        return super().get_queryset().select_related('tournament').prefetch_related('venuecategory_set', 'venuecategory_set__tournament')


class VenueCategoryViewSet(TournamentAPIMixin, PublicAPIMixin, ModelViewSet):
    serializer_class = serializers.VenueCategorySerializer

    def get_queryset(self):
        return super().get_queryset().select_related('tournament').prefetch_related('venues', 'venues__tournament')


class BaseCheckinsView(AdministratorAPIMixin, TournamentAPIMixin, APIView):
    name = "Check-ins"

    lookup_field = 'pk'
    lookup_url_kwarg = None

    def get_object_queryset(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        return self.get_queryset().filter(**filter_kwargs)

    def get_object(self):
        obj = get_object_or_404(self.get_object_queryset())

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        if not hasattr(obj, 'checkin_identifier'):
            raise NotFound(detail='No identifier. Use POST to generate.')
        return obj

    def broadcast_checkin(self, obj, check):
        # Send result to websocket for treatment when opened; but perform the action here
        if check:
            checkin = Event.objects.create(identifier=obj.checkin_identifier,
                                           tournament=self.tournament)
            checkin_dict = checkin.serialize()
            checkin_dict['owner_name'] = obj.name
        else:
            checkins = get_unexpired_checkins(self.tournament, self.window_preference_pref)
            checkins.filter(identifier=obj.checkin_identifier).delete()
            checkin_dict = {'identifier': obj.checkin_identifier.barcode}

        group_name = CheckInEventConsumer.group_prefix + "_" + self.tournament.slug
        async_to_sync(get_channel_layer().group_send)(
            group_name, {
                'type': 'send_json',
                'data': {
                    'checkins': [checkin_dict],
                },
            },
        )

    def get_response_dict(self, request, obj, checked, **kwargs):
        return {
            'object': reverse(
                self.object_api_view,
                kwargs={'tournament_slug': self.tournament.slug, 'pk': obj.pk},
                request=request,
                format=kwargs.get('format'),
            ),
            'barcode': obj.checkin_identifier.barcode,
            'checked': checked,
        }

    def get_queryset(self):
        return self.model.objects.filter(**self.lookup_kwargs()).select_related(self.tournament_field)

    def get(self, request, *args, **kwargs):
        obj = self.get_object()

        event = get_unexpired_checkins(self.tournament, self.window_preference_pref).filter(identifier=obj.checkin_identifier)
        return Response(self.get_response_dict(request, obj, event.exists()))

    def delete(self, request, *args, **kwargs):
        """Checks out"""
        obj = self.get_object()
        self.broadcast_checkin(obj, False)
        return Response(self.get_response_dict(request, obj, False))

    def put(self, request, *args, **kwargs):
        """Checks in"""
        obj = self.get_object()
        self.broadcast_checkin(obj, True)
        return Response(self.get_response_dict(request, obj, True))

    def patch(self, request, *args, **kwargs):
        """Toggles the check-in status"""
        obj = self.get_object()
        check = get_unexpired_checkins(self.tournament, self.window_preference_pref).filter(identifier=obj.checkin_identifier).exists()
        self.broadcast_checkin(obj, not check)
        return Response(self.get_response_dict(request, obj, not check))

    def post(self, request, *args, **kwargs):
        """Creates an identifier"""
        obj = self.get_object_queryset()  # Don't .get() as create_identifiers expects a queryset
        if not obj.exists():
            raise Http404
        create_identifiers(self.model.checkin_identifier.related.related_model, obj)
        return Response(self.get_response_dict(request, obj.get(), False))


class AdjudicatorCheckinsView(BaseCheckinsView):
    model = Adjudicator
    object_api_view = 'api-adjudicator-detail'
    window_preference_pref = 'checkin_window_people'


class SpeakerCheckinsView(BaseCheckinsView):
    model = Speaker
    object_api_view = 'api-speaker-detail'
    window_preference_pref = 'checkin_window_people'
    tournament_field = 'team__tournament'


class VenueCheckinsView(BaseCheckinsView):
    model = Venue
    object_api_view = 'api-venue-detail'
    window_preference_pref = 'checkin_window_venues'


class BaseStandingsView(TournamentAPIMixin, TournamentPublicAPIMixin, GenericAPIView):
    lookup_field = 'slug'
    lookup_url_kwarg = 'tournament_slug'

    def get_metrics(self):
        pref_model = self.model.__name__.lower()
        return self.tournament.pref(pref_model + '_standings_precedence'), self.tournament.pref(pref_model + '_standings_extra_metrics')

    def get_queryset(self):
        qs = self.model.objects.filter(**{self.tournament_field: self.tournament}).select_related(self.tournament_field)
        category = self.request.query_params.get('category', None)
        if category is not None:
            return qs.filter(categories__pk=category)
        return qs

    def get_max_round(self):
        return None

    def get(self, request, **kwargs):
        metrics, extra_metrics = self.get_metrics()
        generator = self.generator(metrics, ('rank',), extra_metrics)
        standings = generator.generate(self.get_queryset(), round=self.get_max_round())
        serializer = self.get_serializer(iter(standings), many=True)
        return Response(serializer.data)


class SubstantiveSpeakerStandingsView(BaseStandingsView):
    name = "Speaker Standings"
    serializer_class = serializers.SpeakerStandingsSerializer
    access_preference = 'speaker_tab_released'
    model = Speaker
    tournament_field = 'team__tournament'
    generator = SpeakerStandingsGenerator

    def get_max_round(self):
        return self.tournament.round_set.last()


class ReplySpeakerStandingsView(SubstantiveSpeakerStandingsView):
    def get_metrics(self):
        return ('replies_avg',), ('replies_stddev', 'replies_count')


class TeamStandingsView(BaseStandingsView):
    name = 'Team Standings'
    serializer_class = serializers.TeamStandingsSerializer
    access_preference = 'team_tab_released'
    model = Team
    generator = TeamStandingsGenerator


class PairingViewSet(RoundAPIMixin, ModelViewSet):

    class Permission(PublicPreferencePermission):
        def get_tournament_preference(self, view, op):
            t = view.tournament
            r = view.round

            draw_status = {
                'off': False,
                'current': t.current_round.id == r.id and self.get_round_status(view),
                'all-released': self.get_round_status(view),
            }[t.pref(view.access_preference)]

            result_status = t.pref('public_results') and r.completed and not r.is_silent
            return draw_status or result_status or t.pref('all_results_released')

        def get_round_status(self, view):
            return getattr(view.round, view.round_released_field) == view.round_released_value

    serializer_class = serializers.RoundPairingSerializer
    lookup_url_kwarg = 'debate_pk'

    access_preference = 'public_draw'

    round_released_field = 'draw_status'
    round_released_value = Round.STATUS_RELEASED

    permission_classes = [APIEnabledPermission, Permission]

    def get_queryset(self):
        return super().get_queryset().select_related('round', 'round__tournament', 'venue', 'venue__tournament').prefetch_related(
            'debateteam_set', 'debateteam_set__team', 'debateteam_set__team__tournament',
            'debateadjudicator_set', 'debateadjudicator_set__adjudicator', 'debateadjudicator_set__adjudicator__tournament',
        )


class BallotViewSet(RoundAPIMixin, TournamentPublicAPIMixin, ModelViewSet):
    serializer_class = serializers.BallotSerializer
    access_preference = 'ballots_released'

    tournament_field = 'debate__round__tournament'
    round_field = 'debate__round'

    @property
    def debate(self):
        if hasattr(self, '_debate'):
            return self._debate

        self._debate = get_object_or_404(Debate, pk=self.kwargs.get('debate_pk'))
        return self._debate

    def perform_create(self, serializer):
        serializer.save(**{'debate': self.debate})

    def lookup_kwargs(self):
        kwargs = super().lookup_kwargs()
        kwargs['debate'] = self.debate
        return kwargs

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['debate'] = self.debate
        return context

    def get_queryset(self):
        filters = Q()
        if self.request.query_params.get('confirmed') or not self.request.user.is_staff:
            filters &= Q(confirmed=True)
        return super().get_queryset().filter(filters)


class FeedbackQuestionViewSet(TournamentAPIMixin, PublicAPIMixin, ModelViewSet):
    serializer_class = serializers.FeedbackQuestionSerializer

    def get_queryset(self):
        filters = Q()
        if self.request.query_params.get('from_adj'):
            filters &= Q(from_adj=True)
        if self.request.query_params.get('from_team'):
            filters &= Q(from_team=True)
        return super().get_queryset().filter(filters)


class FeedbackViewSet(TournamentAPIMixin, AdministratorAPIMixin, ModelViewSet):
    serializer_class = serializers.FeedbackSerializer
    tournament_field = 'adjudicator__tournament'

    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        query_params = self.request.query_params
        filters = Q()
        if query_params.get('source_type') == 'adjudicator':
            filters &= Q(source_team__isnull=True)
            if query_params.get('source'):
                filters &= Q(source_adjudicator__adjudicator_id=query_params.get('source'))
        elif query_params.get('source_type') == 'team':
            filters &= Q(source_adjudicator__isnull=True)
            if query_params.get('source'):
                filters &= Q(source_team__team_id=query_params.get('source'))
        if query_params.get('round'):
            filters &= Q(source_adjudicator__debate__round__seq=query_params.get('round')) | Q(source_team__debate__round__seq=query_params.get('round'))
        if query_params.get('target'):
            filters &= Q(adjudicator_id=query_params.get('target'))

        answers_prefetch = [
            Prefetch(
                typ.__name__.lower() + "_set",
                queryset=typ.objects.all().select_related('question', 'question__tournament'),
            )
            for typ in AdjudicatorFeedbackQuestion.ANSWER_TYPE_CLASSES_REVERSE.keys()
        ]
        return super().get_queryset().filter(filters).select_related(
            'adjudicator', 'adjudicator__tournament',
            'source_adjudicator', 'source_team', 'source_team__team',
            'source_adjudicator__adjudicator__tournament', 'source_team__team__tournament',
            'source_adjudicator__debate', 'source_team__debate',
            'source_adjudicator__debate__round', 'source_team__debate__round',
            'source_adjudicator__debate__round__tournament', 'source_team__debate__round__tournament',
        ).prefetch_related(*answers_prefetch)
