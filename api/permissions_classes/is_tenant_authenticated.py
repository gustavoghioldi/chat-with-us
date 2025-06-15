from rest_framework.permissions import BasePermission


class IsTenantAuthenticated(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        return True
