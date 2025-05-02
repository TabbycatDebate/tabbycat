from copy import deepcopy
from itertools import groupby

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Prefetch, Q
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from dynamic_preferences.api.serializers import PreferenceSerializer
from dynamic_preferences.api.viewsets import PerInstancePreferenceViewSet
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.fields import DateTimeField
from rest_framework.generics import CreateAPIView, GenericAPIView, get_object_or_404, RetrieveUpdateAPIView
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import BasePermission, IsAdminUser
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from actionlog.models import ActionLogEntry
from adjallocation.models import PreformedPanel
from adjallocation.preformed.anticipated import calculate_anticipated_draw
from adjfeedback.models import AdjudicatorFeedback
from availability.models import RoundAvailability
from breakqual.models import BreakCategory
from breakqual.views import GenerateBreakMixin
from checkins.consumers import CheckInEventConsumer
from checkins.models import Event
from checkins.utils import create_identifiers, get_unexpired_checkins
from draw.models import Debate, DebateTeam
from options.models import TournamentPreferenceModel
from participants.models import Adjudicator, Institution, Person, Speaker, SpeakerCategory, Team
from results.models import SpeakerScore, TeamScore
from standings.speakers import SpeakerStandingsGenerator
from standings.teams import TeamStandingsGenerator
from tournaments.mixins import TournamentFromUrlMixin
from tournaments.models import Round, Tournament
from users.permissions import get_permissions, Permission
from venues.models import Venue, VenueCategory

from . import serializers
from .fields import ParticipantAvailabilityForeignKeyField
from .mixins import AdministratorAPIMixin, APILogActionMixin, PublicAPIMixin, RoundAPIMixin, TournamentAPIMixin, TournamentPublicAPIMixin
from .permissions import APIEnabledPermission, PerTournamentPermissionRequired, PublicPreferencePermission, URLKeyAuthentication


tournament_parameter = OpenApiParameter('tournament_slug', description="The tournament's slug", type=str, location="path")
round_parameters = [
    tournament_parameter,
    OpenApiParameter('round_seq', description="The round's sequence number", type=int, location="path"),
]
debate_parameters = [
    *round_parameters,
    OpenApiParameter('debate_pk', description="The debate's primary key", type=int, location="path"),
]
id_parameter = OpenApiParameter('id', description="The object's primary key", type=int, location="path")


@extend_schema(tags=['root'], summary="API root")
class APIRootView(PublicAPIMixin, GenericAPIView):
    name = "API Root"
    serializer_class = serializers.RootSerializer

    def get(self, request, format=None):
        """API Entrypoint; info about versions"""
        return Response({
            "_links": {
                "v1": reverse('api-v1-root', request=request, format=format),
            },
            "timezone": settings.TIME_ZONE,
            "version": settings.TABBYCAT_VERSION,
            "version_name": settings.TABBYCAT_CODENAME,
        })


@extend_schema(tags=['root'], summary="API v1 root")
class APIV1RootView(PublicAPIMixin, GenericAPIView):
    name = "API Version 1 Root"
    serializer_class = serializers.V1RootSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'tournament_slug'

    def get(self, request, format=None):
        """Entrypoint for version 1 of the API"""
        tournaments_create_url = reverse('api-tournament-list', request=request, format=format)
        institution_create_url = reverse('api-global-institution-list', request=request, format=format)
        users_create_url = reverse('api-user-list', request=request, format=format)
        return Response({
            "_links": {
                "tournaments": tournaments_create_url,
                "institutions": institution_create_url,
                "users": users_create_url,
            },
        })


@extend_schema(tags=['tournaments'])
@extend_schema_view(
    list=extend_schema(summary="List tournaments"),
    create=extend_schema(summary="Create tournament"),
    retrieve=extend_schema(summary="Get tournament", parameters=[tournament_parameter]),
    update=extend_schema(summary="Change tournament", parameters=[tournament_parameter]),
    partial_update=extend_schema(summary="Patch tournament", parameters=[tournament_parameter]),
    destroy=extend_schema(summary="Delete tournament", parameters=[tournament_parameter]),
)
class TournamentViewSet(PublicAPIMixin, APILogActionMixin, ModelViewSet):
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
    action_log_type_created = ActionLogEntry.ActionType.TOURNAMENT_CREATE
    action_log_type_updated = ActionLogEntry.ActionType.TOURNAMENT_EDIT


@extend_schema(tags=['tournaments'], parameters=[tournament_parameter])
@extend_schema_view(
    list=extend_schema(summary="List tournament preferences"),
    retrieve=extend_schema(summary="Get tournament preference"),
    update=extend_schema(summary="Modify tournament preference"),
    partial_update=extend_schema(summary="Patch tournament preference"),
    bulk=extend_schema(summary="Update multiple tournament preferences"),
)
class TournamentPreferenceViewSet(TournamentFromUrlMixin, AdministratorAPIMixin, APILogActionMixin, PerInstancePreferenceViewSet):
    """
    """
    # Blank comment to avoid comment from TournamentFromUrlMixin appearing.
    queryset = TournamentPreferenceModel.objects.all()
    serializer_class = PreferenceSerializer

    list_permission = Permission.VIEW_TOURNAMENTPREFERENCEMODEL
    update_permission = Permission.EDIT_TOURNAMENTPREFERENCEMODEL

    action_log_content_object_attr = 'obj'
    action_log_type_updated = ActionLogEntry.ActionType.OPTIONS_EDIT

    def get_related_instance(self):
        return self.tournament


@extend_schema(tags=['rounds'])
@extend_schema_view(
    list=extend_schema(summary="List rounds of a tournament", parameters=[tournament_parameter]),
    create=extend_schema(summary="Create round", parameters=[tournament_parameter]),
    retrieve=extend_schema(summary="Get round", parameters=round_parameters),
    update=extend_schema(summary="Update round", parameters=round_parameters),
    partial_update=extend_schema(summary="Patch round", parameters=round_parameters),
    destroy=extend_schema(summary="Delete round", parameters=round_parameters),
)
class RoundViewSet(TournamentAPIMixin, PublicAPIMixin, ModelViewSet):
    serializer_class = serializers.RoundSerializer
    lookup_field = 'seq'
    lookup_url_kwarg = 'round_seq'
    action_log_type_created = ActionLogEntry.ActionType.ROUND_CREATE
    action_log_type_updated = ActionLogEntry.ActionType.ROUND_EDIT

    create_permission = Permission.CREATE_ROUND
    update_permission = Permission.EDIT_ROUND
    destroy_permission = False

    def get_queryset(self):
        return super().get_queryset().select_related(
            'break_category', 'break_category__tournament',
        ).prefetch_related('roundmotion_set', 'roundmotion_set__motion', 'roundmotion_set__motion__tournament')


@extend_schema(tags=['motions'], parameters=[tournament_parameter])
@extend_schema_view(
    list=extend_schema(summary="List tournament motions"),
    create=extend_schema(summary="Create motion"),
    retrieve=extend_schema(summary="Get motion", parameters=[id_parameter]),
    update=extend_schema(summary="Update motion", parameters=[id_parameter]),
    partial_update=extend_schema(summary="Patch motion", parameters=[id_parameter]),
    destroy=extend_schema(summary="Delete motion", parameters=[id_parameter]),
)
class MotionViewSet(TournamentAPIMixin, TournamentPublicAPIMixin, ModelViewSet):
    serializer_class = serializers.MotionSerializer
    access_preference = ('public_motions', 'motion_tab_released')
    access_operator = any
    action_log_type_created = ActionLogEntry.ActionType.MOTION_EDIT
    action_log_type_updated = ActionLogEntry.ActionType.MOTION_EDIT

    list_permission = Permission.VIEW_MOTION
    create_permission = Permission.EDIT_MOTION
    update_permission = Permission.EDIT_MOTION
    destroy_permission = False

    def get_queryset(self):
        filters = Q()
        if self.tournament.pref('public_motions') and not (self.tournament.pref('motion_tab_released') or self.request.user.is_staff):
            filters &= Q(rounds__motions_released=True)
        return super().get_queryset().filter(filters).prefetch_related('roundmotion_set', 'roundmotion_set__round')


@extend_schema(tags=['break-categories'], parameters=[tournament_parameter])
@extend_schema_view(
    list=extend_schema(summary="List tournament break categories"),
    create=extend_schema(summary="Create break category"),
    retrieve=extend_schema(summary="Get break category", parameters=[id_parameter]),
    update=extend_schema(summary="Update break category", parameters=[id_parameter]),
    partial_update=extend_schema(summary="Patch break category", parameters=[id_parameter]),
    destroy=extend_schema(summary="Delete break category", parameters=[id_parameter]),
)
class BreakCategoryViewSet(TournamentAPIMixin, PublicAPIMixin, ModelViewSet):
    serializer_class = serializers.BreakCategorySerializer
    action_log_type_created = ActionLogEntry.ActionType.BREAK_CATEGORIES_EDIT
    action_log_type_updated = ActionLogEntry.ActionType.BREAK_CATEGORIES_EDIT

    list_permission = Permission.VIEW_BREAK_CATEGORIES
    create_permission = Permission.EDIT_BREAK_CATEGORIES
    update_permission = Permission.EDIT_BREAK_CATEGORIES
    destroy_permission = Permission.EDIT_BREAK_CATEGORIES


@extend_schema(tags=['speaker-categories'], parameters=[tournament_parameter])
@extend_schema_view(
    list=extend_schema(summary="List tournament speaker categories"),
    create=extend_schema(summary="Create speaker category"),
    retrieve=extend_schema(summary="Get speaker category", parameters=[id_parameter]),
    update=extend_schema(summary="Update speaker category", parameters=[id_parameter]),
    partial_update=extend_schema(summary="Patch speaker category", parameters=[id_parameter]),
    destroy=extend_schema(summary="Delete speaker category", parameters=[id_parameter]),
)
class SpeakerCategoryViewSet(TournamentAPIMixin, PublicAPIMixin, ModelViewSet):
    serializer_class = serializers.SpeakerCategorySerializer
    action_log_type_created = ActionLogEntry.ActionType.SPEAKER_CATEGORIES_EDIT
    action_log_type_updated = ActionLogEntry.ActionType.SPEAKER_CATEGORIES_EDIT

    list_permission = Permission.VIEW_SPEAKER_CATEGORIES
    create_permission = Permission.EDIT_SPEAKER_CATEGORIES
    update_permission = Permission.EDIT_SPEAKER_CATEGORIES
    destroy_permission = Permission.EDIT_SPEAKER_CATEGORIES

    def get_queryset(self):
        if not self.request.user or not self.request.user.is_staff:
            return super().get_queryset().filter(public=True)
        return super().get_queryset()


@extend_schema(tags=['break-categories'], parameters=[tournament_parameter, id_parameter])
@extend_schema_view(
    get=extend_schema(summary="Get break-eligible teams for category"),
    put=extend_schema(summary="Update break eligibility of teams"),
    patch=extend_schema(summary="Add teams as break-eligible"),
)
class BreakEligibilityView(TournamentAPIMixin, TournamentPublicAPIMixin, RetrieveUpdateAPIView):
    serializer_class = serializers.BreakEligibilitySerializer
    access_preference = 'public_break_categories'
    action_log_type_updated = ActionLogEntry.ActionType.BREAK_ELIGIBILITY_EDIT

    list_permission = Permission.VIEW_BREAK_ELIGIBILITY
    create_permission = Permission.EDIT_BREAK_ELIGIBILITY
    update_permission = Permission.EDIT_BREAK_ELIGIBILITY

    def get_queryset(self):
        return super().get_queryset().prefetch_related('team_set')


@extend_schema(tags=['speaker-categories'], parameters=[tournament_parameter, id_parameter])
@extend_schema_view(
    get=extend_schema(summary="Get speaker category membership"),
    put=extend_schema(summary="Update membership of speaker category"),
    patch=extend_schema(summary="Add speakers to category"),
)
class SpeakerEligibilityView(TournamentAPIMixin, TournamentPublicAPIMixin, RetrieveUpdateAPIView):
    serializer_class = serializers.SpeakerEligibilitySerializer
    access_preference = 'public_participants'
    action_log_type_updated = ActionLogEntry.ActionType.SPEAKER_ELIGIBILITY_EDIT

    list_permission = Permission.VIEW_SPEAKER_ELIGIBILITY
    create_permission = Permission.EDIT_SPEAKER_ELIGIBILITY
    update_permission = Permission.EDIT_SPEAKER_ELIGIBILITY

    def get_queryset(self):
        qs = super().get_queryset().prefetch_related('speaker_set')
        if not self.request.user or not self.request.user.is_staff:
            return qs.filter(public=True)
        return qs


@extend_schema(tags=['break-categories'], parameters=[tournament_parameter, id_parameter])
@extend_schema_view(list=extend_schema(summary="Get breaking teams"))
class BreakingTeamsView(TournamentAPIMixin, TournamentPublicAPIMixin, GenerateBreakMixin, GenericViewSet, ListModelMixin):
    serializer_class = serializers.BreakingTeamSerializer
    tournament_field = 'break_category__tournament'
    pagination_class = None
    access_preference = 'public_breaking_teams'
    action_log_content_object_attr = 'break_category'

    list_permission = Permission.VIEW_BREAK
    create_permission = Permission.GENERATE_BREAK
    update_permission = Permission.GENERATE_BREAK
    destroy_permission = Permission.GENERATE_BREAK

    @property
    def break_category(self):
        if not hasattr(self, "_break_category"):
            self._break_category = get_object_or_404(BreakCategory, tournament=self.tournament, pk=self.kwargs.get('pk'))
        return self._break_category

    def get_queryset(self):
        return super().get_queryset().filter(
            break_category=self.break_category).select_related('team', 'team__tournament').order_by('rank')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['break_category'] = self.break_category
        return context

    @extend_schema(summary="Generate break")
    def create(self, request, *args, **kwargs):
        self.generate_break((self.break_category,))
        self.log_action(type=ActionLogEntry.ActionType.BREAK_GENERATE_ONE)
        return self.list(request, *args, **kwargs)

    @extend_schema(summary="Delete break")
    def destroy(self, request, *args, **kwargs):
        """
        Destroy is normally for a specific instance, now QuerySet.
        """
        self.filter_queryset(self.get_queryset()).delete()
        self.log_action(type=ActionLogEntry.ActionType.BREAK_DELETE)
        return Response(status=204)  # No content

    @extend_schema(summary="Update remark and regenerate break")
    def update(self, request, *args, **kwargs):
        serializer = serializers.PartialBreakingTeamSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        self.obj = serializer.save()
        self.log_action(type=ActionLogEntry.ActionType.BREAK_UPDATE_ONE, agent=ActionLogEntry.Agent.API)

        return self.create(request, *args, **kwargs)


@extend_schema(tags=['institutions'], parameters=[tournament_parameter])
@extend_schema_view(
    list=extend_schema(summary="List institutions in tournament", parameters=[
        OpenApiParameter('region', description='Only include institutions from the region', required=False, type=str),
    ]),
)
class InstitutionViewSet(TournamentAPIMixin, TournamentPublicAPIMixin, ModelViewSet):
    serializer_class = serializers.PerTournamentInstitutionSerializer
    access_preference = 'public_institutions_list'
    action_log_type_created = ActionLogEntry.ActionType.INSTITUTION_CREATE
    action_log_type_updated = ActionLogEntry.ActionType.INSTITUTION_EDIT

    list_permission = Permission.VIEW_INSTITUTIONS
    create_permission = Permission.ADD_INSTITUTIONS
    update_permission = Permission.ADD_INSTITUTIONS
    destroy_permission = Permission.ADD_INSTITUTIONS

    def perform_create(self, serializer):
        self.obj = serializer.save()
        self.log_action(type=self.action_log_type_created, agent=ActionLogEntry.Agent.API)

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
            'venue_constraints__category__tournament',
        )


@extend_schema(tags=['teams'], parameters=[tournament_parameter])
@extend_schema_view(
    list=extend_schema(summary="List teams in tournament"),
    create=extend_schema(summary="Create team"),
    retrieve=extend_schema(summary="Get team", parameters=[id_parameter]),
    update=extend_schema(summary="Update team", parameters=[id_parameter]),
    partial_update=extend_schema(summary="Patch team", parameters=[id_parameter]),
    destroy=extend_schema(summary="Delete team", parameters=[id_parameter]),
)
class TeamViewSet(TournamentAPIMixin, TournamentPublicAPIMixin, ModelViewSet):
    serializer_class = serializers.TeamSerializer
    access_preference = 'public_participants'
    action_log_type_created = ActionLogEntry.ActionType.TEAM_CREATE
    action_log_type_updated = ActionLogEntry.ActionType.TEAM_EDIT

    list_permission = Permission.VIEW_TEAMS
    create_permission = Permission.ADD_TEAMS
    update_permission = Permission.ADD_TEAMS
    destroy_permission = Permission.ADD_TEAMS

    def get_queryset(self):
        category_prefetch = Prefetch('categories', queryset=SpeakerCategory.objects.all().select_related('tournament'))
        if not self.request.user or not self.request.user.is_staff:
            category_prefetch.queryset = category_prefetch.queryset.filter(public=True)

        return super().get_queryset().select_related('tournament').prefetch_related(
            Prefetch(
                'speaker_set',
                queryset=Speaker.objects.all().prefetch_related(category_prefetch).select_related('team__tournament', 'checkin_identifier'),
            ),
            'institution_conflicts', 'venue_constraints__category__tournament',
            'break_categories', 'break_categories__tournament',
        )


@extend_schema(tags=['adjudicators'], parameters=[tournament_parameter])
@extend_schema_view(
    list=extend_schema(summary="Get adjudicators in tournament", parameters=[
        OpenApiParameter('break', description='Only include breaking adjudicators', required=False, type=bool, default=False),
    ]),
    create=extend_schema(summary="Create adjudicator"),
    retrieve=extend_schema(summary="Get adjudicator", parameters=[id_parameter]),
    update=extend_schema(summary="Update adjudicator", parameters=[id_parameter]),
    partial_update=extend_schema(summary="Patch adjudicator", parameters=[id_parameter]),
    destroy=extend_schema(summary="Delete adjudicator", parameters=[id_parameter]),
)
class AdjudicatorViewSet(TournamentAPIMixin, TournamentPublicAPIMixin, ModelViewSet):
    serializer_class = serializers.AdjudicatorSerializer
    access_preference = 'public_participants'
    action_log_type_created = ActionLogEntry.ActionType.ADJUDICATOR_CREATE
    action_log_type_updated = ActionLogEntry.ActionType.ADJUDICATOR_EDIT

    list_permission = Permission.VIEW_ADJUDICATORS
    create_permission = Permission.ADD_ADJUDICATORS
    update_permission = Permission.ADD_ADJUDICATORS
    destroy_permission = Permission.ADD_ADJUDICATORS

    def get_break_permission(self):
        return self.request.user.is_staff or self.tournament.pref('public_breaking_adjs')

    def get_queryset(self):
        filters = Q()
        if self.request.query_params.get('break') and self.get_break_permission():
            filters &= Q(breaking=True)

        return super().get_queryset().select_related('checkin_identifier').prefetch_related(
            'team_conflicts', 'team_conflicts__tournament',
            'adjudicator_conflicts', 'adjudicator_conflicts__tournament',
            'institution_conflicts', 'venue_constraints__category__tournament',
        ).filter(filters)


@extend_schema(tags=['institutions'])
@extend_schema_view(
    list=extend_schema(summary="List all institutions", parameters=[
        OpenApiParameter('region', description='Only include institutions from the region', required=False, type=str),
    ]),
    create=extend_schema(summary="Create institution"),
    retrieve=extend_schema(summary="Get institution", parameters=[id_parameter]),
    update=extend_schema(summary="Update institution", parameters=[id_parameter]),
    partial_update=extend_schema(summary="Patch institution", parameters=[id_parameter]),
    destroy=extend_schema(summary="Delete institution", parameters=[id_parameter]),
)
class GlobalInstitutionViewSet(AdministratorAPIMixin, ModelViewSet):
    serializer_class = serializers.InstitutionSerializer
    action_log_type_created = ActionLogEntry.ActionType.INSTITUTION_CREATE
    action_log_type_updated = ActionLogEntry.ActionType.INSTITUTION_EDIT

    list_permission = Permission.VIEW_INSTITUTIONS
    create_permission = Permission.ADD_INSTITUTIONS
    update_permission = Permission.ADD_INSTITUTIONS
    destroy_permission = Permission.ADD_INSTITUTIONS

    def get_queryset(self):
        filters = Q()
        if self.request.query_params.get('region'):
            filters &= Q(region__name=self.request.query_params['region'])
        return Institution.objects.filter(filters).select_related('region').prefetch_related('venue_constraints__category__tournament')


@extend_schema(tags=['teams'], parameters=[tournament_parameter])
@extend_schema_view(
    list=extend_schema(summary="List speakers in tournament"),
    create=extend_schema(summary="Add speaker"),
    retrieve=extend_schema(summary="Get speaker", parameters=[id_parameter]),
    update=extend_schema(summary="Update speaker", parameters=[id_parameter]),
    partial_update=extend_schema(summary="Patch speaker", parameters=[id_parameter]),
    destroy=extend_schema(summary="Delete speaker", parameters=[id_parameter]),
)
class SpeakerViewSet(TournamentAPIMixin, TournamentPublicAPIMixin, ModelViewSet):
    serializer_class = serializers.SpeakerSerializer
    tournament_field = "team__tournament"
    access_preference = 'public_participants'
    action_log_type_created = ActionLogEntry.ActionType.SPEAKER_CREATE
    action_log_type_updated = ActionLogEntry.ActionType.SPEAKER_EDIT

    list_permission = Permission.VIEW_TEAMS
    create_permission = Permission.ADD_TEAMS
    update_permission = Permission.ADD_TEAMS
    destroy_permission = Permission.ADD_TEAMS

    def perform_create(self, serializer):
        self.obj = serializer.save()
        self.log_action(type=self.action_log_type_created, agent=ActionLogEntry.Agent.API)

    def get_queryset(self):
        category_prefetch = Prefetch('categories', queryset=SpeakerCategory.objects.all().select_related('tournament'))
        if not self.request.user or not self.request.user.is_staff:
            category_prefetch.queryset = category_prefetch.queryset.filter(public=True)

        return super().get_queryset().select_related('checkin_identifier').prefetch_related(category_prefetch)


@extend_schema(tags=['venues'], parameters=[tournament_parameter])
@extend_schema_view(
    list=extend_schema(summary="List rooms in tournament"),
    create=extend_schema(summary="Create room"),
    retrieve=extend_schema(summary="Get room", parameters=[id_parameter]),
    update=extend_schema(summary="Update room", parameters=[id_parameter]),
    partial_update=extend_schema(summary="Patch room", parameters=[id_parameter]),
    destroy=extend_schema(summary="Delete room", parameters=[id_parameter]),
)
class VenueViewSet(TournamentAPIMixin, PublicAPIMixin, ModelViewSet):
    serializer_class = serializers.VenueSerializer
    action_log_type_created = ActionLogEntry.ActionType.VENUE_CREATE
    action_log_type_updated = ActionLogEntry.ActionType.VENUE_EDIT

    list_permission = Permission.VIEW_ROOMS
    create_permission = Permission.ADD_ROOMS
    update_permission = Permission.ADD_ROOMS
    destroy_permission = Permission.ADD_ROOMS

    def get_queryset(self):
        # Tournament must exist for URLs
        return super().get_queryset().select_related('tournament').prefetch_related(
            Prefetch('venuecategory_set', queryset=VenueCategory.objects.select_related('tournament').filter(tournament__isnull=False)))


@extend_schema(tags=['venues'], parameters=[tournament_parameter])
@extend_schema_view(
    list=extend_schema(summary="List tournament venue categories"),
    create=extend_schema(summary="Create venue category"),
    retrieve=extend_schema(summary="Get venue category", parameters=[id_parameter]),
    update=extend_schema(summary="Update venue category", parameters=[id_parameter]),
    partial_update=extend_schema(summary="Patch venue category", parameters=[id_parameter]),
    destroy=extend_schema(summary="Delete venue category", parameters=[id_parameter]),
)
class VenueCategoryViewSet(TournamentAPIMixin, PublicAPIMixin, ModelViewSet):
    serializer_class = serializers.VenueCategorySerializer
    action_log_type_created = ActionLogEntry.ActionType.VENUE_CATEGORY_CREATE
    action_log_type_updated = ActionLogEntry.ActionType.VENUE_CATEGORIES_EDIT

    list_permission = Permission.VIEW_ROOMCATEGORIES
    create_permission = Permission.EDIT_ROOMCATEGORIES
    update_permission = Permission.EDIT_ROOMCATEGORIES
    destroy_permission = Permission.EDIT_ROOMCATEGORIES

    def get_queryset(self):
        # Tournament must exist for URLs
        return super().get_queryset().select_related('tournament').prefetch_related(
            Prefetch('venues', queryset=Venue.objects.select_related('tournament').filter(tournament__isnull=False)))


@extend_schema(tags=['checkins'], parameters=[tournament_parameter, id_parameter])
class BaseCheckinsView(AdministratorAPIMixin, TournamentAPIMixin, APIView):
    name = "Check-ins"

    lookup_field = 'pk'
    lookup_url_kwarg = None

    list_permission = Permission.VIEW_CHECKIN
    create_permission = Permission.EDIT_PARTICIPANT_CHECKIN
    update_permission = Permission.EDIT_PARTICIPANT_CHECKIN
    destroy_permission = Permission.EDIT_PARTICIPANT_CHECKIN

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
        checkin = None
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
        async_to_sync(get_channel_layer().group_send)(group_name, {
            'type': 'send_json',
            'checkins': [checkin_dict],
            'created': check,
        })
        return checkin

    def get_response_dict(self, request, obj, checked, event, **kwargs):
        return {
            'object': reverse(
                self.object_api_view,
                kwargs={'tournament_slug': self.tournament.slug, 'pk': obj.pk},
                request=request,
                format=kwargs.get('format'),
            ),
            'barcode': obj.checkin_identifier.barcode,
            'checked': checked,
            'timestamp': DateTimeField().to_representation(event.time) if event is not None else None,
        }

    def get_queryset(self):
        return self.model.objects.filter(**self.lookup_kwargs()).select_related(self.tournament_field)

    @extend_schema(request=None, responses=serializers.CheckinSerializer)
    def get(self, request, *args, **kwargs):
        """Get checkin status"""
        obj = self.get_object()

        event = get_unexpired_checkins(self.tournament, self.window_preference_pref).filter(identifier=obj.checkin_identifier)
        return Response(self.get_response_dict(request, obj, event.exists(), event.first()))

    @extend_schema(request=None, responses={200: serializers.CheckinSerializer})
    def delete(self, request, *args, **kwargs):
        """Checks out"""
        obj = self.get_object()
        self.broadcast_checkin(obj, False)
        return Response(self.get_response_dict(request, obj, False, None))

    @extend_schema(request=None, responses=serializers.CheckinSerializer)
    def put(self, request, *args, **kwargs):
        """Checks in"""
        obj = self.get_object()
        e = self.broadcast_checkin(obj, True)
        return Response(self.get_response_dict(request, obj, True, e))

    @extend_schema(request=None, responses=serializers.CheckinSerializer)
    def patch(self, request, *args, **kwargs):
        """Toggles the check-in status"""
        obj = self.get_object()
        events = get_unexpired_checkins(self.tournament, self.window_preference_pref).filter(identifier=obj.checkin_identifier)
        check = events.exists()
        e = self.broadcast_checkin(obj, not check)
        return Response(self.get_response_dict(request, obj, not check, e))

    @extend_schema(request=None, responses=serializers.CheckinSerializer)
    def post(self, request, *args, **kwargs):
        """Creates an identifier"""
        obj = self.get_object_queryset()  # Don't .get() as create_identifiers expects a queryset
        if not obj.exists():
            raise NotFound("Object could not be found")
        status = 200 if hasattr(obj, 'checkin_identifier') else 201
        create_identifiers(self.model.checkin_identifier.related.related_model, obj)
        return Response(self.get_response_dict(request, obj.get(), False, None), status=status)


class PersonCheckinMixin:
    class CustomPermission(BasePermission):
        def has_permission(self, request, view):
            return request.user is None or view.tournament.pref('participant_ballots') == 'private-urls' and view.participant_requester and request.method != 'POST'

    authentication_classes = [TokenAuthentication, SessionAuthentication, URLKeyAuthentication]
    permission_classes = [APIEnabledPermission, PerTournamentPermissionRequired, CustomPermission]

    @property
    def participant_requester(self):
        if isinstance(person := self.request.auth, Person):
            return person

    def get_queryset(self):
        return super().get_queryset().filter(id=self.participant_requester.id)


@extend_schema(tags=['adjudicators'])
@extend_schema_view(
    get=extend_schema(summary="Get adjudicator checkin status"),
    delete=extend_schema(summary="Check out adjudicator"),
    put=extend_schema(summary="Check in adjudicator"),
    patch=extend_schema(summary="Toggle adjudicator checkin status"),
    post=extend_schema(summary="Create adjudicator checkin identifier"),
)
class AdjudicatorCheckinsView(PersonCheckinMixin, BaseCheckinsView):
    model = Adjudicator
    object_api_view = 'api-adjudicator-detail'
    window_preference_pref = 'checkin_window_people'


@extend_schema(tags=['teams'])
@extend_schema_view(
    get=extend_schema(summary="Get speaker checkin status"),
    delete=extend_schema(summary="Check out speaker"),
    put=extend_schema(summary="Check in speaker"),
    patch=extend_schema(summary="Toggle speaker checkin status"),
    post=extend_schema(summary="Create speaker checkin identifier"),
)
class SpeakerCheckinsView(PersonCheckinMixin, BaseCheckinsView):
    model = Speaker
    object_api_view = 'api-speaker-detail'
    window_preference_pref = 'checkin_window_people'
    tournament_field = 'team__tournament'


@extend_schema(tags=['venues'])
@extend_schema_view(
    get=extend_schema(summary="Get room checkin status"),
    delete=extend_schema(summary="Check out room"),
    put=extend_schema(summary="Check in room"),
    patch=extend_schema(summary="Toggle room checkin status"),
    post=extend_schema(summary="Create room checkin identifier"),
)
class VenueCheckinsView(BaseCheckinsView):
    model = Venue
    object_api_view = 'api-venue-detail'
    window_preference_pref = 'checkin_window_venues'

    create_permission = Permission.EDIT_ROOM_CHECKIN
    update_permission = Permission.EDIT_ROOM_CHECKIN
    destroy_permission = Permission.EDIT_ROOM_CHECKIN


def get_metrics_params(generator):
    metrics = {
        'type': 'array',
        'items': {
            'type': 'string',
            'enum': list(generator.metric_annotator_classes.keys()),
        },
    }
    desc_default = '; default is tournament settings'
    return [
        OpenApiParameter('metrics',
            description='Rank participants with these metrics' + desc_default,
            required=False, type=metrics, explode=False),
        OpenApiParameter('extra_metrics',
            description='Include these unranked metrics for participants' + desc_default,
            required=False, type=metrics, explode=False),
    ]


class BaseStandingsView(TournamentAPIMixin, TournamentPublicAPIMixin, GenericAPIView):
    lookup_field = 'slug'
    lookup_url_kwarg = 'tournament_slug'

    def get_metrics(self):
        if self.request.query_params.get('metrics'):
            return self.request.query_params.get('metrics').split(","), self.request.query_params.get('extra_metrics').split(",")

        pref_model = self.model.__name__.lower()
        return self.tournament.pref(pref_model + '_standings_precedence'), self.tournament.pref(pref_model + '_standings_extra_metrics')

    def get_queryset(self):
        qs = self.model.objects.filter(**{self.tournament_field: self.tournament}).select_related(self.tournament_field)
        return qs

    def get_max_round(self):
        if self.request.query_params.get('round'):
            return Round.objects.get(tournament=self.tournament, seq=int(self.request.query_params.get('round')))
        return Round.objects.filter(tournament=self.tournament).order_by('seq').last()

    @extend_schema(tags=['standings'], parameters=[
        tournament_parameter,
        OpenApiParameter('category', description='Only include participants in a category (ID)', required=False, type=int),
        OpenApiParameter('round', description='Sequence of last round to take into account', required=False, type=int),
    ])
    def get(self, request, **kwargs):
        """Get current standings"""
        metrics, extra_metrics = self.get_metrics()
        generator = self.generator(metrics, ('rank',), extra_metrics)
        standings = generator.generate(self.get_queryset(), round=self.get_max_round())
        serializer = self.get_serializer(iter(standings), many=True)
        return Response(serializer.data)


@extend_schema_view(
    get=extend_schema(
        summary="Get substantive speaker standings",
        parameters=get_metrics_params(SpeakerStandingsGenerator),
        responses=serializers.SpeakerStandingsSerializer(many=True),
    ),
)
class SubstantiveSpeakerStandingsView(BaseStandingsView):
    name = "Speaker Standings"
    serializer_class = serializers.SpeakerStandingsSerializer
    access_preference = 'speaker_tab_released'
    model = Speaker
    tournament_field = 'team__tournament'
    generator = SpeakerStandingsGenerator

    list_permission = Permission.VIEW_SPEAKERSSTANDINGS

    def get_queryset(self):
        category = self.request.query_params.get('category', None)
        if category is not None:
            return super().get_queryset().filter(categories__pk=category)
        return super().get_queryset()


@extend_schema_view(
    get=extend_schema(summary="Get reply speaker standings", responses=serializers.SpeakerStandingsSerializer(many=True)),
)
class ReplySpeakerStandingsView(SubstantiveSpeakerStandingsView):
    def get_metrics(self):
        return ('replies_avg',), ('replies_stddev', 'replies_count')


@extend_schema_view(
    get=extend_schema(
        summary="Get team standings",
        parameters=get_metrics_params(TeamStandingsGenerator),
        responses=serializers.TeamStandingsSerializer(many=True),
    ),
)
class TeamStandingsView(BaseStandingsView):
    name = 'Team Standings'
    serializer_class = serializers.TeamStandingsSerializer
    access_preference = 'team_tab_released'
    model = Team
    generator = TeamStandingsGenerator

    list_permission = Permission.VIEW_TEAMSTANDINGS

    def get_queryset(self):
        category = self.request.query_params.get('category', None)
        if category is not None:
            return super().get_queryset().filter(break_categories__pk=category)
        return super().get_queryset()


@extend_schema(tags=['standings'], parameters=[
    tournament_parameter,
    OpenApiParameter('replies', description='Whether to include reply speeches', required=False, type=bool, default=False),
    OpenApiParameter('substantive', description='Whether to include substantive speeches', required=False, type=bool, default=True),
    OpenApiParameter('ghost', description='Include ghost (iron-person) scores', required=False, type=bool, default=False),
])
@extend_schema_view(
    list=extend_schema(summary="Get speaker scores per round", responses=serializers.SpeakerRoundScoresSerializer(many=True)),
)
class SpeakerRoundStandingsRoundsView(TournamentAPIMixin, TournamentPublicAPIMixin, ModelViewSet):
    serializer_class = serializers.SpeakerRoundScoresSerializer
    tournament_field = "team__tournament"
    access_preference = 'speaker_tab_released'

    list_permission = Permission.VIEW_SPEAKERSSTANDINGS

    def get_queryset(self):
        qs = super().get_queryset().prefetch_related(Prefetch('team__debateteam_set', queryset=DebateTeam.objects.all().select_related('debate__round__tournament')))
        data = {s.id: s for s in qs.all()}

        speaker_scores = SpeakerScore.objects.select_related('speaker', 'ballot_submission',
            'debate_team__debate__round__tournament').filter(
            ballot_submission__confirmed=True, speaker_id__in=data.keys(),
        ).order_by('speaker_id', 'debate_team_id', 'position')

        if self.request.query_params.get('ghost', False) == 'true':
            speaker_scores = speaker_scores.filter(ghost=True)
        if self.request.query_params.get('replies', False) == 'true':
            speaker_scores = speaker_scores.filter(position=self.tournament.reply_position)
        elif self.request.query_params.get('substantive', 'true') == 'true':
            speaker_scores = speaker_scores.filter(position__lte=self.tournament.last_substantive_position)

        for spk in data.values():
            spk.debateteams = deepcopy(spk.team.debateteam_set.all())
            for dt in spk.debateteams:
                dt.scores = []

        for speaker, all_scores in groupby(speaker_scores, key=lambda ss: ss.speaker_id):
            speaker_rounds = {dt.id: dt for dt in data[speaker].debateteams}
            for dt, round_scores in groupby(all_scores, key=lambda ss: ss.debate_team_id):
                speaker_rounds[dt].scores.extend(list(round_scores))

        return data.values()


@extend_schema(tags=['standings'], parameters=[
    tournament_parameter,
])
@extend_schema_view(
    list=extend_schema(summary="Get team scores per round", responses=serializers.TeamRoundScoresSerializer(many=True)),
)
class TeamRoundStandingsRoundsView(TournamentAPIMixin, TournamentPublicAPIMixin, ModelViewSet):
    serializer_class = serializers.TeamRoundScoresSerializer
    access_preference = 'team_tab_released'

    list_permission = Permission.VIEW_TEAMSTANDINGS

    def get_queryset(self):
        ts_pf = Prefetch('teamscore_set', queryset=TeamScore.objects.filter(ballot_submission__confirmed=True), to_attr='round_scores')
        qs = super().get_queryset().prefetch_related(
            Prefetch('debateteam_set', queryset=DebateTeam.objects.all().prefetch_related(ts_pf).select_related('debate__round__tournament')))

        for t in qs:
            for dt in t.debateteam_set.all():
                if len(dt.round_scores):
                    # There should only ever be one confirmed score
                    dt.ballot = dt.round_scores[0]
                else:
                    dt.ballot = TeamScore()

        return qs


@extend_schema(tags=['debates'], parameters=round_parameters)
@extend_schema_view(
    list=extend_schema(summary="List pairings in round"),
    create=extend_schema(summary="Create pairing"),
    retrieve=extend_schema(summary="Get pairing", parameters=debate_parameters),
    update=extend_schema(summary="Update pairing", parameters=debate_parameters),
    partial_update=extend_schema(summary="Patch pairing", parameters=debate_parameters),
    destroy=extend_schema(summary="Delete pairing", parameters=debate_parameters),
)
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

            result_status = t.pref('public_results') and r.completed and not r.silent
            return draw_status or result_status or t.pref('all_results_released')

        def get_round_status(self, view):
            return getattr(view.round, view.round_released_field) == view.round_released_value

    serializer_class = serializers.RoundPairingSerializer
    lookup_url_kwarg = 'debate_pk'

    access_preference = 'public_draw'

    round_released_field = 'draw_status'
    round_released_value = Round.Status.RELEASED

    """list_permission = Permission.VIEW_DEBATE
    create_permission = Permission.GENERATE_DEBATE
    update_permission = Permission.GENERATE_DEBATE
    destroy_permission = Permission.GENERATE_DEBATE"""

    permission_classes = [APIEnabledPermission, Permission | PerTournamentPermissionRequired]

    action_log_type_created = ActionLogEntry.ActionType.DEBATE_CREATE
    action_log_type_updated = ActionLogEntry.ActionType.DEBATE_EDIT

    def get_queryset(self):
        return super().get_queryset().select_related('round', 'round__tournament', 'venue', 'venue__tournament').prefetch_related(
            'debateteam_set', 'debateteam_set__team', 'debateteam_set__team__tournament',
            'debateadjudicator_set', 'debateadjudicator_set__adjudicator', 'debateadjudicator_set__adjudicator__tournament',
        )

    @extend_schema(summary="Delete all pairings in the round")
    def delete_all(self, request, *args, **kwargs):
        self.get_queryset().delete()
        self.log_action(ActionLogEntry.ActionType.DRAW_REGENERATE)
        return Response(status=204)  # No content


@extend_schema(
    tags=['debates'],
    parameters=round_parameters,
    request=serializers.DrawGenerationSerializer,
    responses={201: serializers.RoundPairingSerializer(many=True)},
    summary="Generate draw for round",
)
class GeneratePairingView(RoundAPIMixin, AdministratorAPIMixin, CreateAPIView):
    create_permission = Permission.GENERATE_DEBATE
    serializer_class = serializers.DrawGenerationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        draw = self.perform_create(serializer)
        response_serializer = serializers.RoundPairingSerializer(draw, many=True)

        headers = self.get_success_headers(serializer.data)
        return Response(response_serializer.data, status=201, headers=headers)

    def perform_create(self, serializer):
        return serializer.save()


@extend_schema(tags=['results'], parameters=debate_parameters)
@extend_schema_view(
    list=extend_schema(summary="Get debate ballots", parameters=[
        OpenApiParameter('confirmed', description='Only include confirmed ballots', required=False, type=bool, default=False),
    ]),
    create=extend_schema(summary="Create ballot"),
    retrieve=extend_schema(summary="Get ballot", parameters=[id_parameter]),
    update=extend_schema(summary="Update ballot", parameters=[id_parameter], request=serializers.UpdateBallotSerializer),
    partial_update=extend_schema(summary="Patch ballot", parameters=[id_parameter], request=serializers.UpdateBallotSerializer),
)
class BallotViewSet(RoundAPIMixin, TournamentPublicAPIMixin, ModelViewSet):

    class CustomPermission(BasePermission):
        def has_permission(self, request, view):
            return request.user is None or (
                (view.action in ['list', 'retrieve', 'create'] and view.tournament.pref('participant_ballots') == 'private-urls' and view.participant_requester) or
                (view.action == 'create' and view.tournament.pref('participant_ballots') == 'public') or
                (view.action in ['list', 'retrieve'] and view.tournament.pref('private_ballots_released') is True)
            )

    serializer_class = serializers.BallotSerializer
    access_preference = 'ballots_released'

    tournament_field = 'debate__round__tournament'
    round_field = 'debate__round'

    authentication_classes = [TokenAuthentication, SessionAuthentication, URLKeyAuthentication]
    permission_classes = [APIEnabledPermission, PerTournamentPermissionRequired, PublicPreferencePermission | CustomPermission]

    list_permission = Permission.VIEW_BALLOTSUBMISSIONS
    create_permission = Permission.ADD_BALLOTSUBMISSIONS
    update_permission = Permission.EDIT_BALLOTSUBMISSIONS
    destroy_permission = Permission.MARK_BALLOTSUBMISSIONS

    action_log_type_created = ActionLogEntry.ActionType.BALLOT_CREATE
    action_log_type_updated = ActionLogEntry.ActionType.BALLOT_EDIT

    @property
    def participant_requester(self):
        if isinstance(person := self.request.auth, Person):
            try:
                return person.adjudicator
            except Adjudicator.DoesNotExist:
                if self.action == 'create':
                    raise PermissionDenied('URL key for submitting ballot must be for an adjudicator')
                else:
                    return person.speaker.team

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['participant_requester'] = self.participant_requester
        context['debate'] = self.debate
        return context

    @property
    def debate(self):
        if hasattr(self, '_debate'):
            return self._debate

        self._debate = get_object_or_404(Debate, pk=self.kwargs.get('debate_pk'))
        return self._debate

    def lookup_kwargs(self):
        return {'debate': self.debate}

    def get_queryset(self):
        filters = Q()

        if isinstance(self.participant_requester, Adjudicator):
            filters &= Q(debate__debateadjudicator__adjudicator_id=self.participant_requester.id)
        if isinstance(self.participant_requester, Team):
            filters &= Q(debate__debateteam_set__team_id=self.participant_requester.id)

        if self.request.query_params.get('confirmed') or not (getattr(self.request.user, 'is_staff', False) or self.participant_requester):
            filters &= Q(confirmed=True)
        return super().get_queryset().filter(filters).prefetch_related(
            'debateteammotionpreference_set__motion__tournament',
            'debateteammotionpreference_set__debate_team__team__tournament',
        ).select_related(
            'motion', 'motion__tournament',
            'participant_submitter__adjudicator__tournament')

    @extend_schema(summary="Delete ballot", parameters=[id_parameter], responses={200: serializers.BallotSerializer})
    def destroy(self, request, *args, **kwargs):
        """Only mark as discarded; don't allow object deletion."""
        instance = self.get_object()
        instance.discarded = True
        instance.save()
        self.log_action(ActionLogEntry.ActionType.BALLOT_DISCARD)
        return self.retrieve(request, *args, **kwargs)


@extend_schema(tags=['feedback'], parameters=[tournament_parameter])
@extend_schema_view(
    list=extend_schema(summary="List tournament feedback questions", parameters=[
        OpenApiParameter('from_adj', description='Only include questions given to adjudicators', required=False, type=bool, default=False),
        OpenApiParameter('from_team', description='Only include questions given to teams', required=False, type=bool, default=False),
    ]),
    create=extend_schema(summary="Create feedback question"),
    retrieve=extend_schema(summary="Get feedback question", parameters=[id_parameter]),
    update=extend_schema(summary="Update feedback question", parameters=[id_parameter]),
    partial_update=extend_schema(summary="Patch feedback question", parameters=[id_parameter]),
    destroy=extend_schema(summary="Delete feedback question", parameters=[id_parameter]),
)
class FeedbackQuestionViewSet(TournamentAPIMixin, PublicAPIMixin, ModelViewSet):
    serializer_class = serializers.FeedbackQuestionSerializer
    action_log_type_created = ActionLogEntry.ActionType.FEEDBACK_QUESTION_CREATE
    action_log_type_updated = ActionLogEntry.ActionType.FEEDBACK_QUESTION_EDIT

    list_permission = True
    create_permission = Permission.EDIT_FEEDBACKQUESTION
    update_permission = Permission.EDIT_FEEDBACKQUESTION
    destroy_permission = Permission.EDIT_FEEDBACKQUESTION

    def get_queryset(self):
        filters = Q()
        if self.request.query_params.get('from_adj'):
            filters &= Q(from_adj=True)
        if self.request.query_params.get('from_team'):
            filters &= Q(from_team=True)
        return super().get_queryset().filter(filters)


@extend_schema(tags=['feedback'], parameters=[tournament_parameter])
@extend_schema_view(
    list=extend_schema(summary="List all tournament feedback", parameters=[
        OpenApiParameter('source_type', description='The type of participant submitter of the feedback', required=False, type=str, enum=['adjudicator', 'team']),
        OpenApiParameter('source', description='The ID of the participant submitting feedback; must be used in conjunction with `source_type`', required=False, type=int),
        OpenApiParameter('round', description='The sequence of the rounds of the submitted feedback', required=False, type={"type": "array", "items": {"type": "integer"}}, explode=False),
        OpenApiParameter('target', description='The ID of the adjudicator receiving feedback', required=False, type=int),
    ]),
    create=extend_schema(summary="Create feedback"),
    retrieve=extend_schema(summary="Get feedback", parameters=[id_parameter]),
    update=extend_schema(summary="Update feedback", parameters=[id_parameter]),
    partial_update=extend_schema(summary="Patch feedback", parameters=[id_parameter]),
    destroy=extend_schema(summary="Delete feedback", parameters=[id_parameter]),
)
class FeedbackViewSet(TournamentAPIMixin, AdministratorAPIMixin, ModelViewSet):

    class CustomPermission(BasePermission):
        def has_permission(self, request, view):
            return request.user is None or (
                (view.action in ['list', 'retrieve', 'create'] and view.tournament.pref('participant_feedback') == 'private-urls' and view.participant_requester) or
                (view.action == 'create' and view.tournament.pref('participant_feedback') == 'public')
            )

    serializer_class = serializers.FeedbackSerializer
    tournament_field = 'adjudicator__tournament'
    action_log_type_created = ActionLogEntry.ActionType.FEEDBACK_SAVE
    action_log_type_updated = ActionLogEntry.ActionType.FEEDBACK_SAVE

    authentication_classes = [TokenAuthentication, SessionAuthentication, URLKeyAuthentication]
    permission_classes = [APIEnabledPermission, PerTournamentPermissionRequired, CustomPermission]

    list_permission = Permission.VIEW_FEEDBACK
    create_permission = Permission.ADD_FEEDBACK
    update_permission = Permission.EDIT_FEEDBACK_IGNORE
    destroy_permission = Permission.EDIT_FEEDBACK_CONFIRM

    @property
    def participant_requester(self):
        if isinstance(person := self.request.auth, Person):
            try:
                return person.adjudicator
            except Adjudicator.DoesNotExist:
                return person.speaker.team

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['participant_requester'] = self.participant_requester
        return context

    def perform_create(self, serializer):
        self.obj = serializer.save()
        self.log_action(type=self.action_log_type_created, agent=ActionLogEntry.Agent.API)

    def get_queryset(self):
        query_params = self.request.query_params
        filters = Q()

        # Disallow querying for feedback that they didn't submit
        if (person := self.participant_requester) is not None:
            if self.action == 'list' and (query_params.get('source_type') != type(person).__name__.lower() or query_params.get('source') != str(person.id)):
                raise PermissionDenied("URL key-authorized requests may only get the participants' objects")

        if query_params.get('source_type') == 'adjudicator':
            filters &= Q(source_team__isnull=True)
            if query_params.get('source'):
                filters &= Q(source_adjudicator__adjudicator_id=query_params.get('source'))
        elif query_params.get('source_type') == 'team':
            filters &= Q(source_adjudicator__isnull=True)
            if query_params.get('source'):
                filters &= Q(source_team__team_id=query_params.get('source'))
        if query_params.get('round'):
            filters &= (Q(source_adjudicator__debate__round__seq__in=query_params.get('round').split(",")) |
                Q(source_team__debate__round__seq=query_params.get('round')))
        if query_params.get('target'):
            filters &= Q(adjudicator_id=query_params.get('target'))

        answers_prefetch = [
            Prefetch(
                typ,
                queryset=getattr(AdjudicatorFeedback, typ).rel.model.objects.select_related('question__tournament'),
            )
            for typ in AdjudicatorFeedback.answer_rels
        ]
        return super().get_queryset().filter(filters).select_related(
            'adjudicator', 'adjudicator__tournament',
            'source_adjudicator', 'source_team', 'source_team__team',
            'source_adjudicator__adjudicator__tournament', 'source_team__team__tournament',
            'source_adjudicator__debate', 'source_team__debate',
            'source_adjudicator__debate__round', 'source_team__debate__round',
            'source_adjudicator__debate__round__tournament', 'source_team__debate__round__tournament',
            'participant_submitter__adjudicator__tournament', 'participant_submitter__speaker__team__tournament',
        ).prefetch_related(*answers_prefetch)


@extend_schema(tags=['availabilities'], parameters=round_parameters)
class AvailabilitiesViewSet(RoundAPIMixin, AdministratorAPIMixin, APIView):
    serializer_class = serializers.AvailabilitiesSerializer  # Isn't actually used
    action_log_type_updated = ActionLogEntry.ActionType.AVAIL_SAVE
    action_log_content_object_attr = None

    list_permission = Permission.VIEW_ROUNDAVAILABILITIES
    create_permission = Permission.EDIT_ROUNDAVAILABILITIES
    update_permission = Permission.EDIT_ROUNDAVAILABILITIES
    destroy_permission = Permission.EDIT_ROUNDAVAILABILITIES

    extra_params = [
        OpenApiParameter('adjudicators', description='Only include adjudicators', required=False, type=bool, default=False),
        OpenApiParameter('teams', description='Only include teams', required=False, type=bool, default=False),
        OpenApiParameter('venues', description='Only include rooms', required=False, type=bool, default=False),
    ]

    def get_field(self):
        field = ParticipantAvailabilityForeignKeyField(many=True, view_name='api-availability-list')  # Dummy view name
        field.root._context = {'request': self.request}
        return field

    def get_filters(self):
        filters = Q()
        if self.request.query_params.get('adjudicators', 'false') == 'false':
            filters |= Q(content_type__model='adjudicator')
        if self.request.query_params.get('teams', 'false') == 'false':
            filters |= Q(content_type__model='team')
        if self.request.query_params.get('venues', 'false') == 'false':
            filters |= Q(content_type__model='venue')
        return filters

    def get_queryset(self):
        return RoundAvailability.objects.filter(
            ~self.get_filters(), round=self.round).select_related('content_type', 'round__tournament')

    @extend_schema(summary="Get all availabilities of the round", parameters=extra_params)
    def get(self, request, *args, **kwargs):
        return Response(self.get_field().to_representation(self.get_queryset()))

    @extend_schema(summary="Toggle the availabilities of the included objects")
    def patch(self, request, *args, **kwargs):
        objs = sorted(self.get_field().to_internal_value(request.data), key=lambda o: type(o).__name__)
        for model, participants in groupby(objs, key=type):
            contenttype = ContentType.objects.get_for_model(model)

            ids = set(p.pk for p in participants)
            existing_qs = RoundAvailability.objects.filter(
                content_type=contenttype, round=self.round,
                object_id__in=ids,
            )
            existing = set(p.object_id for p in existing_qs)
            existing_qs.delete()

            RoundAvailability.objects.bulk_create(
                [RoundAvailability(content_type=contenttype, round=self.round, object_id=id) for id in ids - existing])
        self.log_action(type=self.action_log_type_updated)

        return self.get(request, *args, **kwargs)

    @extend_schema(summary="Mark objects as available")
    def put(self, request, *args, **kwargs):
        objs = sorted(self.get_field().to_internal_value(request.data), key=lambda o: type(o).__name__)
        for model, participants in groupby(objs, key=type):
            contenttype = ContentType.objects.get_for_model(model)
            RoundAvailability.objects.bulk_create(
                [RoundAvailability(content_type=contenttype, round=self.round, object_id=p.id) for p in participants])
        self.log_action(type=self.action_log_type_updated)
        return self.get(request, *args, **kwargs)

    @extend_schema(summary="Mark objects as unavailable")
    def post(self, request, *args, **kwargs):
        objs = sorted(self.get_field().to_internal_value(request.data), key=lambda o: type(o).__name__)
        for model, participants in groupby(objs, key=type):
            contenttype = ContentType.objects.get_for_model(model)
            RoundAvailability.objects.filter(
                content_type=contenttype, round=self.round,
                object_id__in=[p.id for p in participants],
            ).delete()
        self.log_action(type=self.action_log_type_updated)
        return self.get(request, *args, **kwargs)

    @extend_schema(summary="Delete class of availabilities", parameters=extra_params)
    def delete(self, request, *args, **kwargs):
        self.get_queryset().delete()
        self.log_action(type=self.action_log_type_updated)
        return Response(status=204)


@extend_schema(tags=['debates'], parameters=round_parameters)
@extend_schema_view(
    list=extend_schema(summary="List all preformed panels in the round"),
    create=extend_schema(summary="Create preformed panel"),
    retrieve=extend_schema(summary="Get preformed panel", parameters=debate_parameters),
    update=extend_schema(summary="Update preformed panel", parameters=debate_parameters),
    partial_update=extend_schema(summary="Patch preformed panel", parameters=debate_parameters),
    destroy=extend_schema(summary="Delete preformed panel", parameters=debate_parameters),
)
class PreformedPanelViewSet(RoundAPIMixin, AdministratorAPIMixin, ModelViewSet):

    serializer_class = serializers.PreformedPanelSerializer
    lookup_url_kwarg = 'debate_pk'
    action_log_type_created = ActionLogEntry.ActionType.PREFORMED_PANELS_CREATE
    action_log_type_updated = ActionLogEntry.ActionType.PREFORMED_PANELS_ADJUDICATOR_EDIT

    list_permission = Permission.VIEW_PREFORMEDPANELS
    create_permission = Permission.EDIT_PREFORMEDPANELS
    update_permission = Permission.EDIT_PREFORMEDPANELS
    destroy_permission = Permission.EDIT_PREFORMEDPANELS

    def get_queryset(self):
        return super().get_queryset().select_related('round', 'round__tournament').prefetch_related(
            'preformedpaneladjudicator_set__adjudicator__tournament',
        )

    @extend_schema(summary="Delete all preformed panels from round")
    def delete_all(self, request, *args, **kwargs):
        self.get_queryset().delete()
        self.log_action(ActionLogEntry.ActionType.PREFORMED_PANELS_DELETE)
        return Response(status=204)  # No content

    @extend_schema(summary="Add blank preformed panels")
    def add_blank(self, request, *args, **kwargs):
        """Adds new complete set of panels, with calculated bracket and liveness."""
        for i, (bracket_min, bracket_max, liveness) in enumerate(calculate_anticipated_draw(self.round), start=1):
            PreformedPanel.objects.update_or_create(round=self.round, room_rank=i, defaults={
                'bracket_max': bracket_max,
                'bracket_min': bracket_min,
                'liveness': liveness,
            })
        self.log_action(self.action_log_type_created)

        return self.get(request, *args, **kwargs)


@extend_schema(tags=['users'])
@extend_schema_view(
    list=extend_schema(summary="List all users"),
    create=extend_schema(summary="Create user"),
    retrieve=extend_schema(summary="Get user", parameters=[id_parameter]),
    update=extend_schema(summary="Update user", parameters=[id_parameter]),
    partial_update=extend_schema(summary="Patch user", parameters=[id_parameter]),
    destroy=extend_schema(summary="Deactivate user", parameters=[id_parameter]),
)
class UserViewSet(AdministratorAPIMixin, ModelViewSet):
    serializer_class = serializers.UserSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        qs = get_user_model().objects.prefetch_related('membership_set__group__tournament', 'userpermission_set__tournament')
        for user in qs:
            user.tournaments = get_permissions(user)
        return qs

    def get_object(self):
        obj = super().get_object()
        obj.tournaments = get_permissions(obj)
        return obj

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


@extend_schema(tags=['users'], parameters=[tournament_parameter])
@extend_schema_view(
    list=extend_schema(summary="List all permission groups in tournament"),
    create=extend_schema(summary="Create group"),
    retrieve=extend_schema(summary="Get group", parameters=[id_parameter]),
    update=extend_schema(summary="Update group", parameters=[id_parameter]),
    partial_update=extend_schema(summary="Patch group", parameters=[id_parameter]),
    destroy=extend_schema(summary="Delete group", parameters=[id_parameter]),
)
class GroupViewSet(TournamentAPIMixin, AdministratorAPIMixin, ModelViewSet):
    serializer_class = serializers.GroupSerializer


@extend_schema(tags=['scorecriteria'], parameters=[tournament_parameter])
@extend_schema_view(
    list=extend_schema(summary="List all score criteria in tournament"),
    create=extend_schema(summary="Create score criterion"),
    retrieve=extend_schema(summary="Get score criterion", parameters=[id_parameter]),
    update=extend_schema(summary="Update score criterion", parameters=[id_parameter]),
    partial_update=extend_schema(summary="Patch score criterion", parameters=[id_parameter]),
    destroy=extend_schema(summary="Delete score criterion", parameters=[id_parameter]),
)
class ScoreCriterionViewSet(TournamentAPIMixin, PublicAPIMixin, ModelViewSet):
    serializer_class = serializers.ScoreCriterionSerializer


class ParticipantIdentificationView(TournamentAPIMixin, ModelViewSet):
    serializer_class = serializers.ParticipantIdentificationSerializer
    authentication_classes = [URLKeyAuthentication]

    def get_object(self):
        return self.request.auth


class FullTournamentViewSet(TournamentAPIMixin, ModelViewSet):
    serializer_class = serializers.FullTournamentSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'tournament_slug'

    def get_queryset(self):
        return Tournament.objects.all().prefetch_related(
            'team_set__tournament',
            'team_set__speaker_set__categories__tournament',
            'team_set__breakcategory_set__tournament',
            'adjudicator_set__tournament',
            'round_set__roundmotion_set__motion',
            'round_set__debate_set__debateteam_set__team__tournament',
            'round_set__debate_set__debateadjudicator_set__adjudicator__tournament',
        )
