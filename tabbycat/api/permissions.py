from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission, SAFE_METHODS

from participants.models import Person
from users.permissions import has_permission


class URLKeyAuthentication(TokenAuthentication):
    keyword = 'Key'
    model = Person

    def authenticate_credentials(self, key):
        model = self.get_model()
        if not key:
            raise AuthenticationFailed('No URL key provided.')

        try:
            person = model.objects.select_related('adjudicator__tournament', 'speaker__team__tournament').get(url_key=key)
        except model.DoesNotExist:
            raise AuthenticationFailed('Invalid URL key.')

        return (None, person)


class PublicPreferencePermission(BasePermission):

    def has_permission(self, request, view):
        return (request.user and request.user.is_staff) or (
            request.method in SAFE_METHODS and self.get_tournament_preference(view, view.access_operator))

    def get_tournament_preference(self, view, op):
        if type(view.access_preference) is tuple:
            return op(view.tournament.pref(pref) for pref in view.access_preference)
        return op(view.tournament.pref(view.access_preference), view.access_setting)


class PublicIfReleasedPermission(PublicPreferencePermission):

    def has_object_permission(self, request, view, obj):
        return getattr(obj.round, view.round_released_field) == view.round_released_value


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or (request.user and request.user.is_staff)


class PerTournamentPermissionRequired(BasePermission):
    def get_required_permission(self, view):
        """
        Given a model and an HTTP method, return the list of permission
        codes that the user is required to have.
        """
        return ({
            'list': getattr(view, 'list_permission', False),
            'create': getattr(view, 'create_permission', False),
            'retrieve': getattr(view, 'list_permission', False),
            'update': getattr(view, 'update_permission', False),
            'partial_update': getattr(view, 'update_permission', False),
            'destroy': getattr(view, 'destroy_permission', False),
            'delete_all': getattr(view, 'destroy_permission', False),
            'add_blank': getattr(view, 'create_permission', False),
            'GET': getattr(view, 'list_permission', False),
            'POST': getattr(view, 'update_permission', False),
            'PUT': getattr(view, 'update_permission', False),
            'PATCH': getattr(view, 'update_permission', False),
            'DELETE': getattr(view, 'destroy_permission', False),
        }).get(getattr(view, 'action', view.request.method), False)

    def has_permission(self, request, view):
        if not hasattr(view, 'tournament') or not request.user:
            return True
        perm = self.get_required_permission(view)
        return has_permission(request.user, perm, view.tournament)
