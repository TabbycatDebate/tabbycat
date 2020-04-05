from rest_framework.permissions import BasePermission, SAFE_METHODS


class PublicPreferencePermission(BasePermission):

    def has_permission(self, request, view):
        return (request.user and request.user.is_staff) or (
            request.method in SAFE_METHODS and self.get_tournament_preference(
                view.tournament, view.access_preference, view.access_setting))

    def get_tournament_preference(self, tournament, preference, setting):
        return tournament.pref(preference) == setting


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or (request.user and request.user.is_staff)
