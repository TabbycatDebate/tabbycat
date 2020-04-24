from dynamic_preferences.registries import global_preferences_registry
from rest_framework.permissions import BasePermission, SAFE_METHODS


class APIEnabledPermission(BasePermission):
    message = "The API has been disabled on this site."

    def has_permission(self, request, view):
        return global_preferences_registry.manager()['global__enable_api']


class PublicPreferencePermission(BasePermission):

    def has_permission(self, request, view):
        return (request.user and request.user.is_staff) or (
            request.method in SAFE_METHODS and self.get_tournament_preference(view, view.access_operator))

    def get_tournament_preference(self, view, op):
        return op(view.tournament.pref(view.access_preference), view.access_setting)


class PublicIfReleasedPermission(PublicPreferencePermission):

    def has_object_permission(self, request, view, obj):
        return getattr(obj.round, view.round_released_field) == view.round_released_value


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or (request.user and request.user.is_staff)
